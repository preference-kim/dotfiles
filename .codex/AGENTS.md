# AGENTS.md

## Purpose

This file defines the working principles for agents contributing code,
documentation, reviews, issues, pull request descriptions, and other technical
communication in this repository.

The goal is not merely to produce correct local changes. The goal is to leave
behind artifacts that read as coherent, intentional designs.

## Core Standard

Design, do not accumulate.

Every change should improve or preserve the coherence of the whole. Do not paste
new code, sections, explanations, or exceptions around old experiments. Retouch
the surrounding artifact so the final result reads as one intentional design
rather than a sequence of edits.

A reader should not be able to infer the order in which the code, document, or
message was written.

## Scope

These principles apply to all technical artifacts, including:

- source code;
- tests;
- configuration;
- design documents;
- README and user-facing documentation;
- comments;
- issues;
- pull request descriptions;
- review comments;
- status updates and other engineering messages.

Different artifacts require different levels of detail, but the same standard
applies: communicate the current design and reasoning, not the history of how
you arrived there.

## General Principles

### Communicate structure, not chronology

Present ideas according to their logical structure, not the sequence in which
they were discovered.

Do not publish a running log of attempts, objections, fixes, and follow-up
patches. Reorganize the result so the reader can understand the current state,
the rationale, and the conclusion without reconstructing your thought process.

### Make concepts explicit

Use precise names for roles, payloads, placement, ownership, lifecycle,
contracts, and responsibilities.

Prefer established terminology from the codebase, the project domain, and the
relevant technical field. Do not invent private vocabulary unless it is truly
needed. When a new term is needed, define it before using it.

Avoid overloaded names, implicit assumptions, and context that only exists in a
conversation outside the artifact.

### Optimize for simplicity of the whole

Prefer a system that is simple overall over artifacts that satisfy local rules
mechanically.

A function is not better merely because it is shorter. A document is not better
merely because it has more sections. A message is not better merely because it
lists every intermediate observation.

Split, abstract, summarize, or inline only when doing so makes the whole easier
to understand, maintain, and evolve.

Avoid abstractions, layers, helper functions, sections, terms, or explanations
that exist only to satisfy a local rule while making the overall design harder
to follow.

### Explain causes, not observations

Do not merely describe what happens. Explain the mechanism, constraint,
assumption, invariant, or tradeoff that makes it happen.

Focus comments and documentation on non-obvious rationale. Do not restate what
is already visible from the code or text.

### Be precise and falsifiable

Technical communication should be scientific rather than rhetorical.

Clearly distinguish facts, assumptions, hypotheses, decisions, and open
questions. Avoid vague claims such as "better", "cleaner", "simpler", "faster",
or "more efficient" unless the evaluation criterion is stated.

When possible, use concrete examples, measurable criteria, explicit constraints,
or reproducible checks.

### Keep production intent visible

The primary artifact should represent the intended production design, not the
development history.

Keep debug paths, probes, temporary migrations, and experimental behavior out of
the production baseline unless they are explicitly part of the design. Remove
obsolete mechanisms when their purpose disappears.

Do not leave defensive comments whose only purpose is to answer a possible
review challenge. Instead, document the actual design constraint or remove the
comment.

### Respect local consistency

Follow the conventions of the surrounding code and documentation unless there is
a compelling reason not to.

Naming, formatting, structure, terminology, error handling, and control flow
should feel native to the repository. Improve nearby content when needed to
preserve coherence, but avoid broad rewrites unrelated to the requested change.

## Code Writing Principles

### Retouch the surrounding design

Do not implement changes by layering new code around stale assumptions,
obsolete branches, or previous experiments.

When a change modifies the meaning of an existing mechanism, update the
surrounding source so the final code expresses the new design directly. Remove
or reshape old paths that no longer fit.

### Make roles and ownership visible

Code should reveal what each component owns, receives, produces, validates, and
controls.

Use names that reflect actual responsibilities rather than incidental data
shape. Make ownership, lifecycle, placement, and authority explicit where they
matter.

Prefer explicit contracts and validation over implicit assumptions hidden in
call order, naming conventions, or comments.

### Keep complexity near its mechanism

Local complexity is acceptable when it is the clearest expression of a real
mechanism.

Do not hide complexity behind arbitrary helpers, generic abstractions, or
premature layering. Extract code when the extracted unit has a stable concept,
clear responsibility, and meaningful name.

### Prefer readable control flow

Use direct, readable control flow over cleverness. Avoid compact expressions,
metaprogramming, implicit state, or excessive indirection when they obscure the
actual behavior.

The reader should be able to follow the normal path, exceptional path, and
ownership transitions without reconstructing hidden state.

### Keep the production baseline clean

Do not leave debug output, probes, temporary flags, dead branches, commented-out
code, or unused compatibility shims in the normal production path.

If diagnostic behavior is required, make it an explicit feature with clear
ownership, configuration, and lifecycle.

### Limit unrelated rewrites

Make the change coherent, but do not use a focused task as an excuse to rewrite
unrelated systems.

A surrounding refactor is appropriate when it is necessary to express the
requested change cleanly. It is not appropriate when it merely imposes a new
personal style on otherwise working code.

### Follow project style intentionally

Use the surrounding repository style as the source of truth. Where external
style references are useful, follow the spirit of the Google Python Style Guide
and the Clang style guide: clear ownership, readable control flow, consistent
formatting, and names that expose intent.

Do not apply style rules mechanically when doing so makes the whole design less
simple.

## Testing and Verification

Every substantive code change should be accompanied by an appropriate
verification step.

Prefer tests that check behavior and contracts rather than incidental
implementation details. When modifying existing behavior, update or add tests so
the intended contract is visible.

Before reporting completion, state what was verified. If a relevant test was not
run, say so explicitly and explain the constraint.

Do not claim correctness from inspection alone when a practical verification
path exists.

## Documentation and Communication Principles

### Write for the reader's next action

A technical message should make the expected next step clear.

The reader should understand whether they are being asked to review, decide,
approve, debug, object, merge, operate, or simply be informed.

### Design the explanation as a whole

Do not append new paragraphs, caveats, or updates without reconsidering the
whole explanation.

When adding information, revise the surrounding structure so the document or
message still reads as if it was written intentionally from the start.

### Use shared terminology

Use actual system names, public concepts, and established domain terms. Avoid
private shorthand that only makes sense to the author.

If a new term is necessary, introduce it with a definition, scope, and reason for
existence before relying on it.

### Separate facts from interpretation

Make clear which statements are observed facts, which are assumptions, which are
hypotheses, and which are decisions.

When presenting a recommendation, include the criterion used to judge it. When
raising a concern, explain the mechanism or evidence behind the concern rather
than only saying that something feels wrong.

### Prefer current state over history

Documents, pull requests, and reviews should describe the current design and its
rationale, not merely the sequence of attempts that produced it.

Historical context is useful only when it explains a current constraint,
tradeoff, or decision. Otherwise, remove it or move it out of the primary
explanation.

### Be concise by removing noise, not by removing substance

Conciseness means the reader receives the necessary structure with minimal
irrelevant burden.

Do not omit critical assumptions, constraints, or failure modes merely to make a
message shorter. Remove repetition, chronology, private context, and rhetorical
padding first.

## Agent Workflow

When working on a task, follow this workflow.

### 1. Understand the existing artifact

Inspect the surrounding code, documentation, and conventions before changing
anything. Identify the current design, the relevant contracts, and the local
style.

Do not assume that the immediate edit location is the correct design boundary.

### 2. Define the intended final state

Before editing, determine what the artifact should look like after the change.
The target is not "old content plus patch". The target is the simplest coherent
artifact that includes the requested change.

### 3. Make the smallest coherent change

Apply the narrowest change that preserves or improves the whole design.

Small does not mean fragmented. A slightly broader edit is preferable when it
removes an ad-hoc seam and makes the final artifact read as one design.

### 4. Remove obsolete residue

After implementing the change, remove dead code, stale comments, obsolete
terminology, unused helpers, and outdated explanations introduced by previous
iterations.

Do not preserve history in the primary artifact unless that history is itself a
current design constraint.

### 5. Verify behavior and presentation

Run relevant tests, checks, formatters, or manual validation. For documentation
or communication changes, reread the final artifact from the reader's point of
view and ensure the structure is logical rather than chronological.

### 6. Report clearly

When summarizing work, explain the final state, the important design decisions,
and the verification performed.

Do not provide a raw activity log. Mention failed attempts only if they affect
the final design, risk, or follow-up work.

## Review Checklist

Before finalizing a change, check the following:

- Does the artifact read as one intentional design?
- Can a reader infer the edit history? If so, retouch the structure.
- Are roles, ownership, contracts, and responsibilities explicit?
- Is the whole simpler, not merely locally smaller?
- Are names and terms consistent with the repository and domain?
- Are debug, probe, temporary, and obsolete paths removed or isolated?
- Do comments explain non-obvious rationale rather than restating the code?
- Are broad rewrites limited to what the requested change requires?
- Are facts, assumptions, hypotheses, decisions, and open questions separated?
- Is the reader's next action clear?
- Have relevant tests or checks been run, or has the limitation been stated?

## Prohibited Patterns

Avoid the following patterns unless there is an explicit, documented reason:

- appending new code around obsolete logic instead of reshaping the design;
- creating helper functions solely to make a function shorter;
- adding abstractions without stable responsibility or ownership;
- inventing private terminology for established concepts;
- leaving debug prints, probes, commented-out code, or temporary flags in the
  production path;
- writing comments only to defend against anticipated review objections;
- making vague claims without criteria;
- presenting a chronological log where a structured explanation is needed;
- performing broad rewrites unrelated to the requested change;
- silently weakening contracts, validation, or error handling to make a change
  easier.

## Final Rule

Leave the repository easier to understand than you found it.

Correctness is required, but coherence is the standard. A technically working
change that leaves behind accumulated residue is not complete.
