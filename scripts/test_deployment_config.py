"""Synthetic deployment settings; never load live configuration in tests."""
import copy
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from deployment_config import validate, allowed_paths, load_config, checked_ssh_dir

CONFIG = {'schema_version': 1,
          'bootstrap': {'dotfiles_url': 'https://github.com/example/dotfiles.git',
                        'private_url': 'ssh://git@github.com/example/private.git',
                        'github_account': 'example-user'},
          'paths': {'ssh_include': '~/.ssh/example_cluster.conf',
                    'cluster_key': '~/.ssh/example_cluster_key',
                    'cloud_hosts': '/etc/cloud/cloud.cfg.d/99-example-preserve-hosts.cfg'}}


def write_snapshot(root):
    path = root / 'deployment.json'
    path.write_text(json.dumps(CONFIG))
    path.chmod(0o600)
    return path


class DeploymentTests(unittest.TestCase):
    def test_exact_destinations_and_modes(self):
        allowed = allowed_paths(CONFIG)
        self.assertEqual(len(allowed), 6)
        self.assertEqual(allowed[CONFIG['paths']['cluster_key']], 0o600)
        self.assertEqual(allowed[CONFIG['paths']['cluster_key'] + '.pub'], 0o644)
        self.assertNotIn('~/.ssh/another.conf', allowed)
        self.assertNotIn('/etc/sudoers', allowed)

    def test_rejects_escape_reserved_files_and_shell_values(self):
        for field, values in {
            'cluster_key': ['~/.ssh/../key', '~/.ssh/id_ed25519', '~/.ssh/authorized_keys',
                            '~/.ssh/config', '~/.ssh/known_hosts', '/tmp/key', '~//ssh/key'],
            'ssh_include': ['~/.ssh/config', '~/.ssh/../a.conf', '~/.ssh/a.conf\nHost *'],
            'cloud_hosts': ['/etc/sudoers', '/etc/cloud/cloud.cfg.d/../a', '/etc/cloud/cloud.cfg.d/10-network.cfg'],
        }.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    config = copy.deepcopy(CONFIG); config['paths'][field] = value
                    with self.assertRaises(ValueError): validate(config)
        for value in ['-ufoo', 'https://github.com/example/r;touch x', 'ssh://user:pass@host/repo', '$(id)', 'https://github.com/example/private.git', 'git@github.com:example/private.git']:
            config = copy.deepcopy(CONFIG); config['bootstrap']['private_url'] = value
            with self.assertRaises(ValueError): validate(config)

    def test_reserved_key_names_reject_case_aliases(self):
        for name in ['Config', 'CONFIG', 'Known_Hosts', 'AUTHORIZED_KEYS',
                     'Id_Ed25519', 'ID_RSA', 'IDENTITY']:
            with self.subTest(name=name):
                config = copy.deepcopy(CONFIG)
                config['paths']['cluster_key'] = '~/.ssh/' + name
                with self.assertRaises(ValueError):
                    validate(config)

    def test_missing_unknown_fields_do_not_fall_back(self):
        for section in ['bootstrap', 'paths']:
            config = copy.deepcopy(CONFIG); config[section]['unknown'] = 'x'
            with self.assertRaises(ValueError): validate(config)
        config = copy.deepcopy(CONFIG); del config['paths']['ssh_include']
        with self.assertRaises(ValueError): validate(config)

    def test_unavailable_snapshot_does_not_read_registration(self):
        with patch('deployment_config.protected_json', side_effect=FileNotFoundError), \
             patch('deployment_config.subprocess.run') as run:
            with self.assertRaises(FileNotFoundError): load_config('/unavailable')
            run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
