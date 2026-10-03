"""Synthetic SSH catalog regressions; no private inventory or live servers."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import unittest

spec = importlib.util.spec_from_file_location('renderer', Path(__file__).with_name('render-private-ssh.py'))
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


def fixture():
    return {
        'schema_version': 2,
        'nodes': [{'name': 'node-a', 'ip': '192.0.2.10', 'aliases': ['cluster-a'],
                   'ssh': {'reverse_port': '22201'}}],
        'ssh': {
            'bindings': {},
            'option_sets': {
                'direct': [['HostName', '${ip}'], ['Port', '22']],
                'reverse': [['HostName', '127.0.0.1'], ['Port', '${reverse_port}'],
                            ['ProxyJump', 'gateway'], ['HostKeyAlias', '${name}']],
                'auth': [['User', '${account}'], ['IdentityFile', '${identity_file}'],
                         ['IdentitiesOnly', 'yes'], ['StrictHostKeyChecking', 'yes']],
            },
            'rules': {
                'local': {'nodes': ['node-a'], 'aliases': 'canonical', 'option_sets': ['direct', 'auth']},
                'external': {'nodes': ['node-a'], 'aliases': 'canonical', 'option_sets': ['reverse', 'auth']},
            },
            'contexts': {
                'internal': {'rules': ['local'], 'bindings': {'identity_file': '~/.ssh/team'}},
                'external': {'rules': ['external'], 'bindings': {'identity_file': '~/.ssh/team'}},
            },
        },
        'profiles': {
            'device-a': {'account': 'developer', 'files': [], 'ssh': {'context': 'external', 'bindings': {}}},
            'device-b': {'account': 'developer', 'files': [], 'ssh': {'context': 'external', 'bindings': {}}},
        },
    }


class CatalogTests(unittest.TestCase):
    def test_shared_route_update_reaches_every_consumer(self):
        inv = fixture()
        before = renderer.render(inv, 'device-a')
        inv['nodes'][0]['ssh']['reverse_port'] = '22209'
        after = renderer.render(inv, 'device-a')
        self.assertNotEqual(before, after)
        self.assertIn('Port 22209', after)
        self.assertEqual(after, renderer.render(inv, 'device-b'))
        self.assertEqual(after, renderer.render(copy.deepcopy(inv), 'device-a'))

    def test_network_selection_does_not_copy_node_addresses(self):
        inv = fixture()
        inv['profiles']['device-b']['ssh']['context'] = 'internal'
        self.assertIn('HostName 192.0.2.10', renderer.render(inv, 'device-b'))
        self.assertIn('HostName 127.0.0.1', renderer.render(inv, 'device-a'))
        inv['nodes'][0]['ip'] = '192.0.2.11'
        self.assertIn('HostName 192.0.2.11', renderer.render(inv, 'device-b'))

    def test_profiles_cannot_override_topology(self):
        inv = fixture()
        inv['profiles']['device-a']['ssh']['bindings']['reverse_port'] = '1'
        with self.assertRaisesRegex(ValueError, 'only select local'):
            renderer.render(inv, 'device-a')

    def test_physical_hostname_case_and_alias_exclusions(self):
        inv = fixture()
        inv['nodes'][0]['machine_name'] = 'RACK-A'
        inv['nodes'][0]['deprecated_aliases'] = ['legacy-a']
        inv['ssh']['rules']['external'].update(aliases='all', exclude_aliases=['legacy-*'])
        actual = renderer.render(inv, 'device-a')
        self.assertIn('Host node-a cluster-a 192.0.2.10 RACK-A rack-a', actual)
        self.assertNotIn('legacy-a', actual)

    def test_invalid_input_fails_closed(self):
        mutations = [
            lambda v: v['profiles']['device-a']['files'].append({'path': '~/.ssh/config'}),
            lambda v: v['ssh']['contexts']['external']['rules'].append('missing'),
            lambda v: v['nodes'][0]['ssh'].pop('reverse_port'),
            lambda v: v['ssh']['option_sets']['auth'].append(['Include', '~/.ssh/anything']),
            lambda v: v['ssh']['option_sets']['auth'].append(['User', 'bad\nHost *']),
            lambda v: v['ssh']['option_sets']['auth'].append(['User', 'someone-else']),
            lambda v: v['profiles']['device-a'].update(configuration_owner='device-b'),
            lambda v: v['ssh']['rules'].update({'bad\nHost *': v['ssh']['rules']['local']}),
            lambda v: v['ssh']['rules']['external'].update(hosts=['*']),
            lambda v: v['profiles']['device-a']['ssh']['bindings'].update(identity_file='${unknown}'),
        ]
        for mutate in mutations:
            inv = fixture()
            mutate(inv)
            with self.subTest(mutation=mutate), self.assertRaises(ValueError):
                renderer.render(inv, 'device-a')

    def test_duplicate_json_identifiers_are_rejected(self):
        with self.assertRaises(ValueError):
            json.loads('{"name": 1, "name": 2}', object_pairs_hook=renderer.unique_object)

    def test_helper_alias_cannot_expand_to_a_wildcard(self):
        inv = fixture()
        inv['ssh']['rules']['external'] = {'hosts': ['*'], 'option_sets': ['auth']}
        with self.assertRaisesRegex(ValueError, 'literal host names'):
            renderer.render(inv, 'device-a')

    @unittest.skipUnless(shutil.which('ssh'), 'OpenSSH is required')
    def test_openssh_scope_identity_order_and_aliases(self):
        inv = fixture()
        inv['ssh']['option_sets']['auth'] += [['IdentityFile', '~/.ssh/second'],
                                             ['CertificateFile', '~/.ssh/certificate']]
        rendered = renderer.render(inv, 'device-a')
        config = rendered + '\nHost unrelated\n    User personal\n    Port 2200\n'
        def effective(host):
            result = subprocess.run(['ssh', '-G', '-F', '/dev/stdin', host], input=config,
                                    capture_output=True, text=True, check=True)
            return result.stdout.splitlines()
        actual = effective('cluster-a')
        self.assertIn('hostname 127.0.0.1', actual)
        self.assertIn('port 22201', actual)
        self.assertIn('hostkeyalias node-a', actual)
        self.assertEqual([s for s in actual if s.startswith('identityfile ')],
                         ['identityfile ~/.ssh/team', 'identityfile ~/.ssh/second'])
        self.assertIn('user personal', effective('unrelated'))
        self.assertIn('port 2200', effective('unrelated'))
        self.assertNotIn('proxyjump gateway', effective('unrelated'))

    @unittest.skipUnless(shutil.which('ssh'), 'OpenSSH is required')
    def test_identity_path_with_spaces_and_comment_character(self):
        inv = fixture()
        inv['profiles']['device-a']['ssh']['bindings']['identity_file'] = '~/.ssh/a key #1'
        result = subprocess.run(['ssh', '-G', '-F', '/dev/stdin', 'node-a'],
                                input=renderer.render(inv, 'device-a'), capture_output=True,
                                text=True, check=True)
        self.assertIn('identityfile ~/.ssh/a key #1\n', result.stdout)


if __name__ == '__main__':
    unittest.main()
