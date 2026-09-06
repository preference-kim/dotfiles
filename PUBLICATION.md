# Public files and local state

`dotfiles` and its shared `skills` submodule contain reusable public instructions
and configuration. Established Moreh/TT-Metal guidance is maintained in
`AGENTS.md` and its mandatory `agent-guidance/tt-metal/` references. A new domain
skill or project-derived addition requires its own scope and disclosure review.

Internal audits, inventories, evaluation inputs and outputs, logs, and incident
evidence belong outside both Git worktrees, under
`${XDG_STATE_HOME:-$HOME/.local/state}/agent-update/`. Keep private operational
resources in their authorized project or local storage. Do not copy them into
the public skill tree for discovery. Ignore rules are a fallback, not permission
to stage a previously untracked file.

Each repository's `.publication-policy.json` lists the exact publishable files
and the preserved history preceding this policy. Adding a file requires reviewing
its content and intended audience, then adding that exact path to the policy.
Never regenerate the list from the working directory or widen it with wildcards.
Review modifications to existing files and commit messages for disclosure too.

After cloning with recursive submodules, install the local guards:

```bash
python3 scripts/publication-guard.py install
```

The installer covers dotfiles and the skills submodule, preserves existing hooks,
pins the historical base in each repository's local Git configuration, and stops
if that base changes or a custom hook directory exists. `agent-update` verifies this installation
before staging or publication. The pre-commit hook checks the staged tree. The
pre-push hook checks every commit after the preserved base, including intermediate
commits and merged ancestors. Missing policies, unreviewed paths, and local-only
paths block publication. Existing incident-specific push guards remain active.

These hooks require Git and Python 3. They are local controls and can be bypassed;
they do not classify all confidential text inside an approved file or remove
objects already served by a remote. Do not bypass them to complete a refresh.
Review the complete outgoing history, publish child submodules before parent
pointers, and keep the successful-refresh stamp unchanged while a required check
is incomplete.
