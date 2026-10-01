"""Synthetic tests; artifacts live only under the explicitly supplied work path."""
import importlib.util
import os
from pathlib import Path
import shutil
import sys
import types
import unittest
from unittest.mock import patch
import uuid

spec = importlib.util.spec_from_file_location('installer', Path(__file__).with_name('install-hf-from-stdin.py'))
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
work = Path(sys.argv.pop(1)).resolve()
work.mkdir(parents=True, exist_ok=True)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.root = work / uuid.uuid4().hex
        self.root.mkdir(mode=0o700)
        self.token = self.root / 'token'
        self.stored = self.root / 'stored_tokens'
        self.original_mask = os.umask(0o077)
        self.hub = types.ModuleType('huggingface_hub')
        self.hub.constants = types.SimpleNamespace(HF_TOKEN_PATH=str(self.token), HF_STORED_TOKENS_PATH=str(self.stored))
        self.logins = 0
        def login(token, add_to_git_credential):
            self.assertFalse(add_to_git_credential)
            self.logins += 1
            self.token.write_text(token)
            self.stored.write_text('synthetic named token')
        self.hub.login = login
        self.modules = patch.dict(sys.modules, {'huggingface_hub': self.hub})
        self.modules.start()
        self.env = patch.dict(os.environ, {'HF_TOKEN': '', 'HUGGING_FACE_HUB_TOKEN': ''})
        self.env.start()
        self.process = patch.object(installer.subprocess, 'run', return_value=types.SimpleNamespace(returncode=0))
        self.process.start()

    def tearDown(self):
        self.process.stop()
        self.env.stop()
        self.modules.stop()
        os.umask(self.original_mask)
        assert self.root.parent == work and not self.root.is_symlink() and not (self.root / '.git').exists()
        shutil.rmtree(self.root)

    def test_install_and_idempotent_verification(self):
        result = installer.install('hf_SYNTHETIC', '/synthetic/hf')
        self.assertTrue(result['token_changed'])
        self.assertEqual(self.token.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.stored.stat().st_mode & 0o777, 0o600)
        result = installer.install('hf_SYNTHETIC', '/synthetic/hf')
        self.assertFalse(result['token_changed'])
        self.assertEqual(self.logins, 1)

    def test_backup_before_replace(self):
        self.token.write_text('old credential')
        result = installer.install('hf_SYNTHETIC', '/synthetic/hf')
        self.assertTrue(result['backup_created'])
        files = list((self.root / '.agent-update-backups').glob('*/0'))
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].read_text(), 'old credential')
        self.assertEqual(files[0].stat().st_mode & 0o777, 0o600)

    def test_failed_authentication_rolls_back(self):
        self.token.write_text('old credential')
        installer.subprocess.run.return_value.returncode = 1
        with self.assertRaises(RuntimeError):
            installer.install('hf_SYNTHETIC', '/synthetic/hf')
        self.assertEqual(self.token.read_text(), 'old credential')
        self.assertFalse(self.stored.exists())

    def test_symlink_refused(self):
        unrelated = self.root / 'unrelated'
        unrelated.write_text('keep')
        self.token.symlink_to(unrelated)
        with self.assertRaises(RuntimeError):
            installer.install('hf_SYNTHETIC', '/synthetic/hf')
        self.assertEqual(unrelated.read_text(), 'keep')

    def test_lock_prevents_second_writer(self):
        (self.root / '.agent-update-credential-lock').mkdir()
        with self.assertRaises(FileExistsError):
            installer.install('hf_SYNTHETIC', '/synthetic/hf')
        self.assertEqual(self.logins, 0)

    def test_split_token_paths_still_lock_shared_stored_tokens(self):
        alternate = self.root / 'alternate'
        alternate.mkdir()
        self.hub.constants.HF_TOKEN_PATH = str(alternate / 'token')
        (self.root / '.agent-update-credential-lock').mkdir()
        with self.assertRaises(FileExistsError):
            installer.install('hf_SYNTHETIC', '/synthetic/hf')
        self.assertEqual(self.logins, 0)
        self.assertFalse((alternate / '.agent-update-credential-lock').exists())

    def test_pip_console_script_runtime_without_sibling_python(self):
        cli = self.root / 'hf'
        cli.write_text('#!' + sys.executable + '\n')
        self.assertEqual(installer.hf_python(cli), sys.executable)

    def test_explicit_shebang_wins_over_unrelated_sibling_python(self):
        sibling = self.root / 'python'
        sibling.write_text('#!/bin/sh\n')
        sibling.chmod(0o700)
        cli = self.root / 'hf'
        cli.write_text('#!' + sys.executable + '\n')
        self.assertEqual(installer.hf_python(cli), sys.executable)

    def test_non_python_console_script_refused(self):
        cli = self.root / 'hf'
        cli.write_text('#!/bin/sh\n')
        with self.assertRaises(RuntimeError):
            installer.hf_python(cli)

    def test_environment_override_refused(self):
        os.environ['HF_TOKEN'] = 'hf_OTHER'
        with self.assertRaises(RuntimeError):
            installer.install('hf_SYNTHETIC', '/synthetic/hf')
        self.assertFalse(self.token.exists())

    def test_concurrent_change_during_auth_not_overwritten(self):
        self.token.write_text('old credential')
        def concurrent(*args, **kwargs):
            self.token.write_text('concurrent credential')
            return types.SimpleNamespace(returncode=0)
        installer.subprocess.run.side_effect = concurrent
        with self.assertRaises(RuntimeError):
            installer.install('hf_SYNTHETIC', '/synthetic/hf')
        self.assertEqual(self.token.read_text(), 'concurrent credential')


unittest.main()
