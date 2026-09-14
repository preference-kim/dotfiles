# Task handoffs

A handoff must let a fresh agent understand the work and decide how to continue.
Preserve the user's objective, requirements, and the evidence needed for that
decision. Leave room to reassess the previous agent's diagnosis and approach.

## Required structure

Use these five sections, in this order. Keep the essential explanation in the
document; references support it rather than making the reader reconstruct it.

### 1. Task overview

State the concrete goal, detailed requirements, scope, and acceptance criteria.
Explain the intended behavior before using PR numbers or internal shorthand.
Identify the repository, checkout path, branch and relevant revision, and the
server or cluster where the work ran. Distinguish the writer's location from
execution hosts. Include uncommitted work, active jobs, and task-specific
authorization or restrictions when they affect continuation. Date observations
of mutable state; say which relevant state was not checked.

### 2. Existing plan

Explain the established breakdown of the work: each part's purpose, intended
result, responsibility, and dependencies. Include the rationale needed to
understand those boundaries. Distinguish user requirements, accepted decisions,
and the previous agent's proposed approach. If no plan is recoverable, say so;
label any reconstruction instead of inventing a historical plan. Put progress
in the next section and new suggestions under remaining work.

### 3. Work done

Map the plan's parts to completed, partial, or unverified results. For each
material result, explain what changed, identify the implementation files or
symbols to inspect, and cite the relevant validation and its scope. Include
test and evidence files alongside implementation pointers. Distinguish work
implemented, tested, committed, published, and accepted; one does not imply the
others. A passing sample or historical run supports only its recorded conditions.

### 4. Remaining work

Explain each unresolved problem through its triggering conditions, observed
result, expected behavior or governing criterion, impact, and evidence. State
what is known about the cause and what remains a hypothesis. Include failed
approaches only when their result changes the next decision. Then identify the
outcomes and dependencies still required after the problems are resolved,
including unfinished integration, validation, or delivery when applicable.

Define what would establish resolution. Derive remaining obligations from the
task, not a generic delivery workflow. A proposed fix needs evidence connecting
it to the violated requirement; otherwise keep it a hypothesis. Preserve
binding constraints and acceptance criteria; label optional investigation ideas
as suggestions with their rationale. Leave routine commands, diagnostic choices,
and a new execution plan to the fresh agent. Do not append a second checklist
that dictates its first actions.

### 5. References

Provide a selective map to the task requirements, design, implementation,
reproducers, results, and relevant discussions. Explain what each source
establishes and cite it near the supported claim. Use precise file/symbol,
section, result-field, or log pointers where useful. Define path roots and
hosts; identify local-only evidence that will not travel with Git. Preserve
reproduction details in their owning files. A directory name or a hash alone
does not explain a result, and an uninspected receipt is not verified evidence.

## Compose and check

Reorganize around the current task state instead of appending session history.
Remove repeated conclusions, superseded instructions, reminders about previous
conversational mistakes, and incidental publication or command transcripts.
Refer to maintained operating guidance instead of copying it; retain explicit
task-specific exceptions and unavailable prerequisites that affect the work.
Keep detail when removing it would change the reader's understanding, decision,
or ability to verify a material claim. Brevity alone is not the acceptance test.

Before delivery, check the document against the actual request and available
sources. Missing information stays unknown; do not fill gaps with plausible
dates, statuses, dependencies, or authority. Can a reader without the conversation
explain the goal, the plan and its rationale, what exists and where, what remains
and why, and how to verify those conclusions? Resolve contradictions and
unsupported completion claims;
state consequential evidence gaps without inventing facts or prior authority.
Do not start new implementation work or experiments merely to fill the handoff.
