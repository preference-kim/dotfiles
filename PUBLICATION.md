# Publication boundary

Dotfiles and its shared skills contain reusable public instructions and
configuration. Established Moreh/TT-Metal guidance remains in `AGENTS.md` and
`agent-guidance/tt-metal/`. New domain skills and project-derived additions need
separate scope and disclosure review. Personal ownership, private repository
visibility, and maintenance authority do not authorize confidential disclosure.

Before staging or publishing, verify the destination audience and releasability
of files, the full outgoing history, commit messages, and PR content. Internal
audits, inventories, evaluation inputs/results, logs, and incident evidence belong
outside both worktrees under `${XDG_STATE_HOME:-$HOME/.local/state}/agent-update/`.
Keep private operational resources in authorized project/local storage. Local
installation and ignore rules do not authorize adding them to the public manifest.

For suspected exposure, stop publication and preserve necessary evidence locally.
Keep remediation within authorized scope; repository visibility changes,
published-history rewrites, and remote deletion need explicit authorization.
Distinguish local cleanup from verified removal of remotely served objects.

## Guards and completion

Each repository's `.publication-policy.json` lists exact publishable paths and a
preserved historical base. Review a new file's content and audience before adding
its exact path. Do not generate the list from the worktree or widen it with globs.
Approved paths still require content review.

After a recursive clone, install and verify the guards before staging:

```bash
python3 scripts/publication-guard.py install
```

The installer covers dotfiles and skills, preserves hooks, and pins each base in
local Git configuration. A changed base or custom hook directory blocks install.
Pre-commit checks the staged tree; pre-push checks every commit after the base,
including intermediate commits and merged ancestors. Missing policies, unreviewed
paths, and local-only paths block publication. Existing incident guards remain.

These Git/Python 3 hooks neither classify all confidential content nor remove
remote objects. Do not bypass them. Publish child submodules before parent
pointers. Keep the successful-refresh stamp unchanged until all required checks
pass; `skills/agent-update/references/publication.md` owns that completion gate.
