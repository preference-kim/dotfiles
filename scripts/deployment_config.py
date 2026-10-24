"""Load private deployment settings; public code owns path and mode constraints."""
import argparse
import base64
import json
import os
from pathlib import Path
import re
import stat
import subprocess


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate configuration key')
        result[key] = value
    return result


def validate(config):
    if set(config) != {'schema_version', 'bootstrap', 'paths'} or type(config['schema_version']) is not int or config['schema_version'] != 1:
        raise ValueError('invalid deployment configuration')
    bootstrap, paths = config['bootstrap'], config['paths']
    if set(bootstrap) != {'dotfiles_url', 'private_url', 'github_account'}:
        raise ValueError('invalid bootstrap fields')
    # Literal GitHub clone URLs only; no options, substitutions, credentials or ports.
    for key in ['dotfiles_url', 'private_url']:
        if not isinstance(bootstrap[key], str) or not re.fullmatch(
                r'(?:https://github\.com/|ssh://git@github\.com/|git@github\.com:)[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?', bootstrap[key]):
            raise ValueError('invalid repository URL')
    if not bootstrap['dotfiles_url'].startswith('https://github.com/') or not bootstrap['private_url'].startswith('ssh://git@github.com/'):
        raise ValueError('bootstrap requires public HTTPS and dedicated private SSH transport')
    if not isinstance(bootstrap['github_account'], str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]*', bootstrap['github_account']):
        raise ValueError('invalid GitHub account')
    if set(paths) != {'ssh_include', 'cluster_key', 'cloud_hosts'}:
        raise ValueError('invalid deployment path fields')
    patterns = {
        'ssh_include': r'~/\.ssh/[A-Za-z0-9][A-Za-z0-9_-]*\.conf',
        'cluster_key': r'~/\.ssh/[A-Za-z0-9][A-Za-z0-9_-]*',
        'cloud_hosts': r'/etc/cloud/cloud\.cfg\.d/99-[A-Za-z0-9][A-Za-z0-9_-]*-preserve-hosts\.cfg',
    }
    for key, pattern in patterns.items():
        if not isinstance(paths[key], str) or not re.fullmatch(pattern, paths[key]):
            raise ValueError('destination outside its permitted role')
    # Protect personal names on case-insensitive filesystems as well.
    key_name = paths['cluster_key'].rsplit('/', 1)[1].casefold()
    if key_name in {'config', 'authorized_keys', 'authorized_keys2', 'known_hosts', 'known_hosts2', 'environment', 'rc', 'identity'} or key_name.startswith('id_'):
        raise ValueError('cluster key would replace a personal SSH file')
    return config


def protected_json(path):
    path = Path(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'r') as stream:
        meta = os.fstat(stream.fileno())
        if (not stat.S_ISREG(meta.st_mode) or meta.st_nlink != 1 or
                meta.st_uid != os.geteuid() or stat.S_IMODE(meta.st_mode) & 0o077):
            raise ValueError('configuration must be an owned private regular file')
        content = stream.read()
        after = os.fstat(stream.fileno())
        if (meta.st_size, meta.st_mtime_ns, meta.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError('configuration changed while reading')
    return json.loads(content, object_pairs_hook=unique_object)


def load_config(snapshot=None):
    if snapshot is not None:
        return validate(protected_json(snapshot))
    registration = protected_json(Path.home() / '.config/agent-update/private-sync.json')
    checkout = Path(registration['checkout'])
    if not checkout.is_absolute() or checkout.is_symlink():
        raise ValueError('private checkout must be a literal absolute directory')
    meta = checkout.stat()
    if meta.st_uid != os.geteuid() or stat.S_IMODE(meta.st_mode) & 0o077:
        raise ValueError('private checkout permissions are not private')
    def git(*args):
        return subprocess.check_output(['git', '-C', str(checkout), *args], text=True).strip()
    if Path(git('rev-parse', '--show-toplevel')).resolve() != checkout.resolve():
        raise ValueError('not a private checkout root')
    if git('remote', 'get-url', 'origin') != registration['repository_url']:
        raise ValueError('private origin mismatch')
    if git('status', '--porcelain'):
        raise ValueError('private checkout has local changes')
    subprocess.run(['git', '-C', str(checkout), 'fetch', 'origin', 'main'], check=True)
    revision = git('rev-parse', 'FETCH_HEAD')
    config = validate(json.loads(git('show', revision + ':deployment.json'), object_pairs_hook=unique_object))
    return config


def allowed_paths(config):
    paths = validate(config)['paths']
    return {'/etc/hosts': 0o644, '~/.ssh/config': 0o600,
            paths['ssh_include']: 0o600, paths['cluster_key']: 0o600,
            paths['cluster_key'] + '.pub': 0o644, paths['cloud_hosts']: 0o644}


def checked_ssh_dir():
    directory = Path.home() / '.ssh'
    if directory.is_symlink():
        raise ValueError('SSH directory must not be a symlink')
    if directory.exists():
        meta = directory.stat()
        if not stat.S_ISDIR(meta.st_mode) or meta.st_uid != os.geteuid():
            raise ValueError('SSH directory ownership mismatch')
    else:
        directory.mkdir(mode=0o700)
    return directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deployment-config', help='protected snapshot from an approved private revision')
    parser.add_argument('--bootstrap-base64', action='store_true')
    args = parser.parse_args()
    try:
        config = load_config(args.deployment_config)
        content = json.dumps(config, separators=(',', ':'))
        print(base64.b64encode(content.encode()).decode() if args.bootstrap_base64 else content)
    except (OSError, KeyError, TypeError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, 'Deployment configuration unavailable: ' + type(error).__name__ + '\n')


if __name__ == '__main__':
    main()
