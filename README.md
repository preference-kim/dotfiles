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
| [zsh/interactive.zsh](zsh/interactive.zsh), [.tmux.conf](.tmux.conf) | Interactive shell and tmux configuration. |
| [ubuntu/](ubuntu/README.md), [git.conf.sh](git.conf.sh) | Ubuntu setup notes and scripts, and personal Git defaults. |
| [scripts/](scripts/), [SECRETS.md](SECRETS.md) | Publication guards, credential helpers, and VPN service scripts. |
| [PUBLICATION.md](PUBLICATION.md) | Public-content boundaries and Git publication controls. |

`CLAUDE.md`, `.claude/CLAUDE.md`, and `.codex/AGENTS.md` are symlinks to the root
`AGENTS.md`. Edit the canonical file; both tools use the same guidance.

## Set up shared agent instructions

Git, Python 3, and GitHub SSH access are required for the commands below. The
`skills` and `stop-bullshit` submodules use SSH URLs.

```bash
git clone --recurse-submodules git@github.com:preference-kim/dotfiles.git
cd dotfiles
python3 scripts/publication-guard.py install
cp -n agent-file-sync.example.yaml agent-file-sync.local.yaml
```

Edit the ignored `agent-file-sync.local.yaml` for this host:

| Mode | Instruction and skill discovery |
| --- | --- |
| `host-global` | Instruction links under `~/.codex` and `~/.claude`, with individual shared-skill links in each tool's `skills` directory. |
| `moreh-dev` | Instruction links at the configured development checkout's root, with individual skill links under its `.codex/skills` and `.claude/skills` directories. |

For `moreh-dev`, set `moreh_dev_root` to an existing Git checkout. Relative paths
are resolved from this repository; absolute paths are used as written. The
updater requires a valid configuration and preserves independent local or
project-owned skills.

Ask Claude or Codex to read and follow
[skills/agent-update/SKILL.md](https://github.com/preference-kim/my-claude-skills/blob/main/agent-update/SKILL.md) from this checkout.
This explicit path also works before the skill has been installed for discovery.
`agent-update` maintains the configured links and verifies the complete shared
skill manifest. Development-checkout links remain ignored local installation
metadata. See the [installation rules](https://github.com/preference-kim/my-claude-skills/blob/main/agent-update/references/installation.md)
for exact paths and conflict handling.

## Use and maintain the repository

Edit working principles in [AGENTS.md](AGENTS.md). Keep detailed Moreh/TT-Metal
procedures in [agent-guidance/tt-metal/](agent-guidance/tt-metal/) with explicit
loading triggers in `AGENTS.md`. Reusable task workflows belong in the existing
shared skill that owns them; see the [skill index](https://github.com/preference-kim/my-claude-skills#skills).

Shell, tmux, Git, and Ubuntu setup are separate from agent installation. Review
the relevant files before applying them to a host: `git.conf.sh` sets personal
global Git values, and `ubuntu/setup_ubuntu.sh` performs system package changes.
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
