# dotfiles

Personal development configuration and shared agent instructions for Claude and
Codex. This repository maintains one canonical `AGENTS.md`, operational guidance
for Moreh/TT-Metal work, and a shared skills submodule, alongside shell, tmux,
Ubuntu setup, and credential-management resources.

## Repository layout

| Path | Purpose |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Stable working principles and triggers for loading task-specific guidance. |
| [agent-guidance/](agent-guidance/) | Conditional guidance for Git, authentication, and Moreh/TT-Metal development. |
| [skills/](https://github.com/preference-kim/my-claude-skills) | Shared skills from `preference-kim/my-claude-skills`, including `agent-update` and `stop-bullshit`. |
| [agent-file-sync.example.yaml](agent-file-sync.example.yaml) | Template for choosing where each host exposes instructions and skills. |
| [bash/bashrc](bash/bashrc), [zsh/interactive.zsh](zsh/interactive.zsh), [git/config](git/config), [.tmux.conf](.tmux.conf) | Shell, Git and tmux settings that `agent-update` links into each host. |
| [macos/](macos/README.md) | Pinned D2Coding installation and VS Code/iTerm2 font settings. |
| [ubuntu/](ubuntu/README.md) | Ubuntu desktop setup notes and scripts. |
| [scripts/](scripts/), [SECRETS.md](SECRETS.md) | Server bootstrap, publication guards, credential helpers, and VPN service scripts. |
| [PUBLICATION.md](PUBLICATION.md) | Public-content boundaries and Git publication controls. |

`CLAUDE.md`, `.claude/CLAUDE.md`, and `.codex/AGENTS.md` are symlinks to the root
`AGENTS.md`. Edit the canonical file; both tools use the same guidance.

## Set up shared agent instructions

Git and Python 3 are required for the commands below. All submodules use public
HTTPS URLs, so no GitHub key is needed to clone. Maintainers who push over SSH can
set `remote.origin.pushurl` in their own checkouts.

```bash
git clone --recurse-submodules https://github.com/preference-kim/dotfiles.git
cd dotfiles
python3 scripts/publication-guard.py install
cp -n agent-file-sync.example.yaml agent-file-sync.local.yaml
```

Edit the ignored `agent-file-sync.local.yaml` for this host:

| Mode | Instruction and skill discovery |
| --- | --- |
| `host-global` | Global instruction links; user-scope skills at `~/.agents/skills` (Codex) and `~/.claude/skills` (Claude). Project-only skills are excluded. |
| `moreh-dev` | The same user-scope skills globally; project instructions and project-only skills under the configured checkout’s `.agents/skills` and `.claude/skills`. |

For `moreh-dev`, set `moreh_dev_root` to an existing Git checkout. Relative paths
are resolved from this repository; absolute paths are used as written. The
updater requires a valid mode and preserves independent local or project-owned
skills. An invalid project root blocks project installation while user-scope
skills can still install; the refresh is not marked successful.

The shared `.installation-policy.json` assigns every approved skill to `user`
or `moreh-dev`, independently of publication approval. Individual symlinks point
to canonical sources; resolve those sources before reading relative references.

Ask Claude or Codex to read and follow
[skills/agent-update/SKILL.md](https://github.com/preference-kim/my-claude-skills/blob/main/agent-update/SKILL.md) from this checkout.
This explicit path also works before the skill has been installed for discovery.
`agent-update` maintains the configured links and verifies the complete shared
skill manifest. Development-checkout links remain ignored local installation
metadata. See the [installation rules](https://github.com/preference-kim/my-claude-skills/blob/main/agent-update/references/installation.md)
for exact paths and conflict handling.

## Bootstrap a development server

Set up a new server from a trusted host that already holds the fleet keys, such as
a personal computer where `agent-update` has completed. The trusted host must reach
the server with key-based SSH as your account, and the server needs `git`, `python3`,
`tar`, `gzip`, `sha256sum`, an SSH client and access to github.com.

```bash
scripts/bootstrap-remote <ssh-destination>
```

The script copies the fleet keys, installs `age`, clones this repository and the
private configuration repository, and registers the host. Then ask the agent on the
trusted host to run `agent-update` for that server: it adds the server's inventory
profile if needed and installs the skills, shell and Git settings, SSH configuration
and cluster key. See [SECRETS.md](SECRETS.md) for the key model.

## Use and maintain the repository

Edit working principles in [AGENTS.md](AGENTS.md). Keep detailed Moreh/TT-Metal
procedures in [agent-guidance/tt-metal/](agent-guidance/tt-metal/) with explicit
loading triggers in `AGENTS.md`. Reusable task workflows belong in the existing
shared skill that owns them; see the [skill index](https://github.com/preference-kim/my-claude-skills#skills).

`agent-update` links the shell, Git and tmux settings additively and keeps personal
lines in your own startup files. `ubuntu/setup_ubuntu.sh` performs desktop package
changes; review it before running it on a host.
Follow [SECRETS.md](SECRETS.md) for the encrypted Hugging Face credential workflow.

Before committing, follow [PUBLICATION.md](PUBLICATION.md). Each repository has
an explicit file allowlist; adding a public file requires reviewing its content
and audience, then adding its exact path to `.publication-policy.json`. Review
edits to already-approved files as well. Publish changed submodules before
committing their pointers in the parent repository.

Keep host configuration in the ignored local YAML file. Keep internal audits,
evaluation data, logs, and incident evidence outside both repositories under
`${XDG_STATE_HOME:-$HOME/.local/state}/agent-update/`. The local Git guards check
staged files and outgoing history, but cannot determine whether every passage
inside an approved file is suitable for public disclosure.

Private server configuration and enrolled credentials synchronize through
`agent-update` only when explicitly requested for that scope. Daily refreshes and
a generic `agent-update` request do not fetch or apply private payloads. See
[secret management](SECRETS.md) for enrollment and the separate source-review and
approved-deployment workflow.
