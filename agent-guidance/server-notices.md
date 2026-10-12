# Server notices before development work

Before selecting shared servers or starting work on them, check the current operational notices for the affected resources.
This includes builds, tests, benchmarks, experiments, cluster allocation, resets, and server maintenance.
Reading code or editing documentation without running server workloads does not require this check.

## Find the private source

Read `~/.config/agent-update/private-sync.json` and resolve its `checkout` and `repository_url` literally.
Require the checkout's origin URL to match that registered string exactly; report a mismatch without changing the remote.
Use its existing repository authentication to fetch `origin/main`, then record the fetched commit ID.
If fetch fails, pause the affected work; a cached remote reference does not satisfy this check.
Read `server-notices.md` with `git show <commit>:server-notices.md` from that checkout.
Do not pull, switch branches, or change a dirty private checkout for this read.
The private document owns the channel location and resource-specific search guidance.
Keep channel identifiers, notice contents, and task evidence out of public dotfiles and skills.

If registration, the private document, or the notice source is unavailable, report the missing access and pause the affected server work.
Continue independent code or documentation work where possible.
Do not treat missing access or an empty search result as permission to use a resource.

## Apply current restrictions

Read recent announcements and search for older restrictions affecting the intended servers, clusters, and operation.
Read relevant thread replies and linked updates to establish scope, effective time, and whether a restriction ended or changed.
An unanswered request for an exception is not approval.
Do not infer that a restriction ended because newer messages omit it.

Follow applicable allocation limits, reservations, maintenance windows, and operating procedures before acting.
If notices conflict or applicability remains unclear, pause the dependent action and identify the unresolved condition for the user.
If history and relevant searches leave no applicable restriction or unresolved notice, proceed under the normal operating and lock rules.
Record the check time, relevant message links, and the resulting constraints in the private task context.
Do not copy a transient restriction into permanent guidance.

Check again immediately before launch if planning took time, after a substantial pause, or when the target resources change.
The daily agent-update stamp does not satisfy this check.
Notices supplement device locks and the execution-location policy; they do not authorize a move to another host or cluster.
Pass the check time, resource and operation scope, constraints, and source links to any agent performing the affected work.
That agent can reuse the check for the same scope, subject to the recheck conditions above.

Reading notices does not authorize Slack messages, host configuration changes, or changes to the approved private inventory.
Routine SSH synchronization still consumes the approved inventory under agent-update's private synchronization contract.
