#!/usr/bin/env python3
"""Render shared SSH rules; no filesystem access, decryption, or deployment."""
import argparse
import fnmatch
import ipaddress
import json
from pathlib import Path
import re
import string
import sys

PROFILE_BINDINGS = {'identity_file', 'known_hosts_file', 'login_identity_file', 'login_known_hosts_file'}
ADDITIVE_OPTIONS = {'identityfile', 'certificatefile'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value):
    require(isinstance(value, str) and value and not any(c in value for c in '\r\n\0'),
            'expected a nonempty single-line string')
    return value


def expand(value, bindings):
    try:
        result = text(string.Template(text(value)).substitute(bindings))
        require(not re.search(r'\$\{[A-Za-z_][A-Za-z0-9_]*\}', result),
                'unresolved SSH variable')
        return result
    except (KeyError, ValueError) as error:
        raise ValueError('invalid or unbound SSH variable') from error


def validate_catalog(inventory):
    require(inventory.get('schema_version') == 2, 'SSH catalog requires inventory version 2')
    catalog = inventory['ssh']
    require(set(catalog) == {'bindings', 'option_sets', 'rules', 'contexts'}, 'invalid SSH catalog fields')
    validate_bindings(catalog['bindings'])
    for key in ['option_sets', 'rules', 'contexts']:
        section = catalog[key]
        require(isinstance(section, dict), 'invalid SSH catalog section')
        require(all(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', name) for name in section),
                'invalid SSH catalog identifier')
    nodes = {node['name']: node for node in inventory['nodes']}
    require(len(nodes) == len(inventory['nodes']), 'duplicate node')
    aliases = {}
    for node in nodes.values():
        for name in [node['name'], *node['aliases'], *node.get('deprecated_aliases', [])]:
            require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', text(name)), 'invalid node alias')
            require(name.lower() not in aliases or aliases[name.lower()] == node['name'],
                    'ambiguous node alias')
            aliases[name.lower()] = node['name']
    for name, options in catalog['option_sets'].items():
        text(name)
        require(isinstance(options, list) and options, 'empty option set')
        for pair in options:
            require(isinstance(pair, list) and len(pair) == 2, 'invalid SSH option')
            key, value = pair
            require(isinstance(key, str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9]*', key),
                    'invalid SSH directive')
            require(key.lower() not in {'host', 'match', 'include'}, 'scope directive in option set')
            text(value)
    for rule in catalog['rules'].values():
        require(set(rule) <= {'nodes', 'hosts', 'aliases', 'exclude_aliases', 'option_sets', 'fallback_jump'},
                'invalid SSH rule fields')
        require(('nodes' in rule) != ('hosts' in rule), 'rule needs nodes or hosts')
        targets = rule.get('nodes', rule.get('hosts'))
        require(isinstance(targets, list) and targets and len(targets) == len(set(targets)),
                'empty or duplicate SSH targets')
        require(rule.get('aliases', 'name') in {'name', 'canonical', 'named', 'all'}, 'invalid alias selection')
        require(isinstance(rule.get('exclude_aliases', []), list), 'invalid alias exclusions')
        for pattern in rule.get('exclude_aliases', []):
            text(pattern)
        if 'nodes' in rule:
            require(set(targets) <= nodes.keys(), 'unknown SSH node')
        else:
            require('aliases' not in rule, 'aliases apply only to nodes')
        if 'fallback_jump' in rule:
            require('nodes' in rule and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', text(rule['fallback_jump'])),
                    'fallback jump requires nodes and a literal gateway alias')
        refs = rule['option_sets']
        require(isinstance(refs, list) and refs and len(refs) == len(set(refs)),
                'empty or duplicate option-set references')
        require(set(refs) <= catalog['option_sets'].keys(), 'unknown SSH option set')
    for context in catalog['contexts'].values():
        require(set(context) == {'rules', 'bindings'}, 'invalid SSH context fields')
        refs = context['rules']
        require(isinstance(refs, list) and refs and len(refs) == len(set(refs)),
                'empty or duplicate rule references')
        require(set(refs) <= catalog['rules'].keys(), 'unknown SSH rule')
        validate_bindings(context['bindings'])
    for profile in inventory['profiles'].values():
        require(not any(f['path'].startswith('~/.ssh/')
                        for f in profile['files']), 'SSH file snapshots are forbidden in version 2')
        if 'ssh' in profile:
            require('configuration_owner' not in profile, 'delegated profile cannot own SSH settings')
            selection = profile['ssh']
            require(set(selection) == {'context', 'bindings'}, 'invalid profile SSH fields')
            require(selection['context'] in catalog['contexts'], 'unknown SSH context')
            validate_bindings(selection['bindings'])
            require(set(selection['bindings']) <= PROFILE_BINDINGS,
                    'profile bindings may only select local key and known-hosts paths')
    return catalog, nodes


def validate_bindings(bindings):
    require(isinstance(bindings, dict), 'invalid SSH bindings')
    for key, value in bindings.items():
        require(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', key) and
                key not in {'name', 'ip', 'account'}, 'reserved or invalid binding name')
        text(value)


def render(inventory, profile_id):
    catalog, nodes = validate_catalog(inventory)
    profile = inventory['profiles'][profile_id]
    require('configuration_owner' not in profile, 'render on the configuration owner')
    selection = profile['ssh']
    context = catalog['contexts'][selection['context']]
    profile_jumps = profile.get('ssh_fallback_jumps', {})
    require(isinstance(profile_jumps, dict) and set(profile_jumps) <= set(context['rules']),
            'fallback rule missing from selected context')
    for rule_id, jump in profile_jumps.items():
        rule = catalog['rules'][rule_id]
        require('nodes' in rule and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', text(jump)) and
                rule.get('fallback_jump', jump) == jump, 'invalid or conflicting profile fallback')
    bindings = {**catalog['bindings'], **context['bindings'], **selection['bindings'],
                'account': profile['account']}
    declared_hosts = set()
    fallback_jumps = set()
    output = ['# Generated from the approved private SSH catalog. Do not edit.', 'Host *', '']
    for rule_id in context['rules']:
        rule = catalog['rules'][rule_id]
        targets = rule.get('nodes', [None])
        for target in targets:
            values = dict(bindings)
            if target is None:
                hosts = [expand(host, values) for host in rule['hosts']]
            else:
                node = nodes[target]
                metadata = node.get('ssh', {})
                validate_bindings(metadata)
                require(not set(metadata).intersection(values), 'node metadata shadows context binding')
                values.update(metadata)
                values.update(name=node['name'], ip=node['ip'])
                hosts = [node['name']]
                if rule.get('aliases') in {'canonical', 'named', 'all'}:
                    hosts += node['aliases']
                if rule.get('aliases') in {'named', 'all'}:
                    hosts += node.get('deprecated_aliases', [])
                if rule.get('aliases') == 'all':
                    hosts += [node['ip']]
                    if node.get('machine_name'):
                        hosts += [node['machine_name'], node['machine_name'].lower()]
                hosts = [host for host in hosts if not any(fnmatch.fnmatchcase(host.lower(), pattern.lower())
                         for pattern in rule.get('exclude_aliases', []))]
                require(hosts, 'rule excludes every name of a node')
            require(all(re.fullmatch(r'[A-Za-z0-9_.:%\[\]-]+', text(host)) for host in hosts),
                    'SSH rules require literal host names')
            hosts = list(dict.fromkeys(hosts))
            declared_hosts.update(hosts)
            output += ['# ' + rule_id, 'Host ' + ' '.join(hosts)]
            seen = {}
            for ref in rule['option_sets']:
                for key, value in catalog['option_sets'][ref]:
                    value = expand(value, values)
                    lower = key.lower()
                    if lower in seen and lower not in ADDITIVE_OPTIONS:
                        require(seen[lower] == value, 'conflicting option sets in one rule')
                        continue
                    seen[lower] = value
                    if lower in ADDITIVE_OPTIONS and any(c.isspace() or c in '#"' for c in value):
                        value = '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'
                    output.append('    ' + key + ' ' + value)
            gateway = profile_jumps.get(rule_id, rule.get('fallback_jump'))
            if gateway is not None:
                require(not {'proxyjump', 'proxycommand'}.intersection(seen) and gateway not in hosts,
                        'fallback conflicts with a fixed proxy or its own destination')
                address = str(ipaddress.ip_address(seen['hostname']))
                port = int(seen.get('port', '22'))
                require(0 < port < 65536, 'invalid fallback destination port')
                # Only a validated numeric endpoint enters this fixed, bounded reachability test.
                probe = ("python3 -c 'import socket,sys; "
                         "socket.create_connection((sys.argv[1],int(sys.argv[2])),1).close()' "
                         f"{address} {port} 2>/dev/null")
                output.extend(['Match originalhost ' + ','.join(hosts) + ' !exec "' + probe + '"',
                               '    ProxyJump ' + gateway])
                fallback_jumps.add(gateway)
            output.append('')
    require(fallback_jumps <= declared_hosts, 'fallback gateway missing from selected context')
    validate_verification(profile, declared_hosts)
    personal_migrations(profile)
    output += ['Host *', '']
    return '\n'.join(output)


def validate_verification(profile, declared_hosts):
    verification = profile.get('ssh_verification', {})
    require(isinstance(verification, dict) and
            set(verification) <= {'expected_hostnames', 'excluded_routes', 'required_cluster_key_routes'},
            'invalid SSH verification policy')
    required = verification.get('required_cluster_key_routes', [])
    require(isinstance(required, list) and all(isinstance(alias, str) and
            re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', alias) for alias in required) and
            len(required) == len(set(required)) and set(required) <= declared_hosts,
            'required cluster-key route is missing, duplicated or invalid')
    require(not set(required).intersection(verification.get('excluded_routes', {})),
            'a required cluster-key route cannot be excluded')
    for field in ['expected_hostnames', 'excluded_routes']:
        entries = verification.get(field, {})
        require(isinstance(entries, dict), 'invalid SSH verification entries')
        require(set(entries) <= declared_hosts, 'verification alias is not declared by this profile')
        for alias, value in entries.items():
            require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', alias),
                    'verification aliases must be literal names')
            if field == 'expected_hostnames':
                require(isinstance(value, list) and value and
                        all(isinstance(name, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', name)
                            for name in value) and len(value) == len(set(value)),
                        'expected hostnames must be unique literal names')
            else:
                require(isinstance(value, dict) and set(value) == {'reason', 'resume_condition'},
                        'exclusion requires reason and resume condition')
                text(value['reason'])
                text(value['resume_condition'])


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def personal_migrations(profile):
    migrations = profile.get('ssh_personal_migrations', {})
    required = profile.get('ssh_verification', {}).get('required_cluster_key_routes', [])
    require(isinstance(migrations, dict) and set(migrations) <= set(required),
            'personal stanza migration requires a declared cluster-key route')
    for alias, stanzas in migrations.items():
        require(isinstance(stanzas, list) and 1 <= len(stanzas) <= 2, 'invalid legacy stanza list')
        for index, before in enumerate(stanzas):
            require(isinstance(before, str) and before.endswith('\n') and '\r' not in before,
                    'invalid legacy stanza text')
            header, *lines = before.splitlines()
            if index == 0:
                require(header == 'Host ' + alias and lines and all(re.fullmatch(
                    r'[ \t]+(?:HostName|Port|User|IdentityFile|IdentitiesOnly|ForwardAgent|IdentityAgent|ProxyJump)[ \t]+[^\s#]+',
                    line, re.IGNORECASE) for line in lines), 'invalid legacy Host stanza')
            else:
                # Compared as text for removal only. Never evaluate a supplied command.
                require(header.startswith('Match originalhost ' + alias + ' !exec ') and
                        len(lines) == 1 and re.fullmatch(r'[ \t]+ProxyJump[ \t]+[A-Za-z0-9._-]+', lines[0]),
                        'invalid legacy conditional jump stanza')
    return migrations


def migrate_personal_config(config, profile):
    """Remove only exact approved single-alias stanzas, preserving surrounding text."""
    sections = re.split(r'(?im)(?=^[ \t]*(?:Host|Match)[ \t=])', config)
    for alias, stanzas in personal_migrations(profile).items():
        expected = {stanza.split(' ', 1)[0].lower(): stanza for stanza in stanzas}
        found = set()
        for index, section in enumerate(sections):
            header = section.partition('\n')[0].split('#', 1)[0].strip()
            fields = re.split(r'[ \t=]+', header.lower())
            kind = fields[0]
            host_match = kind == 'host' and alias.lower() in fields[1:]
            conditional_match = (fields[:2] == ['match', 'originalhost'] and len(fields) > 2 and
                                 alias.lower() in fields[2].split(','))
            if not (host_match or conditional_match):
                continue
            require(kind in expected and kind not in found, 'unapproved or duplicate personal stanza: ' + alias)
            before = expected[kind]
            remainder = section[len(before):]
            require(section.startswith(before) and
                    all(not line.strip() or line.lstrip().startswith('#') for line in remainder.splitlines()),
                    'personal stanza differs from approved migration: ' + alias)
            sections[index] = remainder
            found.add(kind)
    return ''.join(sections)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--personal-config', type=Path,
                        help='emit a candidate personal config after exact approved stanza removals')
    args = parser.parse_args()
    try:
        inventory = json.load(sys.stdin, object_pairs_hook=unique_object)
        result = render(inventory, args.profile)
        if args.personal_config is not None:
            with args.personal_config.open(newline='') as source:
                result = migrate_personal_config(source.read(), inventory['profiles'][args.profile])
        sys.stdout.buffer.write(result.encode())
    except (OSError, KeyError, TypeError, ValueError) as error:
        print('SSH inventory validation failed: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
