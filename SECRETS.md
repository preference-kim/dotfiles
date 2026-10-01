# Private host configuration and credentials

Server inventory, the Hugging Face token and an optionally enrolled GitHub account
token live in a private repository as separate age payloads and recipient lists. Public dotfiles contains
only reusable instructions, schemas and synthetic tests. Never add actual host
names, addresses, SSH profiles, deployment targets or recipients here.

Explicitly ask `agent-update` to update server configuration. An owning profile
reviews source server-list changes and updates the current host's `/etc/hosts`
and SSH configuration through an approved private inventory revision. A delegated
profile reports its configuration owner and preserves local files. Enrolled credential
synchronization is requested separately. A generic `agent-update` request and
daily refreshes update agent files and tools without fetching, decrypting or
applying private payloads. Source review alone does not deploy changes.
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
A second personal computer gets its own profile, baseline, routes and local key
paths; it does not copy the controller's registration. Inventory-only setup does
not enroll account credentials. The private profile determines node scope as well
as role, and explicit synchronization remains required after setup.

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
