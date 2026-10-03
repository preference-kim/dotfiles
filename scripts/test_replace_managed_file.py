"""Synthetic files only; supply an explicit private test work directory."""
import importlib.util
import contextlib
import io
import os
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch
import uuid

spec = importlib.util.spec_from_file_location('writer', Path(__file__).with_name('replace-managed-file.py'))
writer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(writer)
work = Path(sys.argv.pop(1)).resolve()
work.mkdir(parents=True, exist_ok=True)


class ReplaceTests(unittest.TestCase):
    def setUp(self):
        self.root = work / uuid.uuid4().hex
        self.root.mkdir(mode=0o700)
        self.path = self.root / 'hosts'
        self.path.write_bytes(b'127.0.0.1 localhost\n')
        self.old = self.path.read_bytes()
        self.new = self.old + b'192.0.2.10 node-example\n'
        self.mask = os.umask(0o077)

    def tearDown(self):
        os.umask(self.mask)
        assert self.root.parent == work and not self.root.is_symlink() and not (self.root / '.git').exists()
        shutil.rmtree(self.root)

    def test_restrictive_umask_keeps_hosts_readable_and_second_run_unchanged(self):
        self.assertEqual(writer.replace(self.path, self.old, self.new, 0o644), 'changed')
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o644)
        self.assertEqual(writer.replace(self.path, self.new, self.new, 0o644), 'unchanged')

    def test_conflicting_local_edit_preserved(self):
        self.path.write_bytes(b'local edit')
        with self.assertRaises(ValueError):
            writer.replace(self.path, self.old, self.new, 0o644)
        self.assertEqual(self.path.read_bytes(), b'local edit')

    def test_symlink_preserved(self):
        link = self.root / 'link'
        link.symlink_to(self.path)
        with self.assertRaises(ValueError):
            writer.replace(link, self.old, self.new, 0o644)
        self.assertEqual(self.path.read_bytes(), self.old)

    def test_concurrent_edit_during_staging_preserved(self):
        original = writer.os.fsync
        def concurrent(fd):
            original(fd)
            self.path.write_bytes(b'concurrent edit')
        with patch.object(writer.os, 'fsync', side_effect=concurrent):
            with self.assertRaises(ValueError):
                writer.replace(self.path, self.old, self.new, 0o644)
        self.assertEqual(self.path.read_bytes(), b'concurrent edit')
        self.assertEqual(list(self.root.iterdir()), [self.path])

    def test_approved_creation_and_restrictive_umask(self):
        target = self.root / 'preserve.cfg'
        self.assertEqual(writer.replace(target, None, b'manage_etc_hosts: false\n', 0o644,
                                        allow_create=True), 'changed')
        self.assertEqual(target.stat().st_mode & 0o777, 0o644)
        self.assertEqual(target.stat().st_nlink, 1)
        with self.assertRaises(ValueError):
            writer.replace(target, None, b'changed', 0o644, allow_create=True)

    def test_creation_needs_explicit_authorization(self):
        with self.assertRaises(FileNotFoundError):
            writer.replace(self.root / 'missing', None, b'content', 0o644)

    def test_cli_creates_generated_include_but_not_personal_entry_point(self):
        target = self.root / 'moreh_cluster.conf'
        data = {'path': '~/.ssh/moreh_cluster.conf', 'before': None,
                'after': 'Host example\n    HostName 192.0.2.10\n', 'mode': '0600'}
        with patch.object(writer.json, 'load', return_value=data), \
             patch.object(writer.Path, 'expanduser', return_value=target), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(writer.main(), 0)
        self.assertEqual(target.stat().st_mode & 0o777, 0o600)
        self.assertEqual(target.read_text(), data['after'])
        data['path'] = '~/.ssh/config'
        with patch.object(writer.json, 'load', return_value=data), \
             patch.object(writer.Path, 'expanduser', return_value=self.root / 'config'), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(writer.main(), 1)
        self.assertFalse((self.root / 'config').exists())

    def test_concurrent_creation_cannot_be_overwritten(self):
        target = self.root / 'new.cfg'
        original = writer.os.link
        def concurrent(src, dst):
            target.write_bytes(b'other owner')
            return original(src, dst)
        with patch.object(writer.os, 'link', side_effect=concurrent):
            with self.assertRaises(FileExistsError):
                writer.replace(target, None, b'ours', 0o644, allow_create=True)
        self.assertEqual(target.read_bytes(), b'other owner')
        self.assertFalse(list(self.root.glob('.agent-update-*')))

    def test_cloud_config_rejects_non_root_owner_and_unrelated_settings(self):
        with patch.object(writer.os, 'geteuid', return_value=0), patch.object(writer.os, 'getegid', return_value=0):
            with patch.object(writer, 'snapshot', return_value=(b'old', (501, 20, 0o644))):
                with self.assertRaises(ValueError):
                    writer.validate_cloud_config(self.path, 'manage_etc_hosts: false\n')
            with self.assertRaises(ValueError):
                writer.validate_cloud_config(self.path, 'manage_etc_hosts: false\nnetwork: disabled\n')


unittest.main()
