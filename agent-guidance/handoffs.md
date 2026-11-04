# Task handoffs

When explicitly invoked, the [agent-handoff skill](../skills/agent-handoff/SKILL.md)
drafts, reviews, revises, and finalizes an outgoing handoff and its opening prompt. The
[selection and length contract](../skills/agent-handoff/references/content.md)
lives with that skill; the workflow requires an independent review using
technical prose review followed by `stop-bullshit`.

Use [agent-takeover](../skills/agent-takeover/SKILL.md) when the current request is
to take over and execute an unfinished task. It assesses inherited evidence and
the approach before carrying out the remaining work. Writing or reading a prompt
for another session does not switch the current session's role.
