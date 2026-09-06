#!/usr/bin/env python3
"""Check the staged tree and every outgoing commit against an explicit file list."""

import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

POLICY = ".publication-policy.json"
BASE_SETTING = "publication.baseCommit"
MARKER = "# Installed by dotfiles publication-guard.py"


def git(*args):
    return subprocess.check_output(["git", *args], stderr=subprocess.PIPE)


def read_policy(data):
    policy = json.loads(data)
    base = policy["base_commit"]
    paths = policy["paths"]
    if not isinstance(base, str) or not re.fullmatch(r"[0-9a-f]{40}", base):
        raise ValueError("invalid publication base")
    if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
        raise ValueError("publication paths must be an explicit list")
    if len(paths) != len(set(paths)) or POLICY not in paths:
        raise ValueError("duplicate paths or missing publication policy")
    for path in paths:
        if (not path or str(PurePosixPath(path)) != path or path.startswith("/")
                or ".." in PurePosixPath(path).parts or any(c in path for c in "*?[]\n\r")):
            raise ValueError("publication paths must be exact repository-relative files")
    return base, set(paths)


def check_paths(paths, allowed):
    paths = set(paths)
    unexpected = paths - allowed
    if unexpected:
        raise ValueError("unreviewed paths: " + ", ".join(sorted(unexpected)))
    for path in paths:
        parts = PurePosixPath(path).parts
        if (any(p in {".agent-local", "__pycache__", "moreh-tt-metal"} for p in parts)
                or path.startswith("docs/harness/")
                or path in {".secrets", ".hf-token", "agent-file-sync.local.yaml"}):
            raise ValueError("local-only path: " + path)


def check_base(base):
    installed = git("config", "--local", "--get", BASE_SETTING).decode().strip()
    if installed != base:
        raise ValueError("publication base differs from the installed guard")


def check_index():
    records = git("ls-files", "--stage", "-z").split(b"\0")
    paths = []
    for record in filter(None, records):
        metadata, path = record.split(b"\t", 1)
        if metadata.split()[2] != b"0":
            raise ValueError("index contains an unresolved merge")
        paths.append(path.decode())
    base, allowed = read_policy(git("show", ":" + POLICY))
    check_base(base)
    check_paths(paths, allowed)


def check_history(tip):
    tip = git("rev-parse", "--verify", tip + "^{commit}").decode().strip()
    base, _ = read_policy(git("show", tip + ":" + POLICY))
    check_base(base)
    git("merge-base", "--is-ancestor", base, tip)
    commits = git("rev-list", "--reverse", tip, "^" + base).decode().splitlines()
    for commit in commits:
        commit_base, allowed = read_policy(git("show", commit + ":" + POLICY))
        if commit_base != base:
            raise ValueError("publication base changed within outgoing history")
        paths = git("ls-tree", "-rz", "--name-only", commit).decode().split("\0")
        check_paths(filter(None, paths), allowed)


def check_push(lines):
    for line in lines:
        fields = line.split()
        if len(fields) != 4:
            raise ValueError("invalid pre-push input")
        _, local_oid, _, _ = fields
        if set(local_oid) == {"0"}:
            continue  # Deleting a remote ref publishes no objects.
        check_history(local_oid)


def install_hook(hook, script, mode):
    prior = hook.with_name(hook.name + ".before-publication-guard")
    for entry in (hook, prior):
        if entry.is_symlink() and not entry.exists():
            raise ValueError("dangling hook link requires inspection: " + str(entry))
    if hook.exists() and (hook.is_symlink() or MARKER not in hook.read_text()):
        if prior.exists():
            raise ValueError("existing hook backup requires inspection: " + str(prior))
        hook.rename(prior)
    commands = [[sys.executable, script, mode]]
    if prior.exists() and os.access(prior, os.X_OK):
        commands.insert(0, [str(prior)])
    hook.write_text(
        "#!/usr/bin/env python3\n" + MARKER + "\n"
        "import subprocess, sys\n"
        "payload = sys.stdin.buffer.read() if " + repr(mode == "push") + " else b''\n"
        "commands = " + repr(commands) + "\n"
        "for command in commands:\n"
        "    args = command + sys.argv[1:] if len(command) == 1 else command\n"
        "    result = subprocess.run(args, input=payload)\n"
        "    if result.returncode:\n"
        "        sys.exit(result.returncode)\n")
    hook.chmod(0o755)


def install():
    root = Path(__file__).resolve().parent.parent
    script = str(root / "scripts/publication-guard.py")
    for repo in (root, root / "skills"):
        def repository_git(*args):
            return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()
        if Path(repository_git("rev-parse", "--show-toplevel")).resolve() != repo:
            raise ValueError("unexpected repository root: " + str(repo))
        configured = subprocess.run(
            ["git", "-C", str(repo), "config", "--get", "core.hooksPath"],
            capture_output=True, text=True)
        if configured.returncode not in (0, 1) or configured.stdout.strip():
            raise ValueError("inspect the existing core.hooksPath before installing")
        base, _ = read_policy((repo / POLICY).read_bytes())
        installed_base = subprocess.run(
            ["git", "-C", str(repo), "config", "--local", "--get", BASE_SETTING],
            capture_output=True, text=True)
        if installed_base.returncode == 1:
            repository_git("config", "--local", BASE_SETTING, base)
        elif installed_base.returncode != 0 or installed_base.stdout.strip() != base:
            raise ValueError("publication base conflicts with the installed guard")
        hooks = Path(repository_git("rev-parse", "--path-format=absolute", "--git-path", "hooks"))
        hooks.mkdir(exist_ok=True)
        for name, mode in (("pre-commit", "index"), ("pre-push", "push")):
            install_hook(hooks / name, script, mode)
        print("Publication hooks installed: " + str(repo))


def main():
    try:
        mode = sys.argv[1]
        if mode == "index":
            check_index()
        elif mode == "push":
            check_push(sys.stdin)
        elif mode == "history" and len(sys.argv) == 3:
            check_history(sys.argv[2])
        elif mode == "install":
            install()
        else:
            raise ValueError("usage: publication-guard.py index|push|history COMMIT|install")
    except (IndexError, KeyError, TypeError, ValueError, OSError, subprocess.CalledProcessError) as error:
        # Never include git's captured output: blobs can contain confidential data.
        detail = "required Git object or policy is unavailable" if isinstance(error, subprocess.CalledProcessError) else str(error)
        print("Publication blocked: " + detail, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
