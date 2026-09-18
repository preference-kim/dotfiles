# AGENTS.md

## Stable working principles

This section is user-owned and independent of the Moreh operational guidance below. Upstream synchronization may update the operational guidance, but must preserve the meaning and position of this section unless the user explicitly requests a change.

### Scientific reasoning

- Before substantial work or a consequential change of direction, establish the objective, constraints, assumptions, and acceptance criteria. Inspect available context before asking about a material gap; defer dependent action while that gap remains. Be able to explain how the proposed action serves the task.
- Each consequential step must resolve a relevant uncertainty or advance an acceptance criterion. Revise the approach when it does neither.
- Distinguish observations, assumptions, hypotheses, inferences, decisions, and open questions. Match support to the claim: observations need conditions and results; inferences need premises; empirical claims need a discriminating check. Narrow or retract unsupported claims rather than soften them with vague hedging. Missing or uninspected evidence does not establish absence or falsity.
- Explain the mechanism, constraint, or causal relationship behind a result. Keep the central unresolved question explicit. When the cause is unknown, identify the evidence needed to distinguish plausible explanations instead of supplying a convenient one.
- Justify recommendations with explicit criteria and tradeoffs. Apply the same criteria to alternatives, the preferred conclusion, and the user's premises; include material counterevidence. Explain what references establish and why they apply. Distinguish established conventions from preferences; authority alone is not an argument. Qualify comparisons such as "better" or "faster" by what is evaluated or measured.
- Reassess the argument when evidence conflicts or progress stalls, and before finalizing a conclusion. If a specific premise is difficult to assess, use an independent sub-agent critic and evaluate its findings against evidence; agreement is not validation. Do not finalize a claim you cannot explain. Gather the missing support or state which unresolved premise limits the conclusion and how it can be checked.

### Communication and delivery

- Write for the reader's decision or next action. Lead with the purpose and current supported conclusion. Include scope, preconditions, invariants, ownership, behavior, failure modes, risks, and next actions only where they affect understanding, evaluation, or use; these are relevance checks, not mandatory headings.
- Identify concrete subjects and explain their relationships. Use established terms consistently and define unfamiliar ones before relying on them. Connect the relevant conditions, actions, evidence, and conclusions without unstated logical jumps. When citing sources, point to the smallest relevant inspected code, passage, or result beside the claim it supports; a name, link, or vague paraphrase does not supply an explanation.
- Put decision-critical facts and explanations in the document. References provide supporting detail and verification without making the reader reconstruct the argument. In PRs, issue comments, and external or project-facing documentation, never cite inaccessible local files, paths, logs, or artifacts as evidence. Provide material facts, reproducible commands or code, and accessible source revisions instead. Direct session reports and same-environment handoffs may link local files accessible to their recipients, but must still carry the essential context and conclusions.
- Use short sentences and focused bullets. Keep each point coherent; do not fragment a causal explanation merely to shorten it. Use tables for comparisons, and include commands, examples, or log excerpts when they support the reader's task. Let structure follow purpose and applicable task requirements rather than imposing one outline on every document.
- Keep examples and reproduction procedures as small as the relevant behavior allows. Preserve the inputs, conditions, required setup, and checks that establish or detect the result; remove unrelated variables, wrappers, and logic. Do not present a simplified procedure as verified unless that version was checked.
- Remove repetition, vague abstractions, generic background, and incidental history before removing material constraints or evidence. Include earlier attempts only when needed to reproduce a result or explain a current decision or risk. Keep progress updates to verified state, a material blocker and its impact, and the next action; omit repetitive closing summaries.
- Apply these principles to instruction documents too. Integrate new information into its owning section instead of appending reminders. Make each rule's applicability, required action, and compliance criterion understandable without forcing them into separate fields. Give conditional references a clear purpose and read-before-action trigger; remove obsolete wording, duplication, and contradictions.
- After the last edit, check the artifact and accompanying response for relevance, concision, precise meaning, and logical completeness. Verify the basis and scope of material conclusions, criticism, praise, severity, and completion claims. Preserve warranted confidence and useful uncertainty; do not manufacture objections or announce a ritual all-clear.

### Pull request communication

- Before creating or revising a PR description, load `write-technical-pr`; its policy preserves the Korean Summary, self-contained evidence, reproduction, and final-state requirements. Every manuscript must be reviewed by a separate agent using `humanizer` and then `stop-bullshit`, revised from the supported findings, and finalized after that pass.
- Apply the communication structure above to each PR review comment, including the triggering conditions and impact. Keep the explanation and suggestions specific to the finding.
- Before delivering or posting PR feedback or a PR description, load `stop-bullshit` and apply its final check after prose editing. Check the reviewed material and the review comments themselves. Copy the check into isolated reviewer prompts; preserve each workflow's write and delegation boundaries.

### Code and design clarity

- Prefer direct, readable control flow that makes the normal path, exceptional path, state transitions, and ownership visible.
- Use the minimum abstraction needed to express stable responsibilities. Extract a unit only when it has a coherent role and meaningful contract; do not create helpers or layers solely to shorten local code.
- Design, do not accumulate. Make the smallest coherent change, reshape stale logic when its assumptions no longer hold, and remove obsolete branches, comments, debug paths, and compatibility residue that no longer serve the production design.

### Build and test paths

- During builds and tests, do not redirect caches, temporary files, artifacts, outputs, or related state to `/tmp` or another temporary path unless the user explicitly authorizes that redirection.
- If a required build or test path remains unavailable or unwritable after applying the shared-default-asset policy below, stop and report the blocker instead of substituting a temporary path.

### Workspace cleanup

- Treat review outputs, temporary directories, diagnostic scratch, and other agent-created transient artifacts as ephemeral. Remove them when their task is complete, and inspect for abandoned instances during every `agent-update` run.
- Before deleting anything, resolve each exact target and verify that it is not a Git repository or worktree, an active process's working directory or input, a credential or configuration directory, a shared default asset, or evidence still needed to reproduce a current conclusion. Never use a broad home-directory glob or delete data whose ownership or purpose is ambiguous.
- Treat experiment outputs and datasets as disposable once the session no longer needs them. Ask the user whether completed experiment data should be retained, state that deletion is the default, and delete it unless the user requests retention. If the user does not answer or the completed scope is unclear, preserve the data and report the unresolved cleanup item.
- After cleanup, report what was removed, the reclaimed space, and whether recovery remains possible.

### Shared default assets

- On shared servers, use the project's configured default paths for datasets, model weights, and other shared assets when those paths exist.
- If an asset exists at its default path but access fails only because its ownership, mode bits, or ACLs restrict it to a particular user, verify the exact shared target and fix its ownership or permissions before continuing. The team must be able to read and write the asset and to traverse directories or execute files where required. Keep the change scoped to the intended shared asset; do not bypass it with a user-private copy or an alternate path.
- If the configured default path or required asset is absent, treat that as an unintended code, configuration, deployment, or provisioning condition. Stop and determine whether the default path or asset provisioning must be fixed instead of silently creating or selecting a substitute path.

## TT-Metal development

The maintained [TT-Metal guidance](agent-guidance/tt-metal/README.md) is part of
this AGENTS.md and must remain available without a domain skill installed. It
covers the active checkout's environment, builds, shared device locking, resets,
and MPI/shared-cache setup. The required-context table below routes basic work
there and specialized work to the deeper references in `agent-guidance/tt-metal/`.

## Instruction priority

Treat this AGENTS.md as repo-local guidance. Explicit user instructions for the current task always take precedence over these defaults.

## Language

Use English by default for communication. Follow an applicable skill's Korean-language requirements for the task content it governs; those requirements are exceptions to the English default and do not require a separate user request. Final explanations and reports to the user remain in English by default, even when the task content is in Korean. Follow explicit user language instructions for the scope they specify, subject to the conventions below.

When a document is requested in Korean, use Korean for explanatory prose, but
keep the following in English even if the request says "entirely in Korean":

- PR titles and section headings.
- Established concepts, terminology, and technical terms whose conventional form
  in academia or industry is English.
- Text in tables, plots, figures, and similar visual elements, including headers,
  cells, labels, legends, and captions.

Apply these conventions to skill-required Korean content as well. Preserve
standard English terminology within Korean prose instead of translating it.

## External services

When compatible with the applicable platform and tool instructions, prefer command-line tools, direct APIs, or another programmatic approach over installing or requesting a plugin for services such as Slack or GitHub. Use a plugin when the platform requires it or the direct approaches are unavailable or clearly inadequate.

## Execution location

Unless the user explicitly requests remote execution, run builds, tests, benchmarks, experiments, and other jobs on the host and cluster where the session is already running. Do not use SSH or another remote connection to move a job elsewhere. For example, from `ttdev31`, run the job on `ttdev31`, not `ttdev32`; from AI cluster 1, stay on AI cluster 1 rather than using AI cluster 2.

## Unexpected errors

Never silently omit an unexpected error. Report it in terms of its current impact, recovery, and residual risk; omit command-by-command retry chronology unless it is needed to reproduce or diagnose the problem.

## Long-running experiments

For experiments expected to take tens of minutes or longer, create a local tmux session on the execution host and enter the execution commands in its windows. Use separate named windows for the server and client when both are needed. Verify that the workload and its required services run under tmux independently of the Codex session, and report the host, session name, and attach command. Keep the applicable device locks and monitoring in place.

Stream or periodically retrieve output while a long-running process runs. Detect completion through process status rather than estimated sleeps or log-following alone, and check the result promptly after exit.

If a TT device experiment takes unexpectedly long, immediately read
[device debugging and recovery](agent-guidance/tt-metal/debugging.md) and follow
its tt-triage and hang-detection procedure before continuing to wait or retry.

## Required context, loaded only when relevant

This is the canonical shared guidance for Claude and Codex. Resolve this file's
symlink to the dotfiles root before resolving the relative paths below. Resolve
skill references from the real skill directory, not the tool-specific entry point.
Read each required resource before the triggering action, even if skill discovery
fails; use the explicit path. If unavailable, stop that action and report the path.
For shared skills, use this dotfiles checkout's `skills/<name>` as the canonical
source when duplicate user installations are visible; preserve explicitly requested
overrides and report conflicts. Do not load unrelated references or recursively read
every linked document.

| Before this action | Required context |
| --- | --- |
| First user task in a new session, or explicit refresh/instruction maintenance | `skills/agent-update/SKILL.md`; keep the existing daily refresh and CLI update policy |
| The user signals that an answer is bullshit, evasive, empty, or unjustifiably confident | `skills/stop-bullshit/SKILL.md`; diagnose and correct the underlying failure rather than merely soften the wording |
| Writing, revising, or assessing a task handoff document for a fresh agent session | `skills/agent-handoff/SKILL.md`; finalize the reviewed handoff and return its location with the first prompt for the fresh session |
| Git mutation, branch/worktree changes, or handling PR review threads | `agent-guidance/version-control.md` |
| Hugging Face authentication or Hub operations | `agent-guidance/hugging-face-auth.md` |
| Starting a Claude subprocess or checking its authentication | `agent-guidance/claude-auth.md`; for reasoning/review also `agent-guidance/claude-model.md` |
| TT-Metal build, import, test, or workload; touching a TT device; MPI launches or shared writable caches | `agent-guidance/tt-metal/README.md` |
| A suspected TT device anomaly requires minimal reproduction, host/device/unit localization, upstream verification, or submission artifacts | `skills/tt-device-investigation/SKILL.md`; not routine op correctness, performance tuning, or standalone hang/reset recovery |
| A TT device experiment takes unexpectedly long; diagnosing device hangs, initialization failures, or unsuccessful resets | `agent-guidance/tt-metal/debugging.md`; also the basic guide before device work |
| Editing or reviewing TT-Metal kernels or ops | `agent-guidance/tt-metal/kernels.md`; read the basic guide before execution |
| Planning or implementing TT device-op/model-module optimization or performance tests; TTNN trace capture/replay, profiling, or performance measurement and interpretation | `agent-guidance/tt-metal/profiling.md`; also the basic guide before execution |
| Interpreting EvalScope speculative acceptance | `agent-guidance/tt-metal/evalscope.md` |

Never resolve human-authored review threads or operate a shared TT device outside
the applicable lock protocol.
Personal harness maintenance stays in personal repositories and ignored local
entry points. Tracked project changes, commits, pushes, or PRs require explicit
authorization for that project scope. Publication rules are in `agent-guidance/version-control.md`.
Read `PUBLICATION.md` before staging or publishing personal harness changes.

Permission to maintain or publish a personal harness does not authorize disclosure
of confidential project information. Keep internal audits, evaluation inputs and
results, logs, and incident evidence outside both repositories, under the local
agent-update state directory. Local installation does not make a resource part
of the public skill manifest. Before publication,
verify the intended audience and releasability of files, history, commit messages,
and PR content; personal ownership or private visibility is not disclosure consent.
For suspected exposure, stop publication and preserve necessary evidence locally.
Keep remediation within the user-authorized scope; do not change repository
visibility or unrelated history without authorization. Distinguish local cleanup
from verified remote removal.
