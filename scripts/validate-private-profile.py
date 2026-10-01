#!/usr/bin/env python3
"""Read-only device binding and hosts layout checks; approval remains separate."""
import collections
import getpass
import ipaddress
import json
import socket
import sys


def hosts_records(text):
    records = collections.defaultdict(list)
    for line in text.splitlines():
        fields = line.split('#', 1)[0].split()
        if not fields:
            continue
        address = str(ipaddress.ip_address(fields[0]))
        for name in fields[1:]:
            records[name.lower()].append(address)
    return records


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(inventory, registration, hostname, account):
    role = registration.get('device_role')
    require(role in ('development-server', 'personal-device'), 'explicit role registration required')
    require(registration.get('account') == account, 'registration account mismatch')
    mapping = registration.get('host_profiles', {})
    if hostname in mapping:
        selected = mapping[hostname]
    else:
        require(registration.get('expected_hostname') == hostname, 'unregistered hostname')
        selected = registration['profile']
    profile = inventory['profiles'][selected]
    require(profile.get('expected_hostname') == hostname, 'profile hostname mismatch')
    require(profile.get('account') == account, 'profile account mismatch')
    require(profile.get('device_role') == role, 'profile role mismatch')
    owner_id = profile.get('configuration_owner')
    if 'configuration_owner' in profile:
        require(isinstance(owner_id, str) and bool(owner_id) and owner_id != selected,
                'invalid configuration owner')
        owner = inventory['profiles'].get(owner_id)
        require(isinstance(owner, dict) and 'configuration_owner' not in owner,
                'configuration owner must be a managing profile')
        require(owner.get('account') == account and owner.get('device_role') == role,
                'configuration owner identity mismatch')
        require('hosts_scope' in owner and
                sum(item['path'] == '/etc/hosts' for item in owner['files']) == 1,
                'configuration owner has no hosts plan')
        require(profile.get('files') == [] and profile.get('ssh_equivalence') == [],
                'delegated configuration must have no file plans')
        require(not any(key in profile for key in
                        ('hosts_scope', 'preserved_hosts_blocks', 'authorized_alias_removals')),
                'delegated configuration must have no local hosts scope')
        return selected
    nodes = {}
    all_names = set()
    for node in inventory['nodes']:
        names = [name.lower() for name in [node['name'], *node['aliases'], *node.get('deprecated_aliases', [])]]
        require(len(names) == len(set(names)) and not all_names.intersection(names), 'duplicate inventory name')
        all_names.update(names)
        require(node['name'] not in nodes, 'duplicate node')
        ipaddress.ip_address(node['ip'])
        nodes[node['name']] = node
    scope = profile['hosts_scope']
    selected_nodes = scope['managed_node_names']
    require(bool(selected_nodes) and len(selected_nodes) == len(set(selected_nodes)), 'invalid node scope')
    require(set(selected_nodes) <= nodes.keys(), 'unknown node in scope')
    expected_policy = 'separate-block' if role == 'development-server' else 'omit'
    require(scope['deprecated_alias_policy'] == expected_policy, 'role alias policy mismatch')
    files = [item for item in profile['files'] if item['path'] == '/etc/hosts']
    require(len(files) == 1, 'one hosts plan required')
    item = files[0]
    before = hosts_records(item['before'] or '')
    after = hosts_records(item['after'])
    expected = {}
    deprecated = {}
    for name in selected_nodes:
        node = nodes[name]
        for alias in [name, *node['aliases']]:
            expected[alias.lower()] = str(ipaddress.ip_address(node['ip']))
        for alias in node.get('deprecated_aliases', []):
            deprecated[alias.lower()] = str(ipaddress.ip_address(node['ip']))
    outside_scope = all_names - expected.keys() - deprecated.keys()
    require(not (outside_scope.intersection(after) - before.keys()), 'new inventory name outside scope')
    for name, address in expected.items():
        values = after.get(name, [])
        local_addresses = [value for value in before.get(name, []) if ipaddress.ip_address(value).is_loopback]
        expected_values = [address, *local_addresses] if name == hostname.lower() else [address]
        require(collections.Counter(values) == collections.Counter(expected_values),
                'canonical name missing, duplicated or changed')
    begin = '# BEGIN Legacy aliases - will be deprecated'
    end = '# END Legacy aliases - will be deprecated'
    if role == 'development-server' and (deprecated or begin in item['after'] or end in item['after']):
        require(item['after'].count(begin) == item['after'].count(end) == 1, 'deprecated block missing or duplicated')
        start = item['after'].index(begin) + len(begin)
        stop = item['after'].index(end)
        require(start < stop, 'deprecated block order')
        block = hosts_records(item['after'][start:stop])
        require(set(block) == set(deprecated), 'non-deprecated name in compatibility block')
        for name, address in deprecated.items():
            require(after.get(name) == block.get(name) == [address], 'deprecated name not preserved in its block')
    if role == 'personal-device':
        require(not set(deprecated).intersection(after), 'deprecated name on personal device')
        removed = set(before).intersection(deprecated)
        require(removed <= {name.lower() for name in profile.get('authorized_alias_removals', [])}, 'personal removal not authorized')
    permitted_removals = set(deprecated) if role == 'personal-device' else set()
    for name, addresses in before.items():
        if name not in permitted_removals and name not in expected:
            require(after.get(name) == addresses, 'existing name changed or removed')
    for block in profile.get('preserved_hosts_blocks', []):
        require(bool(block) and item['after'].count(block) == 1, 'preserved block changed or duplicated')
        for name, addresses in hosts_records(block).items():
            require(name in expected and addresses == [expected[name]], 'preserved block conflicts with scope')
    if 'blocks' in scope:
        titles = set()
        assigned = []
        previous_end = -1
        protected_names = set()
        for preserved in profile.get('preserved_hosts_blocks', []):
            protected_names.update(hosts_records(preserved))
        for section in scope['blocks']:
            title = section['title']
            require(isinstance(title, str) and bool(title.strip()) and '\n' not in title and '\r' not in title,
                    'invalid block title')
            require(title not in titles and title != 'Legacy aliases - will be deprecated', 'duplicate block title')
            titles.add(title)
            ids = section['node_names']
            require(bool(ids) and set(ids) <= set(selected_nodes), 'invalid block scope')
            assigned.extend(ids)
            section_names = {alias.lower() for node_id in ids for alias in
                             [nodes[node_id]['name'], *nodes[node_id]['aliases']]} - protected_names
            begin, end = '# BEGIN ' + title, '# END ' + title
            lines = item['after'].splitlines()
            if not section_names:
                require(begin not in lines and end not in lines, 'empty canonical block')
                continue
            require(lines.count(begin) == lines.count(end) == 1, 'canonical block missing or duplicated')
            start, stop = lines.index(begin), lines.index(end)
            require(previous_end < start < stop, 'canonical block order')
            previous_end = stop
            content = lines[start + 1:stop]
            require(not any(line.startswith(('# BEGIN ', '# END ')) for line in content), 'nested canonical block')
            require(set(hosts_records('\n'.join(content))) == section_names, 'canonical block membership mismatch')
            actual_order = [alias.lower() for line in content
                            for alias in line.split('#', 1)[0].split()[1:]]
            expected_order = [alias.lower() for node_id in ids
                              for alias in [nodes[node_id]['name'], *nodes[node_id]['aliases']]
                              if alias.lower() not in protected_names]
            require(actual_order == expected_order, 'canonical node order mismatch')
        require(collections.Counter(assigned) == collections.Counter(selected_nodes), 'block assignment mismatch')
    return selected


def main():
    try:
        data = json.load(sys.stdin)
        selected = validate(data['inventory'], data['registration'], socket.gethostname(), getpass.getuser())
        owner = data['inventory']['profiles'][selected].get('configuration_owner', selected)
        print(json.dumps({'verified': True, 'configuration_owner': owner, 'applies_here': owner == selected}))
        return 0
    except (KeyError, TypeError, ValueError) as error:
        print(json.dumps({'verified': False, 'error_type': type(error).__name__}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
