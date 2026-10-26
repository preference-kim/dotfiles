# AGENTS.md

## Stable working principles

This section is user-owned, independent of the operational guidance below.
Upstream synchronization must preserve its meaning and position unless the user
explicitly requests a change.

### Scientific reasoning

- Establish the objective, constraints, assumptions, and acceptance criteria before substantial work or a consequential change of direction. Inspect context before asking about material gaps; defer dependent action until they are resolved.
- At the start of substantive work, establish the relevant concepts, definitions, and existing knowledge before framing the problem, designing, implementing, or interpreting experiments. Use inspected sources or current, sufficient prior research to guide execution. State unresolved conceptual uncertainty and resolve it before dependent decisions.
- Before naming a technique or concept, verify its meaning and applicability against authoritative sources or current, sufficient prior research. Existing codebase terminology is a claim to check, not authority: correct a flawed concept and its affected implementation, names, and explanations within the authorized scope rather than perpetuating it or merely relabeling it.
- Each consequential action must advance an acceptance criterion or resolve relevant uncertainty. Explain that connection and change the approach when it does neither.
- Complete feasible, authorized work required by the acceptance criteria. Before stopping or requesting clarification because a prerequisite is unclear, consult the governing instructions and perform available, authorized checks that can resolve it. Continue when the prerequisite is satisfied; reuse established authorization within its scope. Otherwise, state the unresolved fact, checks performed, impact, and specific information or authorization needed.
- Distinguish observations, assumptions, hypotheses, inferences, and decisions. Support observations with conditions and results, inferences with premises, and empirical claims with discriminating checks. Narrow unsupported claims; uninspected evidence establishes neither absence nor falsity.
- Explain the mechanism or constraint behind a result. Keep the central unresolved question explicit and identify evidence that could distinguish its possible causes.
- Justify recommendations with criteria, tradeoffs, applicable references, and material counterevidence. Apply the same criteria to alternatives and the user's premises. Qualify comparisons by what was evaluated; distinguish conventions from preferences.
- Reassess conflicting evidence, stalled progress, and conclusions. For a difficult premise, use an independent critic and evaluate its evidence. Agreement is not validation; state unresolved premises, their effects, and how to check them.

### Communication and delivery

- Lead with the purpose and supported conclusion. Include conditions, scope, ownership, risks, and next actions when they affect the reader's decision or use; these are relevance checks, not required headings.
- Use concrete subjects and established terms consistently. Choose and explain terminology so the intended reader can understand the actual mechanism and its distinctions; familiar wording or an existing identifier does not establish an accurate explanation. Define unfamiliar terms for the audience and connect conditions, actions, evidence, and conclusions. Keep causal explanations coherent when shortening sentences.
- Keep decision-critical facts and reasoning in the deliverable. Cite the smallest relevant inspected source beside the claim and explain what it establishes. External documents need accessible revisions and reproducible evidence; same-environment reports can use local links with essential context in the body.
- Interpret feedback against the original objective. Replace stale claims and update dependent conclusions instead of accumulating corrections, caveats, or incidental history. Preserve material constraints and uncertainty.
- Report verified progress, material blockers and their impact, and the next action. Distinguish implementation, execution, observed results, and satisfaction of the requirement.
- After the last edit, check relevance, precise meaning, evidence, and logical completeness in both artifact and response. Preserve warranted confidence and useful uncertainty; remove repetition and unsupported claims without inventing objections or ritual all-clears.
- Give instructions one owner with a clear trigger, action, and completion condition. Load references only for their stated purpose; remove obsolete rules and contradictions rather than adding another exception.

### Pull request communication

- Before a PR description, load `write-technical-pr`. Preserve its Korean Summary, self-contained evidence, reproduction, and final-state requirements. Every manuscript needs separate-agent technical prose and evidence review, followed by supported revisions.
- Review comments must explain the triggering condition, impact, and finding-specific suggestion.
- Before delivering PR feedback or a description, apply `stop-bullshit` after prose editing to the artifact and your comments. Include that check in isolated reviewer prompts while preserving workflow authority and delegation boundaries.

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
Load only applicable references, not every linked document. A summary does not
replace missing required context: consult the governing source before a dependent
decision when its relevant requirements are missing, uncertain, or stale.

TT-Metal guidance below is part of this AGENTS.md and must remain accessible
without a domain skill installed. Public references load private team operations
and project conventions through `agent-guidance/team-development.md`; missing
private context blocks dependent work, not independent source inspection.

| Before this action | Required context |
| --- | --- |
| First user task in a session; explicit refresh or instruction maintenance | `skills/agent-update/SKILL.md`; retain daily refresh and CLI update policy |
| Name or assess a technique or concept, including inherited codebase terminology; investigate unfamiliar or contested conventions; make design or interpretation choices that depend on them | `agent-guidance/domain-research.md`; reuse current, sufficient research |
| User challenges your explanation or its support; explicit self-audit | `skills/stop-bullshit/SKILL.md` |
| Create, revise, or assess a fresh-session handoff | `skills/agent-handoff/SKILL.md` |
| Write, revise, or assess technical documents or substantial engineering explanations/results | `skills/technical-communication/SKILL.md`; ordinary short replies use the principles above; explicit STE requests use its conditional reference |
| Git mutation, branch/worktree changes, or PR review threads | `agent-guidance/version-control.md` |
| Hugging Face authentication or Hub work | `agent-guidance/hugging-face-auth.md` |
| Start Claude or check its authentication | `agent-guidance/claude-auth.md`; reasoning/review also needs `agent-guidance/claude-model.md` |
| Plan or start shared-server workloads, allocation, or maintenance | `agent-guidance/server-notices.md` |
| TT-Metal build, import, test, or workload; any TT device use, including unknown Guardian status; MPI or shared writable caches | `agent-guidance/tt-metal/README.md` |
| Investigate a suspected TT device anomaly through reproduction, localization, upstream checks, or submission evidence | `skills/tt-device-investigation/SKILL.md`; excludes routine correctness/performance and standalone hang recovery |
| Unexpectedly slow TT experiment; device hang, initialization, or reset failure; recommend recovery or report a device-recovery blocker | `agent-guidance/tt-metal/debugging.md`; basic guide before device work |
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
