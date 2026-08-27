# AGENTS.md

## Stable working principles

This section is user-owned and independent of the Moreh operational guidance below. Upstream synchronization may update the operational guidance, but must preserve the meaning and position of this section unless the user explicitly requests a change.

### Scientific reasoning and communication

- Distinguish observed facts, assumptions, hypotheses, inferences, decisions, and open questions. Do not present one category as another.
- Make technical claims precise and falsifiable. State the evidence, evaluation criterion, reproducer, or measurement that would support or refute a claim when one is available.
- Explain the mechanism, constraint, or causal chain behind a result. Do not conceal missing understanding with vague or abstract language. When the cause is unknown, say so and identify the evidence or experiment needed to resolve it.
- Base recommendations on explicit criteria and describe the relevant tradeoffs. Do not use words such as "better", "cleaner", or "faster" without saying what is being optimized or measured.

### Logical completeness

- Design every document and technical message as a coherent argument rather than a sequence of observations. Its purpose, premises, evidence, conclusions, and expected next action should connect without unstated logical jumps.
- Include the scope, preconditions, invariants, ownership, behavior, and failure modes needed for the reader to evaluate or use the artifact. Omit an element only when it is irrelevant, not merely to make the text shorter.
- Define terms before relying on them, use established terminology consistently, and resolve internal contradictions. If an open question prevents a conclusion, state that no supported conclusion is available and identify the unresolved premise.
- Write every document, status update, and final response from the current supported state. Lead with its purpose and conclusion; include only the evidence, constraints, risks, and next action the reader needs. Omit activity logs, attempt chronology, superseded reasoning, and narration of how the answer was produced unless that history is necessary to reproduce a result or explain current behavior or risk.
- Treat progress updates as state snapshots, not work diaries. Report only the latest verified state, a material blocker or failure and its impact, and the next action.
- When adding policy or new information, revise the surrounding structure so the artifact reads as one intentional whole; remove obsolete residue, duplication, stale wording, and rhetorical padding.
- Treat completeness as coverage of the reasoning necessary for the reader's next action, not as verbosity. Remove repetition, rhetorical padding, and incidental history before removing substantive constraints or evidence.

### Pre-delivery review

- Before delivering any document, artifact, or final response, review it for relevance, concision, precision, and logical completeness. Remove repetition and vague abstractions, and verify that every material conclusion is supported by evidence or an explicit premise.
- Do not finalize a claim that you cannot explain. If material understanding is missing, re-examine the task and gather the required evidence. If that evidence is unavailable, state that no supported conclusion is available and identify the unresolved premise and the check needed to resolve it.

### Pull request descriptions

- Start every PR description with `## Korean Summary`. Write the section in Korean using vocabulary and concepts already established in the codebase. State the core problem, retained solution, and concrete result clearly enough to understand without external context; do not introduce unexplained or promotional terminology.
- Make the PR description self-contained for review. Include the problem, final design, relevant contracts and constraints, reproduction procedure, and evidence needed to assess the change. External references may supplement the body but must not carry information required for the review decision.
- Never include a local artifact path or use a local-only file, log, plot, report, working-tree state, or other reviewer-inaccessible resource as evidence. Move every material fact from such an artifact into the PR description. Do not require the reviewer to consult chat, comments, external documents, dashboards, or unpublished artifacts to understand or validate a claim.
- Write text as short bullets grouped by distinct topics. Use direct, specific wording; remove ambiguous, verbose, or repetitive prose.
- For every reported experiment, provide an exact reproducible command line in a fenced `bash` code block. Include the repository-relative working directory, required environment variables and inputs, and exact test or benchmark selection; do not depend on local aliases, private wrappers, undeclared state, or machine-specific absolute paths.
- Present concrete results in Markdown tables with the workload, conditions, units, acceptance criterion or comparison basis, and result needed to interpret each value.
- When detailed logs are necessary, include only the relevant excerpt inside a collapsed `<details><summary>...</summary>...</details>` block with a specific summary label. Omit irrelevant output, secrets, and local paths.
- State only the final retained design and final results relative to the base branch. Never narrate how the branch arrived there: omit commit-by-commit evolution, review iterations, rebases, intermediate candidates, failed or superseded experiments, transient regressions, fixes to problems absent from the final change, retries, and rerun chronology. A baseline may appear only as a direct comparison needed to quantify the final result, without an accompanying development story.

### Code and design clarity

- Prefer direct, readable control flow that makes the normal path, exceptional path, state transitions, and ownership visible.
- Use the minimum abstraction needed to express stable responsibilities. Extract a unit only when it has a coherent role and meaningful contract; do not create helpers or layers solely to shorten local code.
- Design, do not accumulate. Make the smallest coherent change, reshape stale logic when its assumptions no longer hold, and remove obsolete branches, comments, debug paths, and compatibility residue that no longer serve the production design.

### Build and test paths

- During builds and tests, do not redirect caches, temporary files, artifacts, outputs, or related state to `/tmp` or another temporary path unless the user explicitly authorizes that redirection.
- If a required build or test path remains unavailable or unwritable after applying the shared-default-asset policy below, stop and report the blocker instead of substituting a temporary path.

### Shared default assets

- On shared servers, use the project's configured default paths for datasets, model weights, and other shared assets when those paths exist.
- If an asset exists at its default path but access fails only because its ownership, mode bits, or ACLs restrict it to a particular user, verify the exact shared target and fix its ownership or permissions before continuing. The team must be able to read and write the asset and to traverse directories or execute files where required. Keep the change scoped to the intended shared asset; do not bypass it with a user-private copy or an alternate path.
- If the configured default path or required asset is absent, treat that as an unintended code, configuration, deployment, or provisioning condition. Stop and determine whether the default path or asset provisioning must be fixed instead of silently creating or selecting a substitute path.

You are developing on shared Tenstorrent Galaxy servers at Moreh. Devices are a shared resource — you must follow the locking protocol exactly.

## Instruction priority

Treat this AGENTS.md as repo-local guidance. Explicit user instructions for the current task take precedence over these defaults unless they conflict with system, developer, platform, safety, or other higher-priority instructions. If a requested override cannot be followed because of a higher-priority rule, say so briefly and follow the highest-priority applicable instruction.

## Language

Never use Korean unless the user explicitly requests it.

## External services

When compatible with the applicable platform and tool instructions, prefer command-line tools, direct APIs, or another programmatic approach over installing or requesting a plugin for services such as Slack or GitHub. Use a plugin when the platform requires it or the direct approaches are unavailable or clearly inadequate.

### Hugging Face authentication

Treat a successful bare `hf auth whoami` as the authentication check for Hugging Face Hub operations. If it fails because no usable credential is configured, install the `age`-encrypted token from the canonical dotfiles repository into that host's standard Hugging Face credential store instead of starting an interactive or browser login:

- Resolve the dotfiles root from the canonical `AGENTS.md`; do not assume a host-specific clone path. Require `age`, the tracked `.hf-token.age` ciphertext, and an on-disk RSA or Ed25519 SSH private key whose public key is listed in `.hf-token.recipients`. A GitHub registration or forwarded `ssh-agent` without the private-key file is insufficient.
- Run `<dotfiles>/scripts/install-hf-credential`, then rerun bare `hf auth whoami`. The installer decrypts the token in memory, passes it through `HF_TOKEN` rather than a command argument, and writes it only through the installed Hugging Face client to that host's standard credential store with mode `0600`. Set `HF_TOKEN_SSH_IDENTITY` to the matching private-key path only when companion `.pub` auto-discovery cannot select it.
- Use `<dotfiles>/scripts/with-hf-token <command> [args ...]` only when a process-scoped credential is explicitly preferable to persistent local login. It decrypts the token in memory, exports `HF_TOKEN` only to the child process, and does not update the credential store.
- If `age`, a matching private key, decryption, or the authenticated check is unavailable, report that exact prerequisite and stop. Do not start another login flow, mint a replacement token, or write a plaintext token without explicit authorization.

Never print or commit the token, pass it in a command argument, or write a plaintext copy outside the standard Hugging Face credential store during fallback. GitHub key removal does not revoke access to an existing ciphertext; after a recipient-key compromise, rotate the Hugging Face token and re-encrypt it to the retained recipients.

### Claude authentication

For local Claude subprocesses and reviewer workflows, use the subscription credentials managed by `claude auth login` or `/login`. Do not read or maintain `$HOME/.claude/oauth-token` as a local credential source, and do not export a static `CLAUDE_CODE_OAUTH_TOKEN` from a file.

- Remove inherited `CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_API_KEY`, and `ANTHROPIC_AUTH_TOKEN` only from the Claude child process so those overrides cannot take precedence over the CLI-managed login. Do not unset credentials in the parent session.
- Treat `claude auth status` as a local configuration check, not proof that a bearer token is accepted by the service. When authentication health is material, a successful minimal non-interactive Claude request is the authoritative check.
- If the managed local login is unavailable or cannot refresh, stop and ask the user to run `claude auth login`. Do not start an authentication flow or mint and persist a replacement token without explicit authorization.
- For CI or another browserless environment that cannot use the managed login, generate a long-lived token with `claude setup-token` and inject it as `CLAUDE_CODE_OAUTH_TOKEN` through the environment's secret manager. The command prints the token but does not save it; never commit, log, or store it in a shared plaintext file.

Never print or commit any credential.

## Independent plan review

Use the shared `plan-review` skill when the user asks to review, critique, validate, or stress-test an existing plan. Do not invoke it merely because a request creates or discusses a plan.

- Review only a user-identified plan file or plan content that is uniquely identifiable in the conversation. Never scan tool-specific plan directories, select a recent file, or guess among candidates.
- Use the opposite agent family at its current highest configured model with `xhigh` effort. Read the concrete agent and model mapping from the skill's reviewer adapter rather than duplicating model aliases in this file.
- Treat review as read-only. Produce a replacement plan only when requested, and update a named plan artifact only with explicit write authorization.
- If the required opposite-family reviewer, model, authentication, or read-only execution boundary is unavailable, report that independent review is blocked. Do not present same-family review or self-review as independent.

## Execution location

Unless the user explicitly requests remote execution, run builds, tests, benchmarks, experiments, and other jobs on the host and cluster where the session is already running. Do not use SSH or another remote connection to move a job elsewhere. For example, from `ttdev31`, run the job on `ttdev31`, not `ttdev32`; from AI cluster 1, stay on AI cluster 1 rather than using AI cluster 2.

## Unexpected errors

Never silently omit an unexpected error. Report it in terms of its current impact, recovery, and residual risk; omit command-by-command retry chronology unless it is needed to reproduce or diagnose the problem.

## MPI and shared filesystems

- Never change `HOME` to isolate per-rank or per-job artifacts. `HOME` is a session-wide input that may also determine unrelated runtime paths such as cluster descriptors, launch manifests, configuration, credentials, logs, and caches. Use the dedicated cache or artifact variable instead (for example, `TT_METAL_CACHE` for the tt-metal JIT cache).
- Before assuming that equal path strings collide, verify the filesystem type and mount identity on every participating host. The same path on host-local filesystems names separate objects; on NFS or another shared filesystem it may name the same object.
- On a shared writable cache, namespace the dedicated cache path by both launch identity (for example, host set, job ID, or configuration fingerprint) and MPI rank. Rank is unique only within its MPI world, so independent jobs can both have ranks 0 through N-1.
- Before device work, verify the effective host set, MPI world/rank, and relevant paths in every rank. Audit all consumers and SSH/MPI propagation before overriding any process-global environment variable, and keep shared runtime metadata on explicit stable paths.

## Agent file sync

This file is the canonical shared guidance for Codex and Claude. The concrete entry-point layout is a per-host choice, not fixed in this document: it is recorded in `agent-file-sync.local.yaml` at the dotfiles root, a host-local file that is gitignored and never committed, based on the template in the tracked `agent-file-sync.example.yaml`. In `moreh-dev` mode, the same file records `moreh_dev_root`, the host-specific Git checkout root that receives the entry points. Because the file never syncs through git, no agent-update run on any host can read, set, or overwrite another host's mode or target; each host's choice exists only on that host, made there directly.

Two modes exist:

- `host-global`: `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md` are symlinks to the corresponding dotfiles files, and shared skills are exposed through per-skill links at `~/.codex/skills/<name>` and `~/.claude/skills/<name>`.
- `moreh-dev`: the Git checkout configured by `moreh_dev_root` carries the root `AGENTS.md`/`CLAUDE.md` links and `.codex/skills/<name>`/`.claude/skills/<name>` links instead; no host-global entries under `~/.codex` or `~/.claude` are made. A relative `moreh_dev_root` is resolved from the dotfiles root; an absolute path is used as written.

If the current host has no configured mode, or selects `moreh-dev` without a valid `moreh_dev_root`, `agent-update` must stop and ask rather than guess, search for a checkout, or apply a default.

At the start of the first user task in each new session, use the `agent-update` skill for its daily refresh. The skill skips network and repository work after a successful refresh on the same local calendar day, but always verifies and repairs the current host's configured entry points and skill links. If it pulls or reconciles changed instructions, re-read the updated AGENTS.md and skill files before continuing.

Use `/agent-update` or `$agent-update` to force a refresh, edit shared agent instructions or skills, repair the current host's links, publish agent-file changes, or set this host's mode and target in `agent-file-sync.local.yaml`. Synchronization must compare the local design with `csehydrogen/.files` semantically; never overwrite intentional local policy with a wholesale upstream copy.

## Git workflow

Never push directly to main branches such as `main`, `master`, `moreh/main`, or `origin/moreh/main`. Always create a feature branch and open a pull request for review. If a user asks to push work and the current branch is a main branch, stop and create/switch to a non-main branch before pushing.

Exception: for agent-instruction updates in the personal dotfiles and shared skills repositories, commit and push directly to `main`. Do not create a feature branch or pull request for those updates.

When creating a feature branch, use the `sunho/` prefix by default unless the user explicitly requests a different branch name.

When addressing feedback on a pull request you own, never resolve a review thread whose root comment was authored by another person. You may resolve a thread only when its root comment was authored by Copilot or another automated agent, and only after its concern has been addressed and pushed. Human-authored threads must remain open for a person to resolve, even when you implement the requested change.

## Worktree use

Use the repository's primary checkout by default. Use `git worktree` only for
static code analysis or documentation work at a specific HEAD. Never create an
ad hoc worktree for builds or device-backed tests; perform that work only in
the current session checkout.

If the primary checkout is dirty, do not create a worktree to avoid it.
Preserve the existing changes first: either stash them, including relevant
untracked files, or commit and push them to an appropriate branch, following
the repository's Git rules. Never discard or overwrite existing work. If the
dirty changes are the task's intended input, handle them there rather than
stashing them away. Restore stashed changes when the task is complete and it is
safe to do so; report any restoration conflict.

If existing changes prevent a required branch checkout, commit them locally or
stash them before checking out the branch.

## Device Locking

Only use the lock when you are working with https://github.com/moreh-dev/tt-metal and the current host is registered with `moreh-lock`. Run `moreh-lock status` to confirm registration; it reports the node and its current holder.

`moreh-lock` is a system installation at `/usr/local/bin/moreh-lock`, independent of any tt-metal checkout. Never vendor, install, or invoke a checkout-local copy. tt-metal removed its bundled `tools/moreh_lock`, so a `moreh-lock` inside a checkout virtual environment is a stale console script that shadows the system binary and fails with `ModuleNotFoundError: No module named 'moreh_lock'`. Delete such a shim rather than working around it. The system wrapper runs Python with `-I`, so a tt-metal `PYTHONPATH` cannot shadow the package once the shim is gone.

Separately, activate the active checkout's virtual environment for tt-metal build, test, import, and workload commands, so they resolve dependencies from that checkout rather than another one:

```bash
source "<absolute path to the active tt-metal checkout>/python_env/bin/activate"
```

If that environment does not exist, create it with `./create_venv.sh` first, then activate it. `create_venv.sh` defaults to `./python_env`, but a checkout may use a different directory such as `.venv`; activate the one that checkout actually has. Activating a virtual environment never replaces the system `moreh-lock`.

Exception: `vllm-tt-moreh` test scripts acquire and release the device lock internally. When running those test scripts, do not acquire `moreh-lock` manually outside the script.

### Lock command to use

Use the CLI wrapper:

```bash
moreh-lock
```

Before running any command that touches Tenstorrent devices (for example, opening a TT device with `ttnn.open_device` / `ttnn.open_mesh_device`, running TT-backed pytest, profiling TT workloads, etc.), check lock status:

```bash
moreh-lock status
```

Prefer the CLI wrapper for device commands:

```bash
moreh-lock run --wait-timeout 3600 --max-hold <seconds> -m "<what you are doing and expected duration>" -- <command> <args>
```

The lock is node-wide. Reservations are node-exclusive, so two jobs never share a node, and `TT_VISIBLE_DEVICES` selects only which devices the workload uses; it never narrows the lock. To lock several hosts for one job, name every host with `--nodes host1,host2`.

If the command needs shell features, wrap it with `bash -lc`:

```bash
moreh-lock run --wait-timeout 3600 --max-hold <seconds> -m "<what you are doing and expected duration>" -- bash -lc 'cd path/to/tests && FOO=1 pytest test.py -v 2>&1 | tee run.log'
```

Use manual hold only when you need an interactive lock window:

```bash
moreh-lock hold -m "<why you need the device>"
```

After a locked command exits, verify the lock was released:

```bash
moreh-lock status
```

Expected final output reports the node with no holder:

```text
NODE	<host>
STATE	FREE
USER	-
JOB	-
```

Do not run device commands outside `moreh-lock run` unless a higher-level tool already acquires the lock for you. Do not manually kill another user's lock process.

When queued for `moreh-lock`, do not kill or cancel your own waiter merely because the lock is taking time; the lock is queue-based, and canceling loses your acquisition opportunity. Only cancel a queued waiter if the user explicitly asks, the command is no longer valid, or continuing would be unsafe.

Use `--wait-timeout` for lock acquisition timeout. Use `--max-hold` for command runtime timeout. Always set `--max-hold` to your best estimate of how long you need the device; do not omit it for non-interactive device commands.

If you are debugging or thinking and no command is actively using the device, release the lock immediately so others can use it.

### Docker / container note

Inside Docker, locking only works across processes if the container shares host IPC:

```bash
--ipc=host
```

Also set the real host/user via environment variables or CLI flags when needed:

```bash
export MOREH_LOCK_HOSTNAME=<host>
export MOREH_LOCK_USERNAME=<user>
```

## Building

Always use `./build_metal.sh -ce` to compile tt-metal. Never use cmake directly, and never use a unity build. After changing tt-metal source code, complete this build before running tests or device workloads; do not rely on judging whether JIT compilation is sufficient.

### Environment variables

Before building, testing, importing, or running tt-metal, set the environment for the exact tt-metal checkout being used. Be especially careful with worktrees: `TT_METAL_HOME` must point to the active tt-metal worktree, not another checkout. Set all of the following:

```bash
export TT_METAL_HOME="<absolute path to the tt-metal checkout or worktree in use>"
export TT_METAL_RUNTIME_ROOT="${TT_METAL_HOME}"
export PYTHONPATH="${TT_METAL_HOME}:${TT_METAL_HOME}/ttnn:${TT_METAL_HOME}/tools"
```

## TTNN trace capture, replay, and performance measurement

### Trace capture and replay contract

TT-Metal trace capture records warmed-up, non-blocking device-program dispatch commands with fixed tensor shapes and
addresses. It does not capture arbitrary host command-queue (CQ) work. Beginning capture puts every physical device's
system-memory manager into bypass mode, so this restriction applies to all host CQs on the mesh, not only the CQ whose
trace ID is active.

- Between `begin_trace_capture` and `end_trace_capture`, enqueue only the device operations intended for the trace.
  Compile and warm them up before capture, and keep their device buffers at the addresses the replay will use.
- Do not perform H2D or D2H transfers, buffer/core reads or writes, `.cpu()`/`to_torch()` conversion, device or CQ
  synchronization/finish, event record/wait, profiler drains, tensor dumps, or any helper that performs equivalent host-CQ
  work inside capture. Do not hide such work in an op wrapper or callback expected to run as part of trace replay.
- Replay with `execute_trace(..., blocking=False)`. The trace lifecycle calls themselves necessarily enqueue trace-control
  work; surrounding input writes, output reads, events, and synchronization must be separate CQ commands outside the
  captured/replayed command stream. They may be ordered before or after the replay on the same CQ, or coordinated across
  CQs with events outside capture.
- When debugging a model built on `models/common_moreh`, use the shared
  `models/common_moreh/tensor_dump.py` infrastructure instead of adding an ad hoc dump path. Publish a stable semantic
  point with `capture_tensor(...)` and use the existing `TensorDumpMixin`/generator integration. It captures a
  `ttnn.clone` into a persistent device buffer, retains that handle with the trace, and performs host conversion and
  persistence only after replay. Do not add direct `to_torch`, `.cpu()`, synchronization, or file I/O to model code.
- For a path that cannot use this infrastructure, preserve the same ownership boundary: preallocate a persistent device
  debug tensor before capture and use a warmed-up, traceable device operation to write it. Read it back only after
  `end_trace_capture`, or enqueue the read after `execute_trace` as a following CQ command, then synchronize outside the
  trace. Complete the host snapshot before another replay can overwrite the retained buffer.

### Authoritative steady-state latency for an individual op

For an individual TTNN op repeatedly executed with fixed shapes and buffer addresses, use amortized trace-replay wall
time as the authoritative steady-state latency. This result represents warmed-up execution with dispatch overhead
amortized, as in model trace execution. It is not cold-start latency or the end-to-end latency of an ordinary Python API
call.

Measure it in a fresh process as follows:

1. Leave `TT_METAL_DEVICE_PROFILER` unset or set it to `0`, then execute the op at least once to complete JIT compilation
   and program-cache preparation.
2. Begin trace capture and enqueue the same op `N` times, where `N > 10`, using the shapes and device-buffer addresses that
   replay will retain.
3. End capture, then synchronize the device before timing.
4. Record the start time.
5. Replay the captured trace `M` times with `blocking=False`, where `M > 10`. Do not synchronize between replays.
6. After the final replay, synchronize the device once and record the end time.
7. Compute `time_per_op = elapsed_time / (N * M)`.

Device-profiler instrumentation changes execution, especially CCL performance, so profiler-enabled wall time is not an
authoritative latency result. A host wall-clock measurement without trace replay includes variable dispatch, Python,
filesystem, and other host overhead; do not interpret it as device-op performance.

Report `N`, `M`, profiler state, replay blocking setting, every synchronization position, input and output shapes, memory
configurations, and device topology with each result. Also record any program configuration or buffer-layout condition
needed to reproduce the measurement.

### Tracy attribution

Use Tracy only when per-op or per-kernel attribution is required. Run it in a separate fresh process with
`TT_METAL_DEVICE_PROFILER=1`; do not reuse that process's wall time as the trace-replay latency result. Keep inputs,
shapes, program configurations, caller-owned buffers, warmup, and replay structure matched between the latency and
attribution processes. Runtime profiler options are process-global and read at startup, so changing the environment after
TT-Metal initialization does not establish a clean comparison.

Run `python -m tracy -r -p -v main.py`; Tracy prints the generated CSV path on completion. Relevant CSV columns are index
0 = OP CODE, 1 = OP TYPE, 2 = GLOBAL CALL COUNT, 3 = DEVICE ID, and 18 = DEVICE KERNEL DURATION [ns]. When analyzing,
filter to rows whose DEVICE ID is `0` or empty and extract those five columns. Write a parsing script as needed rather than
using a fixed one.

Tracy device-kernel duration can be smaller than actual op execution time because it excludes firmware time. Device
firmware duration can instead overestimate execution when it spans inter-core start or completion skew. Use both only for
attribution and diagnosis, never as authoritative op latency.

A device-profiler process must use one mesh-device lifetime. Open the mesh device before profiled work and close it only
after every profiled case and profiler drain in that process completes. Never close and reopen a mesh device in the same
profiler-enabled process. If cases require independent mesh-device fixtures or device configurations, expose them as
separately invocable test nodes and run each node in a fresh Tracy process.

## Heehoon's tt-metal Kernel Guide

These rules are intentionally stricter than necessary to reduce mistakes by AI agents.

### General kernel rules

- When writing or modifying TT data-movement kernels, use the Device 2.0 APIs from `tt_metal/hw/inc/api/` rather than legacy data-movement APIs. Follow the [Device 2.0 Data Movement API Migration Guide](https://github.com/tenstorrent/tt-metal/blob/main/docs/source/tt-metalium/tt_metal/apis/kernel_apis/data_movement/device_api_migration_guide.md). Legacy API names elsewhere in these instructions express required behavior only; use their Device 2.0 equivalents in code.
- Never use `invalidate_l1_cache()`.
- Any kernel that issues asynchronous NoC atomics, including semaphore increments, must call `noc_async_atomic_barrier()` after those operations and before the kernel ends.
- Any kernel that issues asynchronous NoC writes must call `noc_async_write_barrier()` after those operations and before the kernel ends.
- Align every NoC transaction to 32 bytes:
  - `src_addr % 32 == dst_addr % 32` is a hard requirement.
  - `size % 32 == 0` is a strong default, not a hard requirement; some operations intentionally use transaction sizes that are not divisible by 32.
- Semaphores are automatically initialized to their configured initial value at the start of the kernel. Do not set them again explicitly; doing so can create races, for example when another core has already sent an increment that then gets overwritten by a set.
- Calling `get_semaphore(id)` for a semaphore that is not allocated on the current core (only on other cores) is wrong.
- Be careful when accessing another core's circular buffer over NoC, especially when that CB is not allocated on the current core. TODO: clarify the correct way to obtain a remote core's CB address.
- For `NocUnicastAtomicIncFusedCommandHeader`, `flush = true` is a performance optimization that waits only for write data to depart before sending the atomic increment. It does not replace the required `noc_async_write_barrier()` before the kernel ends; the atomic also requires `noc_async_atomic_barrier()` before the kernel ends.
- `transpose_wh_dest` is face-wise transpose by default.
- With `matmul_block`, even when `transpose = true`, the B segment (`ct_dim * kt_dim`) is expected to occupy continuous CB slots; the A segment may use `kt_dim` stride.
- `pack_tile` and `pack_tile_block` auto-advance the output tile index by default.
  - For an arbitrary `output_tile_index`, pass `out_of_order_output = true` to `pack_tile`.
- Choose argument types as follows:
  - If values differ across cores, use runtime args.
  - If values are common across cores but can differ run-to-run (for example, tensor addresses), use common runtime args.
  - Otherwise, use compile-time args.
- Do not use a custom `compute_program_hash`. If possible, do not define one; rely on the default hash.

### Multicast

For multicast, use this pattern:

```cpp
noc_async_write_multicast(...);
noc_semaphore_set_multicast(...);
noc_async_write_barrier();
```

The write operations are ordered, so do not put a barrier between the data write and the semaphore write.

TODO: document virtual coordinates, physical coordinates, and the `noc0`/`noc1` reversal rules.

### Unit tests

When adding an op, implement these tests by default:

- `op_correctness`
- `op_performance`: follow the authoritative steady-state trace-replay measurement contract above.

The `op_breakdown` test and its L1 debug tensor interface are optional; implement them only when explicitly instructed. When requested, include an interleaved L1 debug tensor shaped like `[num_cores, num_slots]`; write values as `debug_l1[slot] = x`. Keep this simple; do not use a fancy `TensorAccessor` here.

### Circular buffers

- Never call `cb_push_back` or `cb_pop_front` from multiple threads. CB write/read pointers are not synchronized across threads (see the comment in `cb_api.h`).
- `cb_reserve_back` and `cb_wait_front` are counter-only blocking waits; they do not advance CB pointers or record a physical span. Their requested page count may logically cross the CB wrap boundary, up to the CB's total capacity. Repeated `cb_wait_front` calls without a paired pop use cumulative counts.
- `cb_push_back` and `cb_pop_front` advance the physical write/read pointers. A single call may reach the physical CB limit exactly and wrap, but must not advance past it. Split pointer-advancing operations at the boundary, and ensure push/pop amounts over one complete cycle sum exactly to the CB size.
- A cross-boundary reserve/wait proves only free/available page credit; it does not make the underlying pages physically contiguous. Split actual memory accesses and their corresponding push/pop operations into boundary-safe chunks.

### Accessing tensors

- Almost always use `TensorAccessor`.

### Compute kernels

- Never use `acquire_dst` or `release_dst`.
- Use `tile_regs_acquire`, `tile_regs_commit`, `tile_regs_wait`, and `tile_regs_release`.
- For FPU ops, always precede the operation with reconfiguration and init, for example:

```cpp
reconfig_data_format(cb_m_local, cb_m_local);
copy_tile_to_dst_init_short(cb_m_local);
copy_tile(cb_m_local, 0, 0);
```

- For SFPU ops, always precede the operation with init, for example:

```cpp
exp_tile_init</*approx=*/false, scale_fp32>();
exp_tile</*approx=*/false, /*scale_en=*/true>(0, static_cast<int>(VectorMode::RC), scale_bf16);
```

## Long-running experiments

When running long experiments, print process output intermittently so the user can distinguish progress from a hang.
Also never wait by sleeping with estimated time. The result should be checked immediately after the experiment ends.
Never wait with tail because it only print result after completion, so it makes you cannot check progress.

## Hang detection and device recovery

These hang-detection rules apply only while running TT device workloads (for example, long-running experiments after opening devices or launching device-backed tests). For ordinary host-side work such as `pip`/`uv` installs, dependency resolution, git operations, or other CPU-only commands, use task-appropriate judgment instead of device-hang recovery rules.

If no JIT compilation is running (no `cc1plus` process — only `python`) and there has been no output for more than a minute during an already-running TT device workload, assume the device may be hung. This rule does **not** apply while the process is still in device/runtime initialization (for example importing TTNN, opening devices, initializing Fabric, topology discovery, hugepage setup, or first-time test collection that probes devices). During initialization, wait for a clear runtime failure, a command timeout, or explicit evidence that initialization has stopped progressing before treating it as a device hang.

Galaxy reset can legitimately take several minutes and may produce no output while it is progressing. While the reset process is alive and its own timeout has not expired, do not classify it as hung merely because a generic no-output watchdog elapsed.

Treat an unusually slow reset, or a stall/failure while opening devices after a successful reset, as a device/setup failure on its first occurrence rather than evidence of a branch regression. Briefly report the observed stage and impact, stop any live process before resetting, then reset and retry once under the normal lock protocol unless the task plan or user specifies a different retry budget. Do not count the failed setup attempt as a measurement. Attribute the failure to the branch only when it reproduces from a known-good device state or other evidence connects it to the code; if the device/setup failure repeats, report it as an infrastructure blocker and preserve the relevant logs.

Do not reset underneath a live process that is still initializing or still owns UMD/device mappings. If a reset is needed for a hung TT workload, keep the lock held, stop or let the workload process exit (or run triage from the same lock context when appropriate), then reset and retry.

Also reset the device (without releasing the lock) whenever it appears to be in an invalid state during TT device usage.

Always reset after acquiring the lock to clear state modified by other users.

On a multi-Galaxy server, bound each Galaxy reset attempt to five minutes. Treat
an attempt that exceeds this bound or returns an incomplete Ethernet endpoint
count as an unsuccessful setup attempt.

Start with the Galaxy systems selected for the workload. If that reset is
unsuccessful on a four-Galaxy cluster, confirm that all four nodes have no live
UMD/device mappings, acquire the cluster-wide whole lock, and reset all four
Galaxy systems together. If a narrower lock is held, release it before waiting
for the cluster-wide whole lock; if the cluster-wide whole lock is already
held, keep it while expanding the reset to all four systems. This full-cluster
reset reinitializes Ethernet links to unused neighboring nodes that can
otherwise remain incomplete. If any member of the full-cluster reset exceeds
five minutes, end that reset attempt while retaining the whole lock and run
the full-cluster reset again. Start the workload after the required device
counts and Ethernet endpoints are healthy.

### Choosing the reset command

When working with tt-metal, always use `moreh-smi` for reset commands. Never use
`tt-smi` to reset devices during tt-metal development.

- For tt-metal work on a Galaxy host (hostname is in `moreh-lock`'s hostname-to-slack-channel map): use `moreh-smi -glx_reset` for a whole-Galaxy reset.
- For tt-metal work on a non-Galaxy host (e.g. `ttdev14`): use `moreh-smi -r` with **no** device index. Never pass `-r <index>` on a non-Galaxy host — it can leave the card in a worse state.

When working with a project other than tt-metal (for example, tt-latem), using
`tt-smi` to reset devices is allowed unless repo-local instructions say
otherwise.

## EvalScope metrics

Never use, report, compare, or draw conclusions from EvalScope's `Spec. Accept Rate`. It is an approximation inferred from streaming behavior, not the model runtime's real speculative-token acceptance rate. Use only acceptance metrics measured directly by the model or runtime.

## Misc.

- In TT dataflow kernels, avoid tiny unaligned NOC reads/writes for scalar fields in interleaved tensors or L1 buffers. Read/write an aligned 32-byte (or larger aligned) chunk into scratch, then index the scalar locally. For example, reading one int32 from `TensorAccessor::get_noc_addr(page, elem * sizeof(int32_t))` or an `InterleavedAddrGen` with a 4-byte size can silently fetch the wrong value on device; align the offset down and transfer at least 32 bytes.
- In TT ops, allocate internal L1 scratch/persistent workspace as circular buffers (`CircularBufferConfig` + `CreateCircularBuffer`) and pass/access them by CB index with `get_read_ptr`/`get_write_ptr`; do not allocate scratch L1 with `CreateBuffer(BufferType::L1)` unless you are intentionally creating a real tensor-like/runtime buffer and have verified the pattern in nearby ops. For manually managed L1 storage that is not a tensor, do raw address math from the CB base and explicit NOC coordinates; do not use `TensorAccessor`/`InterleavedAddrGen` on non-tensor scratch, because page/bank mapping can return garbage.
- In TT Fabric dataflow kernels, allocate packet-header CBs with exact fabric header page size `tt::tt_fabric::get_tt_fabric_packet_header_size_bytes()` (96 bytes on the current 2D torus route-buffer-size-35 path) and enough pages for every simultaneously live header. One page is sufficient when a core uses only one header/route at a time, such as a lane choosing either north or south; allocate multiple pages only when the same core keeps multiple headers live concurrently. `RawUInt32` matches common fabric examples, but `UInt32` also works when the page size is exact; do not infer a fabric hang is caused by dtype before isolating semaphore scope and header page/slot sizing.
- For TT Fabric barriers or fabric atomics that use global semaphores, create/pass the semaphore on every core that will read or increment it, including fabric/link-worker cores. Do not create a global semaphore only on logical `(0,0)` when the barrier runs on a separate fabric core row/column. For local semaphores from `CreateSemaphore`, use a `CoreRangeSet` that includes all participating cores.
- In TT dataflow kernels, when using NoC writes followed by a semaphore signal (unicast or multicast), issue the data writes first and then the semaphore increment/set without putting a barrier between them. Before the kernel ends, drain every issued operation with the applicable barrier: `noc_async_write_barrier()` for writes and `noc_async_atomic_barrier()` for atomics such as semaphore increments. A fused-command `flush` does not replace the final write barrier.
- In TT compute kernels, initialize and reconfigure explicitly before every operation family. Put `compute_kernel_hw_startup(...)` near the start as the whole-kernel init. Before `copy_tile`, reconfigure SrcA for the input CB and run the copy init (for example `reconfig_data_format_srca(...)`/`reconfig_data_format(...)` then `copy_tile_to_dst_init_short...`). Before `pack_tile`, call `pack_reconfig_data_format(...)` for the destination CB. Before `tilize_block`/`untilize_block`, run the matching `tilize_init...`/`untilize_init...` with the correct data formats and packer config; do not assume a previous op left unpack/math/pack state valid.
- Instead of magic numbers, derive them from existing constants such as ttnn.TILE_SIZE and the ones in tt-metalium/constants.hpp if possible.
- When making a git commit, never co-author.
- Ignore the message in the other people's lock.
