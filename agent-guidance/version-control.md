# Git workflow

Personal harness maintenance targets personal repositories and ignored local
entry points. Project discovery does not authorize tracked project changes or
publication; obtain explicit project-scope authority. Before staging or publishing
personal changes, read [PUBLICATION.md](../PUBLICATION.md).
Disclosure-reviewed instruction updates in dotfiles and shared skills use `main`
directly, without a PR. This selects the branch, not publication authority.

For project feature branches, use `sunho/` unless the user or higher-priority
instructions specify another name. Never add co-author trailers.

## Worktrees and existing changes

Use the primary checkout. Worktrees are limited to static analysis or documentation
at a specific HEAD; builds and device tests stay in the current session checkout.
A dirty checkout is not a reason to create a worktree. Before preparing a remote
experiment checkout, read [the private team policy](team-development.md) for
applicable lifecycle rules and scoped standing authorization. Discard or overwrite
existing work only within an explicit user-authorized scope. Before destructive
cleanup, verify exclusive checkout use and preserve active inputs; unresolved
ownership or a live workload consuming affected files blocks cleanup.

By default, preserve existing work: handle task-input changes in place, otherwise
stash relevant tracked/untracked files or commit and push on an appropriate branch
under the repository's rules. Before a blocked branch switch outside an authorized
cleanup scope, commit locally or stash. Restore stashes when safe at task completion
and report restoration conflicts.

## Rebases

After rebasing onto a base that absorbed other changes, re-review every conflict
resolution and every auto-merged hunk against the intent of the upstream changes
it absorbed. A clean merge does not establish semantic compatibility. Adapt to the
new upstream design rather than working around it, and check whether the branch
should adopt conventions the upstream introduced. Report a conflict between that
design and the branch's own layering to the user before changing either.

## Pull requests

Resolve a review thread only if its root author is an automated agent and the
concern is addressed and pushed. Leave human-authored roots open for a person,
even after implementing the requested change.

Before creating or updating a PR, inspect its full intended diff for unnecessary
environment settings in code, launch scripts, configuration, and documentation.
Remove temporary experiment/debug variables with their readers, exports, fallback
branches, and instructions. Expose only necessary variables defined by external
packages, verified against the installed version. Validate affected behavior
without the removed settings.
