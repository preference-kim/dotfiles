"""Filesystem/Git integration checks with synthetic settings and explicit work root."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch
import uuid
from deployment_config import load_config, protected_json, checked_ssh_dir
from test_deployment_config import CONFIG, write_snapshot

work = Path(sys.argv.pop(1)).resolve()
work.mkdir(mode=0o700, parents=True, exist_ok=True)


class LoadingTests(unittest.TestCase):
    def setUp(self):
        self.root = work / uuid.uuid4().hex; self.root.mkdir(mode=0o700)
        self.home = self.root / 'home'; self.home.mkdir(mode=0o700)
        self.repo = self.root / 'source'; self.repo.mkdir(mode=0o700)
        self.remote = self.root / 'origin.git'
        def run(*args): subprocess.run(args, check=True, capture_output=True)
        run('git', 'init', '-q', '-b', 'main', str(self.repo))
        run('git', '-C', str(self.repo), 'config', 'user.name', 'Example')
        run('git', '-C', str(self.repo), 'config', 'user.email', 'example@example.invalid')
        write_snapshot(self.repo)
        run('git', '-C', str(self.repo), 'add', 'deployment.json')
        run('git', '-C', str(self.repo), 'commit', '-qm', 'Synthetic settings')
        run('git', 'clone', '-q', '--bare', str(self.repo), str(self.remote))
        run('git', '-C', str(self.repo), 'remote', 'add', 'origin', str(self.remote))
        self.reg = self.home / '.config/agent-update/private-sync.json'
        self.reg.parent.mkdir(mode=0o700, parents=True)
        self.reg.write_text(json.dumps({'checkout': str(self.repo), 'repository_url': str(self.remote)}))
        self.reg.chmod(0o600)
        self.home_patch = patch.dict(os.environ, HOME=str(self.home)); self.home_patch.start()

    def tearDown(self):
        self.home_patch.stop()
        assert self.root.parent == work and not self.root.is_symlink()
        shutil.rmtree(self.root)

    def test_fetches_published_settings_without_changing_worktree(self):
        self.assertEqual(load_config(), CONFIG)
        self.assertEqual(subprocess.check_output(['git','-C',str(self.repo),'status','--porcelain']), b'')
        self.assertEqual(load_config(), CONFIG)

    def test_dirty_checkout_and_origin_mismatch_are_rejected(self):
        (self.repo / 'local').write_text('preserve me')
        with self.assertRaises(ValueError): load_config()
        (self.repo / 'local').unlink()
        self.reg.write_text(json.dumps({'checkout': str(self.repo), 'repository_url': 'different'}))
        with self.assertRaises(ValueError): load_config()

    def test_failed_fetch_does_not_use_cached_settings(self):
        self.assertEqual(load_config(), CONFIG)
        shutil.rmtree(self.remote)
        with self.assertRaises(subprocess.CalledProcessError): load_config()

    def test_snapshot_rejects_public_mode_symlink_hardlink_and_duplicate_keys(self):
        config = write_snapshot(self.root)
        config.chmod(0o644)
        with self.assertRaises(ValueError): load_config(config)
        config.chmod(0o600)
        link = self.root / 'link'; link.symlink_to(config)
        with self.assertRaises((ValueError, OSError)): load_config(link)
        hard = self.root / 'hard'; os.link(config, hard)
        with self.assertRaises(ValueError): load_config(config)
        hard.unlink(); config.write_text('{"schema_version":1,"schema_version":2}')
        with self.assertRaises(ValueError): load_config(config)

    def test_ssh_directory_symlink_is_rejected(self):
        (self.home / '.ssh').symlink_to(self.root)
        with self.assertRaises(ValueError): checked_ssh_dir()


unittest.main()
