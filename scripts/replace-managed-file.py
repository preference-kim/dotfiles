#!/usr/bin/env python3
"""Atomic, guarded replacement; the caller owns approval, backup and verification."""
import json
import os
from pathlib import Path
import stat
import sys
import uuid


def snapshot(path):
    meta = path.lstat()
    if not stat.S_ISREG(meta.st_mode) or meta.st_nlink != 1:
        raise ValueError('destination must be a regular, singly linked file')
    return path.read_bytes(), (meta.st_uid, meta.st_gid, stat.S_IMODE(meta.st_mode))


def replace(path, before, after, mode, *, allow_create=False):
    def current():
        try:
            return snapshot(path)
        except FileNotFoundError:
            if allow_create and before is None:
                return None
            raise
    original = current()
    if (original[0] if original else None) != before:
        raise ValueError('destination differs from reviewed baseline')
    if original and before == after and original[1][2] == mode:
        return 'unchanged'
    owner = original[1][:2] if original else (os.geteuid(), os.getegid())
    staging = path.with_name('.agent-update-' + uuid.uuid4().hex)
    try:
        fd = os.open(staging, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(after)
            stream.flush()
            os.fchown(stream.fileno(), *owner)
            # An explicit chmod is required: the caller's umask may be 077.
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
        if current() != original:
            raise ValueError('destination changed while staging')
        if original is None:
            # Link creation fails atomically if another writer creates the destination.
            os.link(staging, path)
            staging.unlink()
        else:
            os.replace(staging, path)
        if snapshot(path) != (after, (*owner, mode)):
            raise RuntimeError('post-write verification failed; inspect backup')
        return 'changed'
    finally:
        if staging.exists():
            staging.unlink()


def validate_cloud_config(path, content):
    if os.geteuid() != 0 or os.getegid() != 0:
        raise ValueError('cloud configuration requires root ownership')
    settings = [line.strip() for line in content.splitlines()
                if line.strip() and not line.lstrip().startswith('#')]
    if settings != ['manage_etc_hosts: false']:
        raise ValueError('unexpected cloud configuration')
    try:
        _, metadata = snapshot(path)
    except FileNotFoundError:
        return
    if metadata[:2] != (0, 0):
        raise ValueError('unexpected cloud configuration ownership')


def main():
    os.umask(0o077)
    try:
        data = json.load(sys.stdin)
        allowed = {'/etc/hosts': 0o644, '~/.ssh/config': 0o600,
                   '~/.ssh/moreh_cluster.conf': 0o600,
                   '/etc/cloud/cloud.cfg.d/99-moreh-preserve-hosts.cfg': 0o644}
        mode = allowed[data['path']]
        if data['mode'] != format(mode, '04o'):
            raise ValueError('unexpected file mode')
        cloud_config = data['path'] == '/etc/cloud/cloud.cfg.d/99-moreh-preserve-hosts.cfg'
        if cloud_config:
            validate_cloud_config(Path(data['path']), data['after'])
        before = data['before'].encode() if data['before'] is not None else None
        ssh_file = data['path'].startswith('~/.ssh/')
        allow_create = cloud_config or ssh_file
        path = Path(data['path']).expanduser()
        if ssh_file and before is None and not path.parent.exists():
            path.parent.mkdir(mode=0o700)
            os.chmod(path.parent, 0o700)
        result = replace(path, before, data['after'].encode(), mode, allow_create=allow_create)
        print(json.dumps({'status': result, 'verified': True}))
        return 0
    except Exception as error:
        print(json.dumps({'status': 'failed', 'error_type': type(error).__name__}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
