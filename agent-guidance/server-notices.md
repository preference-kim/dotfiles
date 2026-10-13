# Check server notices before work

Before selecting shared resources or planning/starting workloads, allocation,
resets, or maintenance, check current operational notices. Code reading and
documentation edits without workloads do not trigger this check.

## Read the current private source

Resolve `checkout` and `repository_url` literally from
`~/.config/agent-update/private-sync.json`. Require an exact origin URL match.
With existing repository authentication, fetch `origin/main`, record the commit,
and read `server-notices.md` using `git show <commit>:server-notices.md`.
Do not alter a dirty checkout, branch, or remote. Failed fetch cannot be replaced
by cached references. The private document owns the notice source and search
procedure; keep its identifiers, contents, and task evidence out of public files.

Missing registration, document, or source access pauses affected server work,
while independent code/documentation work can continue. An empty search alone
does not authorize a resource.

## Establish applicable restrictions

Read recent announcements and search older restrictions for the target resources
and operation. Inspect relevant replies and linked changes for scope, effective
time, and explicit ending/modification. Newer silence does not end a restriction;
a requested exception is not approval.

Apply allocation limits, reservations, maintenance windows, and procedures.
Conflicting or unclear notices pause dependent work. Proceed under normal rules
when history and relevant searches establish no applicable unresolved restriction.
Record check time, source links, and resulting constraints in private task state;
do not turn transient notices into permanent instructions.

Recheck immediately before launch after lengthy planning, a substantial pause,
or changed resources. The daily refresh stamp cannot replace this check. An
executing agent can reuse a check for the same resources and operation when given
its time, scope, constraints, and links, subject to the same recheck conditions.
Notices supplement locks and execution-location policy. Reading them authorizes
neither relocation, Slack messages, host changes, nor inventory edits. Routine SSH
still consumes only the approved inventory under agent-update.
