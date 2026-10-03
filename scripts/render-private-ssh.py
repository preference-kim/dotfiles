#!/usr/bin/env python3
"""Render shared SSH rules; no filesystem access, decryption, or deployment."""
import argparse
import fnmatch
import json
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
        require(set(rule) <= {'nodes', 'hosts', 'aliases', 'exclude_aliases', 'option_sets'}, 'invalid SSH rule fields')
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
        require(not any(f['path'] in {'~/.ssh/config', '~/.ssh/moreh_cluster.conf'}
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
    bindings = {**catalog['bindings'], **context['bindings'], **selection['bindings'],
                'account': profile['account']}
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
            output.append('')
    output += ['Host *', '']
    return '\n'.join(output)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True)
    args = parser.parse_args()
    try:
        sys.stdout.write(render(json.load(sys.stdin, object_pairs_hook=unique_object), args.profile))
    except (KeyError, TypeError, ValueError) as error:
        print('SSH inventory validation failed: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
