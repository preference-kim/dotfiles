#!/usr/bin/env python3
"""Install one token from stdin using this interpreter's Hugging Face runtime.

Decryption is performed separately; only the plaintext token is read from stdin.
Output deliberately contains status only. Run as the destination account.
"""
import contextlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import socket
import stat
import subprocess
import sys
import uuid


def hf_python(hf_cli):
    """Resolve venv and ordinary pip console-script interpreters without eval."""
    cli = Path(hf_cli).resolve()
    with cli.open() as stream:
        first = stream.readline(4096)
    if not first.startswith('#!'):
        raise RuntimeError('unsupported HF executable')
    parts = shlex.split(first[2:].strip())
    if len(parts) == 2 and Path(parts[0]).name == 'env':
        parts = [shutil.which(parts[1]) or '']
    if len(parts) != 1 or not re.fullmatch(r'python(?:[0-9.]+)?', Path(parts[0]).name):
        raise RuntimeError('unsupported HF interpreter')
    if not Path(parts[0]).is_absolute() or not os.access(parts[0], os.X_OK):
        raise RuntimeError('HF interpreter unavailable')
    return parts[0]


def snapshot(path):
    if not path.exists() and not path.is_symlink():
        return None
    meta = path.lstat()
    if not stat.S_ISREG(meta.st_mode) or meta.st_uid != os.getuid() or meta.st_nlink != 1:
        raise RuntimeError('unsafe credential file')
    if meta.st_size > 1024 * 1024:
        raise RuntimeError('oversized credential file')
    return (path.read_bytes(), stat.S_IMODE(meta.st_mode))


def replace(path, data, mode):
    staging = path.with_name('.agent-update-' + uuid.uuid4().hex)
    fd = os.open(staging, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(staging, path)
    finally:
        if staging.exists():
            staging.unlink()


def install(token, hf_cli):
    if not re.fullmatch(r'hf_[A-Za-z0-9]+', token):
        raise ValueError('invalid token format')
    if os.environ.get('HF_TOKEN') or os.environ.get('HUGGING_FACE_HUB_TOKEN'):
        raise RuntimeError('process token would override stored authentication')
    from huggingface_hub import constants, login
    paths = [Path(constants.HF_TOKEN_PATH), Path(constants.HF_STORED_TOKENS_PATH)]
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
    # The credential paths come from the installed library, including HF_HOME.
    root = paths[0].parent
    # Cover both destinations even when runtime settings split their parents.
    locks = []
    try:
        for parent in sorted({p.parent.resolve() for p in paths}):
            lock = parent / '.agent-update-credential-lock'
            lock.mkdir(mode=0o700)
            locks.append(lock)
            (lock / 'owner.json').write_text(json.dumps({'hostname': socket.gethostname(), 'pid': os.getpid()}))
    except Exception:
        for lock in reversed(locks):
            owner = lock / 'owner.json'
            if owner.exists():
                owner.unlink()
            lock.rmdir()
        raise
    before = {}
    after = None
    backup = None
    try:
        before = {p: snapshot(p) for p in paths}
        already = before[paths[0]] is not None and before[paths[0]][0].strip() == token.encode()
        if not already:
            backup_root = root / '.agent-update-backups'
            if backup_root.is_symlink():
                raise RuntimeError('unsafe backup directory')
            backup_root.mkdir(mode=0o700, exist_ok=True)
            if backup_root.stat().st_uid != os.getuid() or stat.S_IMODE(backup_root.stat().st_mode) != 0o700:
                raise RuntimeError('unsafe backup directory permissions')
            backup = backup_root / uuid.uuid4().hex
            backup.mkdir(mode=0o700)
            for index, (path, old) in enumerate(before.items()):
                if old is not None:
                    replace(backup / str(index), old[0], 0o600)
            replace(backup / 'metadata.json', json.dumps({str(i): {'path': str(p), 'mode': old[1] if old else None} for i, (p, old) in enumerate(before.items())}).encode(), 0o600)
            if any(snapshot(p) != old for p, old in before.items()):
                raise RuntimeError('credential changed after backup')
            # Restrict existing files before a library version that writes in place.
            for p, old in before.items():
                if old is not None:
                    p.chmod(0o600)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                login(token=token, add_to_git_credential=False)
        for p in paths:
            if snapshot(p) is not None:
                p.chmod(0o600)
        after = {p: snapshot(p) for p in paths}
        if after[paths[0]] is None or after[paths[0]][0].strip() != token.encode():
            raise RuntimeError('installed token differs')
        check = subprocess.run([hf_cli, 'auth', 'whoami'], capture_output=True, timeout=45)
        if check.returncode:
            raise RuntimeError('stored credential authentication failed')
        if any(snapshot(p) != value for p, value in after.items()):
            raise RuntimeError('credential changed during verification')
        return {'status': 'verified', 'token_changed': not already, 'mode': '0600', 'backup_created': backup is not None}
    except Exception:
        # Restore only a known post-write state. An interrupted library write or
        # an unrelated concurrent writer needs manual recovery from the backup.
        if after is not None and all(snapshot(p) == value for p, value in after.items()):
            for p, old in before.items():
                if old is None:
                    if p.exists():
                        p.unlink()
                else:
                    replace(p, old[0], old[1])
        raise
    finally:
        for lock in reversed(locks):
            owner = lock / 'owner.json'
            if owner.exists():
                owner.unlink()
            lock.rmdir()


def main():
    os.umask(0o077)
    try:
        if len(sys.argv) != 2:
            raise ValueError('expected path to the installed hf CLI')
        token = sys.stdin.buffer.read(4097)
        if len(token) > 4096:
            raise ValueError('oversized token input')
        result = install(token.decode().strip(), sys.argv[1])
    except Exception as error:
        result = {'status': 'failed', 'error_type': type(error).__name__, 'message': 'No success recorded; inspect lock ownership, local state and any recovery backups before retrying.'}
    print(json.dumps(result))
    return 0 if result['status'] == 'verified' else 1


if __name__ == '__main__':
    sys.exit(main())
