### Claude model selection

For local Claude subprocesses that perform planning, technical review, or other reasoning-intensive work, explicitly request the current highest configured model and highest supported effort. The current default is `--model fable --effort xhigh`; use a lower-cost model only when the user or the task explicitly prioritizes cost or latency over review quality.

- In non-interactive `--print` workflows, add `--fallback-model opus,sonnet`. This ordered fallback is authorized only when Claude Code reports the primary model unavailable because of model quota, capacity, or availability. It does not authorize changing authentication providers, consuming a different API key, purchasing credits, or bypassing an account-wide usage limit. If every candidate is unavailable, stop and report the blocker.
- When the result depends on reviewer tier, request JSON output, use the top-level `result` as the reviewer response, and inspect `modelUsage` to determine which configured candidate produced it. Ignore auxiliary model entries outside the configured candidate chain. Disclose any fallback and do not describe a fallback result as a highest-model review.
- Keep model aliases in the concrete reviewer adapters and invocations so they can be updated in one intentional policy change when Claude Code's model mapping changes; do not pin a dated model ID merely to preserve an obsolete version.

Split broad reviews by coherent contract and supply only its relevant code, tests
and dependencies. Do not repeat an oversized packet after a caller timeout.
For long non-interactive reviews, use `--output-format stream-json`, `--verbose`,
and `--include-partial-messages` so reasoning progress and errors remain observable.
Read the final `type: result` event for the response and `modelUsage`. A caller's
wall-clock timeout is an incomplete review, not evidence that the model is
unavailable or stalled. Check progress and errors before interrupting or retrying;
allow an actively progressing review to finish within the task's runtime budget.
