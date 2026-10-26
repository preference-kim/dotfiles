# Load the private team development policy

Read before preparing remote experiment checkouts, TT builds, tests, device
access, kernel/operation edits or reviews, and profiling decisions that depend
on project conventions. Also read before recommending device recovery or
reporting that recovery is blocked; these judgments depend on the same policy.

Resolve `checkout` and `repository_url` literally from
`~/.config/agent-update/private-sync.json`; require an exact origin match.
With existing authentication, fetch `origin/main`, record its commit, and read
`team-development.md` using `git show <commit>:team-development.md`. Do not change
checkout files, branches, or remotes, or substitute cached refs after a failed
fetch. Missing registration, access, document, or verified applicability blocks
only work dependent on that policy; independent source inspection can continue.

The private document owns team-specific build/test conventions, device commands,
reservation and recovery policy, remote checkout lifecycle, and project helper
integrations. Keep those settings out of public guidance. Apply relevant sections
alongside public API
and reasoning guidance. The policy may record explicit user-approved cleanup
scopes; it does not independently authorize remote execution or publication.
For isolated reviewers, supply applicable sections and the source revision;
leaves report missing context without accessing unrelated private configuration.
Reuse an inspected revision within the same unchanged task scope; recheck before
work after a substantial pause or changed resources.
