# Private host configuration and credentials

Server inventory, the Hugging Face token and an optionally enrolled GitHub account
token live in a private repository as separate age payloads and recipient lists. Public dotfiles contains
only reusable instructions, schemas and synthetic tests. Never add actual host
names, addresses, SSH profiles, deployment targets or recipients here.

Every `agent-update` refresh, including a same-day refresh, fetches the approved
private inventory and synchronizes the current enrolled owner's generated SSH
include. Missing registration is skipped; a delegated profile reports its owner.
Source review and enrollment are requested separately. `/etc/hosts` and its
cloud-init preservation setting change only on an explicit hosts-file request;
credential synchronization also requires its own request. Source review alone
does not deploy changes. Login and `clear` use local files without synchronization.
The host-local registration at
`~/.config/agent-update/private-sync.json` selects the private repository,
profile and local identities. Read the
[private synchronization protocol](skills/agent-update/references/private-sync.md)
before enrollment, fetching, decryption or installation. Each enrolled server uses a read-only repository deploy key and separate age
identities for inventory and HF. An explicitly authorized credential group may
share those three service keys across its members. The initial maintainer may
retain its existing repository authentication. GitHub account access may also be explicitly enrolled with a separately encrypted
and approved token. Headless servers store it in the standard gh credential file
with mode 0600; the account and target authorization remain private. Its age
identity may be shared with HF only for members authorized for both payloads.
Git uses the gh HTTPS credential helper; SSH remotes keep their existing policy.
A shared home has one set of keys and a shared writer lock, with hostname-specific
profile selection.

Each device is explicitly registered as `development-server` or `personal-device`,
independently of OS and agent installation mode. Owning development-server
profiles retain old IP aliases in a `will be deprecated` block for shared users and preserve operational
hosts blocks. Personal devices use the approved canonical names in hosts and SSH.
A second personal computer gets its own registration and selects a shared SSH
context with its existing local key paths. It does not copy the controller's
registration or duplicate its SSH file. Inventory-only setup does
not enroll account credentials. The private profile determines node scope as well
as role. After SSH setup, agent refreshes apply reviewed changes automatically;
hosts-file and credential writes retain their explicit-request requirement.

SSH destinations and route metadata live once in the version-two inventory.
Shared option sets and network contexts generate `~/.ssh/moreh_cluster.conf`;
personal rules remain in `~/.ssh/config`, which includes that file. Profiles
select contexts instead of storing complete SSH configurations. Review every
consumer of a shared change, and keep migration plans and backups in protected
local state. See the [SSH configuration contract](skills/agent-update/references/private-ssh.md).

The protocol checks an approval digest at a pinned Git revision before applying
any enrolled payload, including an inventory plan or piping the HF payload to `scripts/install-hf-credential`.
The installer accepts the token only on stdin, uses the installed HF library's
standard credential paths, enforces mode 0600, backs up changed credentials and
verifies authentication. It does not fetch or approve private updates.

Public ciphertext and recipient files have been removed from the current tree.
Historical Git objects and previously copied ciphertext remain accessible. The
token has not been rotated: old recipients can still decrypt their old copy.
Discuss token rotation and any published-history rewrite before performing either.
Recipient removal alone does not revoke an already recovered token.
