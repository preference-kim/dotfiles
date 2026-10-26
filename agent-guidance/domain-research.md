# Domain research

Read before naming or assessing a technique or concept, including terminology
inherited from a codebase, and when unfamiliar or contested concepts or conventions
affect problem framing, design, implementation, interpretation, or writing. Reuse
current, sufficient research; investigate the material gap before making decisions
that depend on it.

- Identify the relevant concepts, definitions, contracts, units, and assumptions.
  Inspect primary specifications, documentation, or source to establish what they
  mean and where they apply before choosing terminology or a design.
- Compare relevant external implementations when conventions or design
  alternatives matter. Reuse inspected comparisons while they still cover the
  decision; choose authoritative sources appropriate to the task.
- Check semantic fit: inputs, outputs, ownership, state transitions, ordering, and
  constraints where material. Similar names do not establish equivalent behavior.
  Prefer established, precise terms that match the intended semantics; explain
  differences when conventions vary instead of claiming consensus or copying an
  implementation without checking its assumptions. If no established term fits,
  use a descriptive name and define its scope; identify a new abstraction as local
  rather than presenting a coined label as an established technique.
- When codebase terminology encodes a flawed concept, determine whether the defect
  is in the label, the abstraction or contract, or the behavior. Correct the owning
  definition and affected implementation, identifiers, comments, and documentation
  within the authorized scope. Preserve required compatibility explicitly; explain
  any legacy name and leave work outside that scope as a concrete follow-up rather
  than using the existing code to justify the misconception.
- Record the relevant sources and revisions, applicable findings, and remaining
  conceptual uncertainty where they support the work. Use those findings to guide
  execution. If a definition or assumption remains unresolved, state what depends
  on it and the check needed before proceeding with that decision.
