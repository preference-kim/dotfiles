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


def replace(path, before, after, mode):
    original = snapshot(path)
    if original[0] != before:
        raise ValueError('destination differs from reviewed baseline')
    if before == after and original[1][2] == mode:
        return 'unchanged'
    staging = path.with_name('.agent-update-' + uuid.uuid4().hex)
    try:
        fd = os.open(staging, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(after)
            stream.flush()
            os.fchown(stream.fileno(), original[1][0], original[1][1])
            # An explicit chmod is required: the caller's umask may be 077.
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
        if snapshot(path) != original:
            raise ValueError('destination changed while staging')
        os.replace(staging, path)
        if snapshot(path) != (after, (original[1][0], original[1][1], mode)):
            raise RuntimeError('post-write verification failed; inspect backup')
        return 'changed'
    finally:
        if staging.exists():
            staging.unlink()


def main():
    os.umask(0o077)
    try:
        data = json.load(sys.stdin)
        allowed = {'/etc/hosts': 0o644, '~/.ssh/config': 0o600,
                   '~/.ssh/moreh_cluster.conf': 0o600}
        mode = allowed[data['path']]
        if data['mode'] != format(mode, '04o'):
            raise ValueError('unexpected file mode')
        result = replace(Path(data['path']).expanduser(), data['before'].encode(),
                         data['after'].encode(), mode)
        print(json.dumps({'status': result, 'verified': True}))
        return 0
    except Exception as error:
        print(json.dumps({'status': 'failed', 'error_type': type(error).__name__}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
