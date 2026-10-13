# AGENTS.md

## Stable working principles

This section is user-owned, independent of the operational guidance below.
Upstream synchronization must preserve its meaning and position unless the user
explicitly requests a change.

### Scientific reasoning

- Before substantial work or a consequential change of direction, establish the objective, constraints, assumptions, and acceptance criteria. Inspect context before asking about a material gap; defer dependent action until it is resolved. Explain how the action serves the task.
- Each consequential step must resolve a relevant uncertainty or advance an acceptance criterion. Change the approach when it does neither.
- Distinguish observations, assumptions, hypotheses, inferences, decisions, and open questions. Support observations with conditions and results, inferences with premises, and empirical claims with discriminating checks. Narrow or retract unsupported claims. Missing or uninspected evidence establishes neither absence nor falsity.
- Explain the mechanism, constraint, or causal relationship behind a result. Keep the central unresolved question explicit. When the cause is unknown, identify the evidence that would distinguish explanations.
- Justify recommendations with criteria, tradeoffs, and material counterevidence. Apply the same criteria to alternatives, your conclusion, and the user's premises. Explain why references apply; distinguish conventions from preferences. Qualify comparisons by what was evaluated or measured.
- Reassess when evidence conflicts, progress stalls, and before concluding. For a difficult premise, use an independent sub-agent critic and evaluate its evidence; agreement is not validation. Gather missing support or state the unresolved premise, its effect on the conclusion, and how to check it.

### Communication and delivery

- Lead with the purpose and supported conclusion. Include scope, conditions, ownership, behavior, risks, and next actions when they affect the reader's decision or use; they are relevance checks, not required headings.
- Name concrete subjects, use established terms consistently, and define unfamiliar ones. Connect conditions, actions, evidence, and conclusions. Cite the smallest relevant inspected source beside the claim and explain what it establishes.
- Keep decision-critical facts and reasoning in the document. PRs, issue comments, and external or project-facing documentation need reproducible commands/code and accessible source revisions, not inaccessible local evidence. Same-environment reports and handoffs can link local files, but must carry the essential conclusions and context.
- Use short sentences and coherent bullets. Use tables for comparisons and examples or logs when useful. Let structure follow the task; do not fragment a causal explanation to shorten it.
- Minimize examples and reproductions while retaining inputs, conditions, setup, and result checks. Call a simplified procedure verified only after checking that version.
- Remove repetition, vague abstractions, background, and incidental history before material constraints or evidence. Keep earlier attempts only when needed to reproduce a result or explain a decision or risk. Progress updates report verified state, material blockers and impact, and the next action.
- Apply these principles to instructions: integrate each rule with its owner, make its trigger, action, and completion understandable, and give references a read-before-action purpose. Remove obsolete wording, duplicates, and contradictions.
- After the last edit, check the artifact and response for relevance, concision, precise meaning, and logical completeness. Check the basis and scope of claims, criticism, praise, severity, and completion. Preserve warranted confidence and useful uncertainty; avoid invented objections and ritual all-clears.

### Pull request communication

- Before a PR description, load `write-technical-pr`. Preserve its Korean Summary, self-contained evidence, reproduction, and final-state requirements. Every manuscript needs a separate agent's `humanizer` then `stop-bullshit` review and revision from supported findings.
- Review comments must explain the triggering condition, impact, and finding-specific suggestion.
- Before delivering or posting PR feedback or a description, apply `stop-bullshit` after prose editing to the artifact and your comments. Include that check in isolated reviewer prompts while preserving workflow authority and delegation boundaries.

### Code and design clarity

- Make normal and exceptional paths, state transitions, and ownership visible. Extract abstractions only for coherent responsibilities and meaningful contracts.
- Make the smallest coherent change. Reshape stale logic and remove obsolete branches, comments, debug paths, and compatibility residue.

### Build and test paths

Use configured build/test paths. Redirect caches, temporary files, artifacts, or
outputs to `/tmp` or another temporary path only with explicit user authorization.
If a required path remains unavailable after the shared-asset policy below, stop
and report the blocker.

### Workspace cleanup

- Remove completed review outputs, diagnostic scratch, and other agent-created transient artifacts. Check for abandoned instances during every `agent-update`.
- Before deletion, resolve exact targets and verify they are not repositories/worktrees, active process inputs or working directories, credentials/configuration, shared default assets, or still-needed evidence. Preserve ambiguous ownership or purpose; never use a broad home-directory glob.
- For completed experiment outputs and datasets, ask whether to retain them and state deletion is the default. Delete unless retention is requested; if there is no answer or completion is unclear, preserve and report the unresolved item.
- Report what was removed, reclaimed space, and whether recovery remains possible.

### Shared default assets

- On shared servers, use the project's configured default datasets, weights, and other shared assets.
- If access fails solely because ownership, permissions, or ACLs restrict an existing asset to one user, verify the exact shared target and fix access there. The team needs read/write access and directory traversal or file execution where required. Keep changes scoped; do not substitute a private copy or path.
- If the default path or asset is absent, stop and determine the required code, configuration, deployment, or provisioning repair before selecting or creating a substitute.

## Instruction priority

This is repo-local guidance. Explicit user instructions take precedence.

## Language

Communicate in English unless the user requests otherwise. A skill's Korean
requirement applies to its task content; final reports remain English by default.
In Korean content, retain English PR titles, section headings, established
technical terms, and all text in tables, plots, and figures, including captions.
These conventions also apply to requests for entirely Korean documents.

## External services

Prefer CLI tools or direct APIs when compatible with platform/tool requirements.
Use a plugin when required or when direct access is unavailable or inadequate.

## Execution location

Run jobs, builds, tests, benchmarks, and experiments on the session's current host
and cluster unless the user explicitly requests remote execution.

## Unexpected errors

Report unexpected errors, their current impact, recovery, and residual risk.
Include retry history only when needed to reproduce or diagnose the failure.

## Long-running experiments

For experiments expected to take tens of minutes or longer, run in local tmux on
the execution host, with named server/client windows when needed. Verify workloads
and services survive the agent session; report the host, session, and attach
command. Retain required locks and monitoring. Retrieve output periodically,
detect completion from process status, and inspect results promptly.

When a TT device experiment takes unexpectedly long, immediately read
[debugging and recovery](agent-guidance/tt-metal/debugging.md) and diagnose before
continuing to wait or retry.

## Required context, loaded only when relevant

This file is canonical for Claude and Codex. Resolve its symlink to the dotfiles
root and skill links to their real directories before resolving relative paths.
Use this checkout's `skills/<name>` for duplicate shared installations; preserve
explicit overrides and report conflicts. Read each resource before its trigger,
even when discovery fails. If unavailable, stop that action and report the path.
Load only applicable references, not every linked document.

TT-Metal guidance below is part of this AGENTS.md and must remain accessible
without a domain skill installed.

| Before this action | Required context |
| --- | --- |
| First user task in a session; explicit refresh or instruction maintenance | `skills/agent-update/SKILL.md`; retain daily refresh and CLI update policy |
| User challenges your explanation or its support; explicit self-audit | `skills/stop-bullshit/SKILL.md` |
| Create, revise, or assess a fresh-session handoff | `skills/agent-handoff/SKILL.md` |
| Write or revise technical documents such as READMEs, runbooks, or API guides; explicit plain-English or STE request | `skills/simple-english/skills/simple-english/SKILL.md`; ordinary short explanations use the communication principles above |
| Git mutation, branch/worktree changes, or PR review threads | `agent-guidance/version-control.md` |
| Hugging Face authentication or Hub work | `agent-guidance/hugging-face-auth.md` |
| Start Claude or check its authentication | `agent-guidance/claude-auth.md`; reasoning/review also needs `agent-guidance/claude-model.md` |
| Plan or start shared-server workloads, allocation, or maintenance | `agent-guidance/server-notices.md` |
| TT-Metal build, import, test, or workload; any TT device use, including unknown Guardian status; MPI or shared writable caches | `agent-guidance/tt-metal/README.md` |
| Investigate a suspected TT device anomaly through reproduction, localization, upstream checks, or submission evidence | `skills/tt-device-investigation/SKILL.md`; excludes routine correctness/performance and standalone hang recovery |
| Unexpectedly slow TT experiment; device hang, initialization, or reset failure | `agent-guidance/tt-metal/debugging.md`; basic guide before device work |
| Edit or review TT kernels/ops | `agent-guidance/tt-metal/kernels.md`; basic guide before execution |
| Plan or implement TT op/module optimization or performance tests; TTNN trace capture/replay, profiling, or measurement interpretation | `agent-guidance/tt-metal/profiling.md`; basic guide before execution |
| Interpret EvalScope speculative acceptance | `agent-guidance/tt-metal/evalscope.md` |

## Maintenance and publication scope

Human-authored review threads remain for humans to resolve. Shared TT device use
requires the applicable lock protocol. Personal harness maintenance belongs in
personal repositories and ignored entry points; tracked project changes and
publication require explicit project-scope authorization.

Maintenance/publication authority does not authorize confidential disclosure.
Keep internal audits, evaluation inputs/results, logs, and incident evidence
outside both repositories under the local agent-update state directory. Local
installation does not add a skill to the public manifest. Read `PUBLICATION.md`
before staging or publishing; it owns audience/history review, guards, and
exposure response. Suspected exposure stops publication.
