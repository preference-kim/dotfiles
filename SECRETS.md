# Private host configuration and credentials

The server inventory, the shared cluster SSH key, the Hugging Face token and the
GitHub account token live in a private repository as separate age payloads, each
with its own approval digest. Public dotfiles contains only reusable instructions,
schemas, scripts and synthetic tests. Never add actual host names, addresses, SSH
profiles, deployment targets or recipients here.

Two fleet keys give a host access: one age identity that decrypts every payload,
and one read-only deploy key for the private repository. Every development server
and trusted personal device holds the same two keys in
`~/.config/agent-update/fleet/`. Their master copy is a plain key directory in a
private cloud vault whose location the private repository records; access to that
vault is equivalent to holding the keys. A trusted host bootstraps a
new server with `scripts/bootstrap-remote <ssh-destination>`, which streams the fleet
keys over SSH, installs `age`, clones both repositories and writes the registration
at `~/.config/agent-update/private-sync.json`. Read the
[private synchronization protocol](skills/agent-update/references/private-sync.md)
before bootstrap, fetching, decryption or installation.

Every `agent-update` refresh, including a same-day refresh, fetches the approved
private inventory, synchronizes the registered owner's generated SSH include and
installs the cluster key the include uses. Missing registration is skipped; a
delegated profile reports its owner. Source review and bootstrap are requested
separately. `/etc/hosts` and its cloud-init preservation setting change only on an
explicit hosts-file request, and HF or GitHub token installation also requires its
own request. Headless servers store the GitHub token in the standard gh credential
file with mode 0600; Git uses the gh HTTPS credential helper. A shared home has one
set of keys and a shared writer lock, with hostname-specific profile selection.

Each device is explicitly registered as `development-server` or `personal-device`,
independently of OS and agent installation mode. Owning development-server
profiles retain old IP aliases in a `will be deprecated` block for shared users and
preserve operational hosts blocks. Personal devices use the approved canonical names
in hosts and SSH and register their own profile. The private profile determines node
scope as well as role.

SSH destinations and route metadata live once in the version-two inventory.
Shared option sets and network contexts generate `~/.ssh/moreh_cluster.conf`;
personal rules remain in `~/.ssh/config`, which includes that file. Profiles
select contexts instead of storing complete SSH configurations. Review every
consumer of a shared change, and keep migration plans and backups in protected
local state. See the [SSH configuration contract](skills/agent-update/references/private-ssh.md).

The protocol checks an approval digest at a pinned Git revision before applying
any payload, including an inventory plan or piping the HF payload to
`scripts/install-hf-credential`. The installer accepts the token only on stdin, uses
the installed HF library's standard credential paths, enforces mode 0600, backs up
changed credentials and verifies authentication. It does not fetch or approve
private updates.

Any host holding the fleet keys can decrypt every payload, so removing a host means
rotating both keys and re-running bootstrap on the remaining hosts. Old ciphertext
in Git history stays readable with an old identity, and recipient removal alone does
not revoke an already recovered token. This repository's own history still contains
earlier HF ciphertext and recipient files; that token has not been rotated. Discuss
token rotation and any published-history rewrite before performing either.
