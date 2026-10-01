# Private host configuration and credentials

Server inventory and the Hugging Face token live in a private repository as
separate age payloads with separate recipient lists. Public dotfiles contains
only reusable instructions, schemas and synthetic tests. Never add actual host
names, addresses, SSH profiles, deployment targets or recipients here.

Run `agent-update` on an enrolled host. Its host-local registration at
`~/.config/agent-update/private-sync.json` selects the private repository,
profile and local identities. Read the
[private synchronization protocol](skills/agent-update/references/private-sync.md)
before enrollment, fetching, decryption or installation. Each enrolled server uses its own
read-only deploy key and generates its own age identities; the initial maintainer
may retain its existing repository authentication; no personal repository
credential or another host's private key is copied. A shared home has one set of
keys and a shared writer lock, with hostname-specific profile selection.

The protocol checks an approval digest at a pinned Git revision before applying
an inventory plan or piping the HF payload to `scripts/install-hf-credential`.
The installer accepts the token only on stdin, uses the installed HF library's
standard credential paths, enforces mode 0600, backs up changed credentials and
verifies authentication. It does not fetch or approve private updates.

Public ciphertext and recipient files have been removed from the current tree.
Historical Git objects and previously copied ciphertext remain accessible. The
token has not been rotated: old recipients can still decrypt their old copy.
Discuss token rotation and any published-history rewrite before performing either.
Recipient removal alone does not revoke an already recovered token.
