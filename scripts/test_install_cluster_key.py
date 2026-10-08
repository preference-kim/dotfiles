"""Synthetic keys only; supply an explicit private test work directory."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
import uuid

script = Path(__file__).with_name('install-cluster-key')
work = Path(sys.argv.pop(1)).resolve()
work.mkdir(parents=True, exist_ok=True)


def keypair(directory, name):
    path = directory / name
    subprocess.run(['ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-f', str(path)], check=True)
    return path.read_bytes()


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.root = work / uuid.uuid4().hex
        self.root.mkdir(mode=0o700)
        self.home = self.root / 'home'
        self.home.mkdir(mode=0o700)
        self.key = keypair(self.root, 'synthetic')

    def tearDown(self):
        assert self.root.parent == work and not self.root.is_symlink()
        shutil.rmtree(self.root)

    def run_installer(self, data, *args):
        env = dict(os.environ, HOME=str(self.home))
        result = subprocess.run([sys.executable, str(script), *args], input=data, env=env, capture_output=True)
        return result.returncode, json.loads(result.stdout)

    def test_installs_then_reports_unchanged(self):
        code, out = self.run_installer(self.key)
        self.assertEqual((code, out['status']), (0, 'installed'))
        ssh = self.home / '.ssh'
        self.assertEqual(ssh.stat().st_mode & 0o777, 0o700)
        self.assertEqual((ssh / 'moreh_cluster_sunho').stat().st_mode & 0o777, 0o600)
        self.assertEqual((ssh / 'moreh_cluster_sunho.pub').stat().st_mode & 0o777, 0o644)
        self.assertEqual((ssh / 'moreh_cluster_sunho.pub').read_bytes().split()[:2],
                         (self.root / 'synthetic.pub').read_bytes().split()[:2])
        self.assertEqual(self.run_installer(self.key)[1]['status'], 'unchanged')

    def test_different_existing_key_is_kept_as_override(self):
        ssh = self.home / '.ssh'
        ssh.mkdir(mode=0o700)
        other = keypair(self.root, 'other')
        (ssh / 'moreh_cluster_sunho').write_bytes(other)
        code, out = self.run_installer(self.key)
        self.assertEqual((code, out['status']), (0, 'override'))
        self.assertEqual((ssh / 'moreh_cluster_sunho').read_bytes(), other)

    def test_authorized_rotation_replaces_previous_key(self):
        ssh = self.home / '.ssh'
        ssh.mkdir(mode=0o700)
        old = keypair(self.root, 'old')
        (ssh / 'moreh_cluster_sunho').write_bytes(old)
        (ssh / 'moreh_cluster_sunho').chmod(0o600)
        old_fp = subprocess.run(['ssh-keygen', '-l', '-f', str(self.root / 'old')], capture_output=True,
                                text=True, check=True).stdout.split()[1]
        code, out = self.run_installer(self.key, '--replace', old_fp)
        self.assertEqual((code, out['status']), (0, 'installed'))
        self.assertEqual((ssh / 'moreh_cluster_sunho').read_bytes(), self.key)

    def test_rejects_non_key_input(self):
        self.assertEqual(self.run_installer(b'not a key\n')[0], 1)
        self.assertFalse((self.home / '.ssh' / 'moreh_cluster_sunho').exists())


unittest.main()
