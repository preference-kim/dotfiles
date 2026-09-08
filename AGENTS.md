# AGENTS.md

## Stable working principles

This section is user-owned and independent of the Moreh operational guidance below. Upstream synchronization may update the operational guidance, but must preserve the meaning and position of this section unless the user explicitly requests a change.

### Scientific reasoning

- Before substantial work or a consequential change of direction, pause to understand the task and relevant context: establish the objective, constraints, assumptions, and acceptance criteria, and be able to explain how the proposed action serves them. Inspect available context to resolve gaps that could change the action; defer dependent action while a material gap remains. Ask the user only when the needed information cannot be established from available evidence.
- Check whether each consequential step resolves an uncertainty or advances the acceptance criteria; if it does neither, revise the approach.
- Distinguish observed facts, assumptions, hypotheses, inferences, decisions, and open questions. Do not present one category as another.
- Make technical claims precise and falsifiable. State the evidence, evaluation criterion, reproducer, or measurement that would support or refute a claim when one is available. Narrow or retract unsupported claims; vague hedging does not repair them. Missing evidence does not establish falsity.
- Explain the mechanism, constraint, or causal chain behind a result. Keep the central unresolved question explicit; do not obscure it with vague language, convenient assumptions, or a nearby easier question. When the cause is unknown, say so and identify the evidence needed to distinguish plausible explanations.
- Base recommendations on explicit criteria and describe the relevant tradeoffs. Apply the same criteria to alternatives, your preferred conclusion, and the user's premises; include material counterevidence. Do not use words such as "better", "cleaner", or "faster" without saying what is being optimized or measured. Verify what references establish and why they apply; authority or agreement alone is not an argument.
- Reassess the argument throughout the task, especially when evidence conflicts or progress stalls. If that self-check is difficult, use a sub-agent as an independent critic of the specific uncertain premise or approach. Evaluate its findings against evidence; do not treat agreement as validation.
- Do not finalize a claim you cannot explain. Re-examine the task and gather the missing evidence or understanding. If an unresolved premise prevents a supported conclusion, say so and identify the check needed to resolve it.

### Communication and delivery

- Keep all feedback, documentation, and answers concise, especially PR review comments. For technical problems, identify the problem precisely, explain the fundamental design or contract established conventions call for with relevant code, standards, or authoritative references, and end with a brief summary of concrete suggestions. Distinguish conventions from preferences; omit repetition and generic background.
- Present every document and technical message as a coherent argument: connect its purpose, premises, evidence, conclusions, and expected next action without unstated logical jumps. Define terms before relying on them, use established terminology consistently, and resolve internal contradictions. Remove gibberish and vague abstractions that conceal missing understanding; use language whose meaning you can explain.
- Include the scope, preconditions, invariants, ownership, behavior, and failure modes needed for the reader to evaluate or use the artifact. Omit an element only when it is irrelevant. Completeness means covering what the reader needs for the next action; remove repetition, vague abstractions, and incidental history before removing substantive constraints or evidence.
- Lead with the current supported conclusion and the document's purpose. Include the evidence, constraints, risks, and next action the reader needs. Omit activity logs, superseded reasoning, and attempt chronology unless that history is necessary to reproduce a result or explain current behavior or risk.
- Keep progress updates to the latest verified state, a material blocker or failure and its impact, and the next action.
- When adding policy or new information, revise the surrounding structure so the artifact reads as one intentional whole; remove obsolete residue, duplication, stale wording, and rhetorical padding.
- Before delivering any document, artifact, or final response, check both the material and your own response for relevance, concision, precision, and logical completeness, applying the reasoning principles above. Verify the evidence or explicit premise and scope of material conclusions, criticism, praise, severity, and completion claims; recheck after the last edit. Preserve warranted confidence and useful uncertainty; do not manufacture objections or announce a ritual all-clear.

### Pull request communication

- Before creating or revising a PR description, load `write-technical-pr`; its policy preserves the Korean Summary, self-contained evidence, reproduction, and final-state requirements.
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

Treat this AGENTS.md as repo-local guidance. Explicit user instructions for the current task take precedence over these defaults unless they conflict with system, developer, platform, safety, or other higher-priority instructions. If a requested override cannot be followed because of a higher-priority rule, say so briefly and follow the highest-priority applicable instruction.

## Language

Use English by default for communication. Follow an applicable skill's Korean-language requirements for the task content it governs; those requirements are exceptions to the English default and do not require a separate user request. Final explanations and reports to the user remain in English by default, even when the task content is in Korean. Follow explicit user language instructions for the scope they specify.

## External services

When compatible with the applicable platform and tool instructions, prefer command-line tools, direct APIs, or another programmatic approach over installing or requesting a plugin for services such as Slack or GitHub. Use a plugin when the platform requires it or the direct approaches are unavailable or clearly inadequate.

## Execution location

Unless the user explicitly requests remote execution, run builds, tests, benchmarks, experiments, and other jobs on the host and cluster where the session is already running. Do not use SSH or another remote connection to move a job elsewhere. For example, from `ttdev31`, run the job on `ttdev31`, not `ttdev32`; from AI cluster 1, stay on AI cluster 1 rather than using AI cluster 2.

## Unexpected errors

Never silently omit an unexpected error. Report it in terms of its current impact, recovery, and residual risk; omit command-by-command retry chronology unless it is needed to reproduce or diagnose the problem.

## Long-running experiments

Stream or periodically retrieve output while a long-running process runs. Detect completion through process status rather than estimated sleeps or log-following alone, and check the result promptly after exit.

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
| Git mutation, branch/worktree changes, or handling PR review threads | `agent-guidance/version-control.md` |
| Hugging Face authentication or Hub operations | `agent-guidance/hugging-face-auth.md` |
| Starting a Claude subprocess or checking its authentication | `agent-guidance/claude-auth.md`; for reasoning/review also `agent-guidance/claude-model.md` |
| TT-Metal build, import, test, or workload; touching a TT device; MPI launches or shared writable caches | `agent-guidance/tt-metal/README.md` |
| Diagnosing TT device hangs, initialization failures, or unsuccessful resets | `agent-guidance/tt-metal/debugging.md`; also the basic guide before device work |
| Editing or reviewing TT-Metal kernels or ops | `agent-guidance/tt-metal/kernels.md`; read the basic guide before execution |
| TTNN trace capture/replay or performance measurement and interpretation | `agent-guidance/tt-metal/profiling.md`; also the basic guide before execution |
| Interpreting EvalScope speculative acceptance | `agent-guidance/tt-metal/evalscope.md` |

Never push directly to a project's main branch, resolve human-authored review
threads, or operate a shared TT device outside the applicable lock protocol.
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
