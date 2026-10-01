"""Synthetic files only; supply an explicit private test work directory."""
import importlib.util
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


unittest.main()
