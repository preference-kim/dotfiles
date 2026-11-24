"""Synthetic SSH catalog regressions; no private inventory or live servers."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import socket
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
    def test_mobile_rule_uses_the_declared_gateway_only_when_direct_is_unreachable(self):
        inv = fixture()
        inv['nodes'][0]['ip'] = '127.0.0.1'
        ssh = inv['ssh']
        ssh['rules']['local']['fallback_jump'] = 'gateway'
        ssh['rules']['gateway'] = {'hosts': ['gateway'], 'option_sets': ['auth']}
        ssh['contexts']['internal']['rules'].append('gateway')
        inv['profiles']['device-a']['ssh']['context'] = 'internal'
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            ssh['option_sets']['direct'][1][1] = str(listener.getsockname()[1])
            config = renderer.render(inv, 'device-a')
            def effective_jump():
                result = subprocess.run(['ssh', '-G', '-F', '/dev/stdin', 'node-a'], input=config,
                                        text=True, capture_output=True, check=True)
                return [line for line in result.stdout.splitlines() if line.startswith('proxyjump ')]
            self.assertEqual(effective_jump(), ['proxyjump gateway'])
            listener.listen(1)
            self.assertIn(effective_jump(), ([], ['proxyjump none']))
        ssh['contexts']['internal']['rules'].remove('gateway')
        with self.assertRaises(ValueError):
            renderer.render(inv, 'device-a')

    def test_required_alias_must_be_rendered_and_cannot_be_excluded(self):
        inv = fixture()
        v = inv['profiles']['device-a']['ssh_verification'] = {'required_cluster_key_routes': ['node-a']}
        renderer.render(inv, 'device-a')
        for invalid in (['absent'], ['node-a', 'node-a'], 'node-a'):
            v['required_cluster_key_routes'] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                renderer.render(inv, 'device-a')
        v.update(required_cluster_key_routes=['node-a'],
                 excluded_routes={'node-a': {'reason': 'offline', 'resume_condition': 'online'}})
        with self.assertRaises(ValueError):
            renderer.render(inv, 'device-a')

    def test_approved_personal_migration_is_exact_scoped_and_idempotent(self):
        inv = fixture()
        p = inv['profiles']['device-a']
        old = 'Host node-a\n    User developer\n    ForwardAgent yes\n'
        p.update(ssh_verification={'required_cluster_key_routes': ['node-a']},
                 ssh_personal_migrations={'node-a': [old]})
        renderer.render(inv, 'device-a')
        rest = '# unrelated\n\nHost another\n    User other\n'
        for config in ['', rest, old + rest]:
            expected = config[len(old):] if config.startswith(old) else config
            self.assertEqual(renderer.migrate_personal_config(config, p), expected)
            self.assertEqual(renderer.migrate_personal_config(expected, p), expected)
        for different in (old.replace('yes', 'no'), old + '  Port 2200\n', old + old,
                          old.replace('Host node-a', 'Host node-a another')):
            with self.subTest(different=different), self.assertRaises(ValueError):
                renderer.migrate_personal_config(different, p)
        condition = 'Match originalhost node-a !exec "test -e /example"\n    ProxyJump gateway\n'
        p['ssh_personal_migrations']['node-a'].append(condition)
        self.assertEqual(renderer.migrate_personal_config(old + '\n' + condition + rest, p), '\n' + rest)
        with self.assertRaises(ValueError):
            renderer.migrate_personal_config(old + condition.replace('/example', '/other'), p)
        p['ssh_personal_migrations']['node-a'][0] += 'Host another\n'
        with self.assertRaises(ValueError):
            renderer.render(inv, 'device-a')

    def test_verification_metadata_preserves_routes(self):
        inv = fixture()
        before = renderer.render(inv, 'device-a')
        inv['profiles']['device-a']['ssh_verification'] = {
            'expected_hostnames': {'node-a': ['machine-a']},
            'excluded_routes': {'cluster-a': {
                'reason': 'User excluded this route',
                'resume_condition': 'User explicitly resumes checks'}}}
        self.assertEqual(before, renderer.render(inv, 'device-a'))
        self.assertEqual(before, renderer.render(inv, 'device-b'))

    def test_verification_rejects_missing_scope_and_ambiguous_rules(self):
        policies = [
            {'expected_hostnames': {'missing': ['machine-a']}},
            {'expected_hostnames': {'node-a': []}},
            {'expected_hostnames': {'node-a': ['*']}},
            {'expected_hostnames': {'node-a': ['machine-a', 'machine-a']}},
            {'excluded_routes': {'node-a': {'reason': 'Unreachable'}}},
            {'excluded_routes': {'node-a': {'reason': '', 'resume_condition': 'User request'}}},
            {'excluded_routes': {'node-*': {'reason': 'User request', 'resume_condition': 'User request'}}},
            {'unverified_is_success': True},
        ]
        for policy in policies:
            inv = fixture()
            inv['profiles']['device-a']['ssh_verification'] = policy
            with self.subTest(policy=policy), self.assertRaises(ValueError):
                renderer.render(inv, 'device-a')

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
