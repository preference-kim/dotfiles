"""Synthetic device separation and compatibility checks; no private fixtures."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('profile_check', Path(__file__).with_name('validate-private-profile.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ProfileTests(unittest.TestCase):
    def fixture(self, role='development-server'):
        before = '127.0.0.1 localhost\n192.0.2.1 node-a old-a\n'
        after = '127.0.0.1 localhost\n# protected\n192.0.2.1 node-a\n'
        if role == 'development-server':
            after += '# BEGIN Legacy aliases - will be deprecated\n192.0.2.1 old-a\n# END Legacy aliases - will be deprecated\n'
        profile = {'device_role': role, 'expected_hostname': 'machine-a', 'account': 'tester',
                   'hosts_scope': {'managed_node_names': ['node-a'], 'deprecated_alias_policy': 'separate-block' if role == 'development-server' else 'omit'},
                   'files': [{'path': '/etc/hosts', 'before': before, 'after': after}],
                   'authorized_alias_removals': ['old-a'], 'preserved_hosts_blocks': ['# protected\n192.0.2.1 node-a\n']}
        inventory = {'nodes': [{'name': 'node-a', 'ip': '192.0.2.1', 'aliases': [], 'deprecated_aliases': ['old-a']}], 'profiles': {'device-a': profile}}
        registration = {'device_role': role, 'account': 'tester', 'expected_hostname': 'machine-a', 'profile': 'device-a'}
        return inventory, registration

    def check(self, inv, reg):
        return module.validate(inv, reg, 'machine-a', 'tester')

    def test_server_keeps_compatibility_block(self):
        self.assertEqual(self.check(*self.fixture()), 'device-a')

    def test_personal_inventory_does_not_require_hf(self):
        self.assertEqual(self.check(*self.fixture('personal-device')), 'device-a')

    def test_local_hostname_loopback_is_preserved(self):
        inv, reg = self.fixture()
        import json
        inv = json.loads(json.dumps(inv).replace('node-a', 'machine-a'))
        item = inv['profiles']['device-a']['files'][0]
        for key in ['before', 'after']:
            item[key] = '127.0.1.1 machine-a\n' + item[key]
        self.assertEqual(self.check(inv, reg), 'device-a')
        item['after'] = item['after'].replace('127.0.1.1 machine-a\n', '')
        with self.assertRaises(ValueError): self.check(inv, reg)

    def test_physical_hostname_can_be_added_beside_existing_loopback(self):
        inv, reg = self.fixture()
        import json
        inv = json.loads(json.dumps(inv).replace('node-a', 'machine-a'))
        item = inv['profiles']['device-a']['files'][0]
        item['before'] = '127.0.0.1 localhost\n127.0.1.1 machine-a\n192.0.2.1 old-a\n'
        item['after'] = '127.0.1.1 machine-a\n' + item['after']
        self.assertEqual(self.check(inv, reg), 'device-a')

    def test_unselected_inventory_addition_rejected_but_baseline_preserved(self):
        inv, reg = self.fixture()
        inv['nodes'].append({'name': 'node-b', 'ip': '192.0.2.2', 'aliases': []})
        item = inv['profiles']['device-a']['files'][0]
        item['after'] += '192.0.2.2 node-b\n'
        with self.assertRaises(ValueError): self.check(inv, reg)
        item['before'] += '192.0.2.2 node-b\n'
        self.assertEqual(self.check(inv, reg), 'device-a')

    def test_case_variant_conflicts_rejected(self):
        inv, reg = self.fixture()
        inv['profiles']['device-a']['files'][0]['after'] += '192.0.2.2 NODE-A\n'
        with self.assertRaises(ValueError): self.check(inv, reg)
        inv, reg = self.fixture()
        inv['nodes'][0]['aliases'].append('NODE-A')
        with self.assertRaises(ValueError): self.check(inv, reg)

    def test_canonical_entry_inside_deprecation_block_rejected(self):
        inv, reg = self.fixture()
        item = inv['profiles']['device-a']['files'][0]
        canonical = '# protected\n192.0.2.1 node-a\n'
        item['after'] = item['after'].replace(canonical, '').replace(
            '# BEGIN Legacy aliases - will be deprecated\n',
            '# BEGIN Legacy aliases - will be deprecated\n' + canonical)
        with self.assertRaises(ValueError): self.check(inv, reg)

    def test_wrong_role_or_account_rejected(self):
        for field, value in [('device_role', 'personal-device'), ('account', 'someone-else'), ('expected_hostname', 'other-device')]:
            inv, reg = self.fixture(); inv['profiles']['device-a'][field] = value
            with self.assertRaises(ValueError): self.check(inv, reg)

    def test_missing_role_rejected(self):
        inv, reg = self.fixture(); del reg['device_role']
        with self.assertRaises(ValueError): self.check(inv, reg)

    def test_shared_home_mapping_checked_against_physical_host(self):
        inv, reg = self.fixture(); inv['profiles']['device-b'] = copy.deepcopy(inv['profiles']['device-a'])
        inv['profiles']['device-b']['expected_hostname'] = 'machine-b'
        reg['host_profiles'] = {'machine-a': 'device-b'}
        with self.assertRaises(ValueError): self.check(inv, reg)

    def test_unknown_shared_home_host_rejected(self):
        inv, reg = self.fixture(); reg['expected_hostname'] = 'machine-b'; reg['host_profiles'] = {'machine-b': 'device-a'}
        with self.assertRaises(ValueError): self.check(inv, reg)

    def test_server_alias_loss_and_protected_block_change_rejected(self):
        for old, new in [('192.0.2.1 old-a', ''), ('# protected', '# changed')]:
            inv, reg = self.fixture(); item = inv['profiles']['device-a']['files'][0]; item['after'] = item['after'].replace(old, new)
            with self.assertRaises(ValueError): self.check(inv, reg)

    def test_unauthorized_personal_removal_rejected(self):
        inv, reg = self.fixture('personal-device'); inv['profiles']['device-a']['authorized_alias_removals'] = []
        with self.assertRaises(ValueError): self.check(inv, reg)

    def test_out_of_scope_and_duplicate_names_rejected(self):
        inv, reg = self.fixture(); inv['profiles']['device-a']['hosts_scope']['managed_node_names'] = ['missing']
        with self.assertRaises(ValueError): self.check(inv, reg)
        inv, reg = self.fixture(); inv['nodes'][0]['aliases'] = ['old-a']
        with self.assertRaises(ValueError): self.check(inv, reg)


    def test_operational_blocks_cover_scope_and_preserve_external_block(self):
        inv, reg = self.fixture()
        inv['nodes'].append({'name': 'node-b', 'ip': '192.0.2.2', 'aliases': []})
        profile = inv['profiles']['device-a']
        profile['hosts_scope']['managed_node_names'].append('node-b')
        profile['hosts_scope']['blocks'] = [
            {'title': 'Example cluster', 'node_names': ['node-a', 'node-b']}]
        profile['files'][0]['after'] += '# BEGIN Example cluster\n192.0.2.2 node-b\n# END Example cluster\n'
        self.assertEqual(self.check(inv, reg), 'device-a')
        for bad in [[], [{'title': 'Example cluster', 'node_names': ['node-b']}],
                    [{'title': 'Wrong cluster', 'node_names': ['node-a', 'node-b']}]]:
            candidate = copy.deepcopy(inv)
            candidate['profiles']['device-a']['hosts_scope']['blocks'] = bad
            with self.assertRaises(ValueError): self.check(candidate, reg)

    def test_empty_generated_block_is_omitted_for_preserved_names(self):
        inv, reg = self.fixture()
        profile = inv['profiles']['device-a']
        profile['hosts_scope']['blocks'] = [{'title': 'Example cluster', 'node_names': ['node-a']}]
        self.assertEqual(self.check(inv, reg), 'device-a')
        profile['files'][0]['after'] += '# BEGIN Example cluster\n# END Example cluster\n'
        with self.assertRaises(ValueError): self.check(inv, reg)

    def test_block_and_node_order_are_enforced(self):
        inv, reg = self.fixture()
        inv['nodes'] += [{'name': 'node-b', 'ip': '192.0.2.2', 'aliases': []},
                         {'name': 'node-c', 'ip': '192.0.2.3', 'aliases': []}]
        profile = inv['profiles']['device-a']
        profile['preserved_hosts_blocks'] = []
        profile['hosts_scope']['managed_node_names'] = ['node-a', 'node-b', 'node-c']
        profile['hosts_scope']['blocks'] = [
            {'title': 'Example first', 'node_names': ['node-a', 'node-b']},
            {'title': 'Example second', 'node_names': ['node-c']}]
        first = '# BEGIN Example first\n192.0.2.1 node-a\n192.0.2.2 node-b\n# END Example first\n'
        second = '# BEGIN Example second\n192.0.2.3 node-c\n# END Example second\n'
        item = profile['files'][0]
        prefix = item['after'].replace('# protected\n192.0.2.1 node-a\n', '')
        item['after'] = prefix + first + second
        self.assertEqual(self.check(inv, reg), 'device-a')
        for bad in [second + first, first.replace('192.0.2.1 node-a\n192.0.2.2 node-b', '192.0.2.2 node-b\n192.0.2.1 node-a') + second]:
            item['after'] = prefix + bad
            with self.assertRaises(ValueError): self.check(inv, reg)

    def delegated_fixture(self):
        inv, reg = self.fixture()
        owner = inv['profiles'].pop('device-a')
        owner['expected_hostname'] = 'machine-b'
        inv['profiles']['device-b'] = owner
        inv['profiles']['device-a'] = {
            'device_role': 'development-server', 'account': 'tester',
            'expected_hostname': 'machine-a', 'configuration_owner': 'device-b',
            'files': [], 'ssh_equivalence': []}
        reg['host_profiles'] = {'machine-a': 'device-a', 'machine-b': 'device-b'}
        return inv, reg

    def test_delegated_profile_preserves_enrollment_without_file_plans(self):
        inv, reg = self.delegated_fixture()
        before = copy.deepcopy(reg)
        self.assertEqual(self.check(inv, reg), 'device-a')
        self.assertEqual(reg, before)
        self.assertEqual(module.validate(inv, reg, 'machine-b', 'tester'), 'device-b')

    def test_delegated_profile_rejects_local_file_or_scope_plans(self):
        for key, value in [('files', [{'path': '/etc/hosts'}]),
                           ('ssh_equivalence', [['old', 'new']]),
                           ('hosts_scope', {}), ('preserved_hosts_blocks', []),
                           ('authorized_alias_removals', [])]:
            inv, reg = self.delegated_fixture()
            inv['profiles']['device-a'][key] = value
            with self.assertRaises(ValueError): self.check(inv, reg)

    def test_delegation_rejects_missing_self_or_chained_owner(self):
        for value in ['missing', 'device-a', '', None, 42]:
            inv, reg = self.delegated_fixture()
            inv['profiles']['device-a']['configuration_owner'] = value
            with self.assertRaises(ValueError): self.check(inv, reg)
        inv, reg = self.delegated_fixture()
        inv['profiles']['device-b']['configuration_owner'] = 'device-a'
        with self.assertRaises(ValueError): self.check(inv, reg)

    def test_delegation_preserves_binding_and_owner_identity_checks(self):
        for profile_id, key, value in [
                ('device-a', 'expected_hostname', 'machine-b'),
                ('device-b', 'account', 'someone-else'),
                ('device-b', 'device_role', 'personal-device'),
                ('device-b', 'files', [])]:
            inv, reg = self.delegated_fixture()
            inv['profiles'][profile_id][key] = value
            with self.assertRaises(ValueError): self.check(inv, reg)


if __name__ == '__main__':
    unittest.main()
