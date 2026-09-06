"""Offline regression tests for accidental publication paths and ancestry."""

import io
import ast
import json
import subprocess
import unittest
from unittest.mock import Mock, patch

import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("publication_guard", Path(__file__).with_name("publication-guard.py"))
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

BASE = "1" * 40
FIRST = "2" * 40
TIP = "3" * 40


def policy(*paths):
    return json.dumps({"base_commit": BASE, "paths": [guard.POLICY, *paths]}).encode()


class PublicationGuardTests(unittest.TestCase):
    def test_exact_paths_allow_files_and_gitlinks(self):
        _, allowed = guard.read_policy(policy("AGENTS.md", "skills"))
        guard.check_paths([guard.POLICY, "AGENTS.md", "skills"], allowed)

    def test_new_file_is_rejected_even_under_an_approved_directory(self):
        _, allowed = guard.read_policy(policy("docs/guide.md"))
        with self.assertRaisesRegex(ValueError, "unreviewed paths"):
            guard.check_paths(["docs/guide.md", "docs/session-output.json"], allowed)

    def test_policy_rejects_globs_traversal_and_duplicate_paths(self):
        for paths in [("docs/*",), ("../private.md",), ("./guide.md",), ("guide.md", "guide.md")]:
            with self.subTest(paths=paths), self.assertRaises(ValueError):
                guard.read_policy(policy(*paths))

    def test_local_only_paths_are_rejected_even_when_listed(self):
        for path in [".hf-token", "agent-file-sync.local.yaml", ".agent-local/report.md", "docs/harness/report.md", "moreh-tt-metal/SKILL.md"]:
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "local-only"):
                guard.check_paths([path], {path})

    def test_local_only_check_also_handles_history_iterators(self):
        path = ".agent-local/report.md"
        with self.assertRaisesRegex(ValueError, "local-only"):
            guard.check_paths(iter([path]), {path})

    def test_index_uses_staged_policy_and_rejects_unmerged_entries(self):
        def git(*args):
            if args[0] == "ls-files":
                return b"100644 " + TIP.encode() + b" 2\tAGENTS.md\0"
            self.fail("An unresolved index must be rejected before reading policy")
        with patch.object(guard, "git", side_effect=git), self.assertRaisesRegex(ValueError, "unresolved merge"):
            guard.check_index()
        records = b"100644 " + TIP.encode() + b" 0\tAGENTS.md\0"
        with patch.object(guard, "git", side_effect=[records, policy("AGENTS.md"), BASE.encode()]) as mocked:
            guard.check_index()
            mocked.assert_any_call("show", ":" + guard.POLICY)

    def history_git(self, bad_paths=None, missing_policy=False):
        def git(*args):
            if args[0] == "config":
                return BASE.encode()
            if args[0] == "rev-parse":
                return TIP.encode()
            if args[0] == "merge-base":
                return b""
            if args[0] == "rev-list":
                self.assertEqual(args, ("rev-list", "--reverse", TIP, "^" + BASE))
                return (FIRST + "\n" + TIP + "\n").encode()
            if args[0] == "show":
                if missing_policy and args[1].startswith(FIRST):
                    raise subprocess.CalledProcessError(128, "git")
                return policy("AGENTS.md")
            if args[0] == "ls-tree":
                paths = bad_paths if args[-1] == FIRST and bad_paths else [guard.POLICY, "AGENTS.md"]
                return "\0".join(paths).encode()
            self.fail(args)
        return git

    def test_clean_history_is_accepted(self):
        with patch.object(guard, "git", side_effect=self.history_git()):
            guard.check_history(TIP)

    def test_deleted_intermediate_artifact_still_blocks_push(self):
        with patch.object(guard, "git", side_effect=self.history_git(["session-output.json"])), self.assertRaisesRegex(ValueError, "unreviewed paths"):
            guard.check_history(TIP)

    def test_merged_legacy_history_without_policy_is_rejected(self):
        with patch.object(guard, "git", side_effect=self.history_git(missing_policy=True)), self.assertRaises(subprocess.CalledProcessError):
            guard.check_history(TIP)

    def test_advancing_policy_base_cannot_exempt_history(self):
        changed = json.loads(policy("AGENTS.md"))
        changed["base_commit"] = FIRST
        with patch.object(guard, "git", side_effect=[TIP.encode(), json.dumps(changed).encode(), BASE.encode()]), self.assertRaisesRegex(ValueError, "installed guard"):
            guard.check_history(TIP)

    def test_deletion_and_multiple_ref_updates(self):
        zero = "0" * 40
        lines = f"(delete) {zero} refs/heads/old {FIRST}\nrefs/heads/main {TIP} refs/heads/main {FIRST}\nrefs/heads/next {FIRST} refs/heads/next {zero}\n"
        with patch.object(guard, "check_history") as check:
            guard.check_push(io.StringIO(lines))
            self.assertEqual([call.args[0] for call in check.call_args_list], [TIP, FIRST])

    def test_malformed_push_input_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid pre-push input"):
            guard.check_push(["not a ref update with four fields"])

    def hook_paths(self):
        hook, prior = Mock(spec=Path), Mock(spec=Path)
        hook.name = "pre-push"
        hook.with_name.return_value = prior
        hook.is_symlink.return_value = False
        prior.is_symlink.return_value = False
        return hook, prior

    def test_disabled_existing_hook_is_preserved_without_execution(self):
        hook, prior = self.hook_paths()
        hook.exists.return_value = True
        hook.read_text.return_value = "# disabled user hook"
        prior.exists.side_effect = [False, True]
        with patch.object(guard.os, "access", return_value=False):
            guard.install_hook(hook, "guard.py", "push")
        hook.rename.assert_called_once_with(prior)
        prior.chmod.assert_not_called()
        written = hook.write_text.call_args.args[0]
        commands = next(line.removeprefix("commands = ") for line in written.splitlines() if line.startswith("commands = "))
        self.assertEqual(ast.literal_eval(commands), [[guard.sys.executable, "guard.py", "push"]])

    def test_dangling_hook_or_backup_stops_before_write(self):
        for target in ["hook", "backup"]:
            hook, prior = self.hook_paths()
            entry = hook if target == "hook" else prior
            entry.is_symlink.return_value = True
            entry.exists.return_value = False
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, "dangling hook"):
                guard.install_hook(hook, "guard.py", "push")
            hook.rename.assert_not_called()
            hook.write_text.assert_not_called()


if __name__ == "__main__":
    unittest.main()
