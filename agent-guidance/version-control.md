## Git workflow

The project workflow below applies to authorized project contributions. Personal
harness maintenance targets the personal dotfiles and skills repositories; a
project-local discovery path does not authorize tracked project changes, commits,
pushes, or PRs. Keep its installation in ignored local links and metadata unless
the user explicitly requests a project contribution.

Never push directly to main branches such as `main`, `master`, `moreh/main`, or `origin/moreh/main`. Always create a feature branch and open a pull request for review. If a user asks to push work and the current branch is a main branch, stop and create/switch to a non-main branch before pushing.

Exception: authorized, disclosure-reviewed agent-instruction updates in the personal dotfiles and shared skills repositories use `main` directly, without a feature branch or PR. This selects a branch; it does not authorize publication. Verify the destination audience and inspect the full outgoing diff and history, including commit messages and PR text. Internal project content and maintenance evidence stay local and untracked unless disclosure to that specific audience is explicitly authorized. Stop publication during a suspected exposure; visibility changes, published-history rewrites, and remote deletion require approval.

When creating a feature branch, use the `sunho/` prefix by default unless the user explicitly requests a different branch name.

When addressing feedback on a pull request you own, never resolve a review thread whose root comment was authored by another person. You may resolve a thread only when its root comment was authored by Copilot or another automated agent, and only after its concern has been addressed and pushed. Human-authored threads must remain open for a person to resolve, even when you implement the requested change.

## Worktree use

Use the repository's primary checkout by default. Use `git worktree` only for
static code analysis or documentation work at a specific HEAD. Never create an
ad hoc worktree for builds or device-backed tests; perform that work only in
the current session checkout.

If the primary checkout is dirty, do not create a worktree to avoid it.
Preserve the existing changes first: either stash them, including relevant
untracked files, or commit and push them to an appropriate branch, following
the repository's Git rules. Never discard or overwrite existing work. If the
dirty changes are the task's intended input, handle them there rather than
stashing them away. Restore stashed changes when the task is complete and it is
safe to do so; report any restoration conflict.

If existing changes prevent a required branch checkout, commit them locally or
stash them before checking out the branch.

- When making a git commit, never co-author.
