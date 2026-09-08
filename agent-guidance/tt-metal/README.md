# Basic TT-Metal guidance

Read this guide before TT-Metal builds, imports, tests, device workloads, or
MPI/shared-cache setup. Use the active checkout and the session's current host;
follow `AGENTS.md` for execution location and shared default asset policy.

## Building

Always use `./build_metal.sh -ce` to compile tt-metal. Never use cmake directly, and never use a unity build. After changing tt-metal source code, complete this build before running tests or device workloads; do not rely on judging whether JIT compilation is sufficient.

Separately, activate the active checkout's virtual environment for tt-metal build, test, import, and workload commands, so they resolve dependencies from that checkout rather than another one:

```bash
source "<absolute path to the active tt-metal checkout>/python_env/bin/activate"
```

If that environment does not exist, create it with `./create_venv.sh` first, then activate it. `create_venv.sh` defaults to `./python_env`, but a checkout may use a different directory such as `.venv`; activate the one that checkout actually has. Activating a virtual environment never replaces the system `moreh-lock`.

### Environment variables

Before building, testing, importing, or running tt-metal, set the environment for the exact tt-metal checkout being used. Be especially careful with worktrees: `TT_METAL_HOME` must point to the active tt-metal worktree, not another checkout. Set all of the following:

```bash
export TT_METAL_HOME="<absolute path to the tt-metal checkout or worktree in use>"
export TT_METAL_RUNTIME_ROOT="${TT_METAL_HOME}"
export PYTHONPATH="${TT_METAL_HOME}:${TT_METAL_HOME}/ttnn:${TT_METAL_HOME}/tools"
```

## Test organization

- Put standalone device-operation tests in `tests/ttnn/unit_tests/operations/moreh`.
- Put tests for model-internal modules under `models/demos/<moreh implementation>/tests`.
- Use `test_<op_or_module>.py` as the base filename. Append purpose suffixes before
  `.py`, such as `test_<op_or_module>_perf.py` or `test_<op_or_module>_util.py`.

Before designing or running performance tests, read [trace capture and profiling](profiling.md).

## Device locking

This process is required when using shared team device infrastructure. Run `moreh-lock status` to confirm that the current host is registered; it reports the node and its current holder.

`moreh-lock` is a system installation at `/usr/local/bin/moreh-lock`, independent of any tt-metal checkout. Never vendor, install, or invoke a checkout-local copy. tt-metal removed its bundled `tools/moreh_lock`, so a `moreh-lock` inside a checkout virtual environment is a stale console script that shadows the system binary and fails with `ModuleNotFoundError: No module named 'moreh_lock'`. Delete such a shim rather than working around it. The system wrapper runs Python with `-I`, so a tt-metal `PYTHONPATH` cannot shadow the package once the shim is gone.

Exception: `vllm-tt-moreh` test scripts acquire and release the device lock internally. When running those test scripts, do not acquire `moreh-lock` manually outside the script.

### Running device commands

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

Ignore the message in other people's locks.

## Device reset

Always reset after acquiring the lock to clear state modified by other users.

Do not reset underneath a live process that is still initializing or still owns UMD/device mappings. If a reset is needed for a hung TT workload, keep the lock held, stop or let the workload process exit (or run triage from the same lock context when appropriate), then reset and retry.

Also reset the device (without releasing the lock) whenever it appears to be in an invalid state during TT device usage.

When working with tt-metal, always use `moreh-smi` for reset commands. Never use
`tt-smi` to reset devices during tt-metal development.

- For tt-metal work on a Galaxy host (hostname is in `moreh-lock`'s hostname-to-slack-channel map): use `moreh-smi -glx_reset` for a whole-Galaxy reset.
- For tt-metal work on a non-Galaxy host (e.g. `ttdev14`): use `moreh-smi -r` with **no** device index. Never pass `-r <index>` on a non-Galaxy host — it can leave the card in a worse state.

When working with a project other than tt-metal (for example, tt-latem), using
`tt-smi` to reset devices is allowed unless repo-local instructions say
otherwise.

On a multi-Galaxy server, bound each Galaxy reset attempt to five minutes. Treat
an attempt that exceeds this bound or returns an incomplete Ethernet endpoint
count as an unsuccessful setup attempt.

Read [debugging and recovery](debugging.md) before diagnosing a device hang,
an initialization failure, or an unsuccessful reset. That guide defines the
hang-detection thresholds, retry budget, and multi-Galaxy reset escalation.

## MPI and shared filesystems

- Never change `HOME` to isolate per-rank or per-job artifacts. `HOME` is a session-wide input that may also determine unrelated runtime paths such as cluster descriptors, launch manifests, configuration, credentials, logs, and caches. Use the dedicated cache or artifact variable instead (for example, `TT_METAL_CACHE` for the tt-metal JIT cache).
- Before assuming that equal path strings collide, verify the filesystem type and mount identity on every participating host. The same path on host-local filesystems names separate objects; on NFS or another shared filesystem it may name the same object.
- On a shared writable cache, namespace the dedicated cache path by both launch identity (for example, host set, job ID, or configuration fingerprint) and MPI rank. Rank is unique only within its MPI world, so independent jobs can both have ranks 0 through N-1.
- Before device work, verify the effective host set, MPI world/rank, and relevant paths in every rank. Audit all consumers and SSH/MPI propagation before overriding any process-global environment variable, and keep shared runtime metadata on explicit stable paths.

## Deeper topics

Read these references before the corresponding work:

- [Kernel and op development](kernels.md): editing or reviewing kernels or ops.
- [Debugging and recovery](debugging.md): immediately when a TT device experiment
  takes unexpectedly long, or when diagnosing device hangs, initialization
  failures, or unsuccessful resets, including multi-Galaxy reset escalation.
- [Trace capture and profiling](profiling.md): planning or implementing device-op
  or model-module optimization and performance tests; TTNN capture/replay,
  trace-safe tensor debugging, profiling, and performance measurement or interpretation.
- [EvalScope metrics](evalscope.md): interpreting speculative acceptance.
