# Load the private team policies

Two private documents hold team settings that public guidance must not contain.
Read the applicable one before the work it governs:

| Document | Read before | Owns |
| --- | --- | --- |
| `team-development.md` | Preparing remote experiment checkouts, TT builds, tests, device access, kernel/operation edits or reviews, and profiling decisions that depend on project conventions; recommending device recovery or reporting that recovery is blocked | Build/test conventions, device commands, reservation and recovery policy, remote checkout lifecycle, and project helper integrations |
| `writing-policy.md` | Writing or revising a PR description or another technical document; sharing a document, figure, or spreadsheet with the team | Which repositories and work it covers, their PR-description defaults, project vocabulary and reporting conventions, and hosting of shared and supplementary material |

Resolve `checkout` and `repository_url` literally from
`~/.config/agent-update/private-sync.json`; require an exact origin match.
With existing authentication, fetch `origin/main`, record its commit, and read
the document using `git show <commit>:<document>`. Do not change checkout files,
branches, or remotes, or substitute cached refs after a failed fetch. Missing
registration, access, document, or verified applicability blocks only work
dependent on that policy; independent work can continue. Report the limit.

Keep team settings out of public guidance. Apply relevant sections alongside
public API, writing, and reasoning guidance. A policy may record explicit
user-approved scopes, such as cleanup targets or figure uploads; it does not
otherwise authorize remote execution or publication. For isolated reviewers,
supply applicable sections and the source revision; leaves report missing
context without accessing unrelated private configuration. Reuse an inspected
revision within the same unchanged task scope; recheck before work after a
substantial pause or changed resources.
