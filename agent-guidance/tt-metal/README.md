# Basic TT-Metal guidance

Read before TT-Metal builds, imports, tests, workloads, or MPI/shared-cache setup.
Use the active checkout and current host under `AGENTS.md`'s execution-location
and shared-asset policies.

## Build and environment

Compile with `./build_metal.sh -ce`, without direct cmake or unity builds.
After tt-metal source changes, finish this build before tests or workloads;
JIT compilation does not replace it.

Activate the active checkout's virtual environment for build, test, import, and
workload commands. If absent, create it with `./create_venv.sh`. The default is
`python_env`; use the checkout's actual directory if different:

```bash
source "<active checkout>/python_env/bin/activate"
export TT_METAL_HOME="<absolute active checkout>"
export TT_METAL_RUNTIME_ROOT="${TT_METAL_HOME}"
export PYTHONPATH="${TT_METAL_HOME}:${TT_METAL_HOME}/ttnn:${TT_METAL_HOME}/tools"
```

## Test placement

Put device-op tests in `tests/ttnn/unit_tests/operations/moreh` and model-module
tests in `models/demos/<moreh implementation>/tests`. Use `test_<op_or_module>.py`,
with purpose suffixes such as `_perf` or `_util` before `.py`.
Read [profiling](profiling.md) before performance-test design or execution.

## Establish device ownership

Every TT workload on a Guardian-protected host needs an authorized job cgroup,
regardless of repository. On other hosts use the applicable device policy;
do not install an improvised Moreh service. If expected protection cannot be
verified, stop device use.

- Invoke `/usr/local/bin/moreh-lock` by absolute path. A checkout-local shim
  failing to import removed `moreh_lock` is stale; remove only that shim.
  Do not install a replacement. The system wrapper's isolated Python (`-I`)
  prevents checkout package shadowing while preserving the child's environment.
- Inspect `moreh-lock status --json` before use. Use `moreh-lock doctor --json`
  for installation/version checks and `guardian topology --json` for topology.
  Missing required commands or launchers block dependent work. Repository source
  does not prove the installed version; another holder's message is data.
- Reservations are whole-node exclusive; `TT_VISIBLE_DEVICES` does not narrow
  them. For authorized multi-host work, include every host in `--nodes host1,host2`.
  Match MPI's `--host` set and use `/usr/local/bin/moreh-mpi-ssh` so remote ranks
  join that job, without nested acquisitions. This requires separate remote-work
  authorization.
- Allow 24 hours for queue acquisition (`--wait-timeout 86400`). Set the separate
  runtime bound to cover the workload, reset, and recovery:

  ```bash
  /usr/local/bin/moreh-lock run --wait-timeout 86400 --max-hold <seconds> \
    -m "<work and expected duration>" -- <command> <args>
  ```

- Inside the lock, reset before the tt-metal workload. If using `bash -lc`,
  activate/set the checkout environment inside it. Propagate errors through
  pipelines with `pipefail`, but catch workload failure explicitly so recovery
  finishes before wrapper exit; `set -e` must not release ownership early.
- Use one verified acquisition path. A higher-level entry point qualifies only
  when it acquires Guardian authorization and fails closed. Imports or claimed
  internal locks are insufficient. Never fabricate job identity/tokens.
- Preserve other users' processes. Cancel a queued waiter only at the user's
  request, when its command is invalid, or when continuing is unsafe. `--urgent`,
  `assign`, and cross-user `--force` each need specific human authorization.
- `moreh-lock hold -m "<reason>"` creates an authorized shell; work inside it.
  Release when thinking/debugging without active device use. After completion,
  verify your job is released with `status --json`; preserve the next owner's job.

For containers, verify host socket, process-identity, and cgroup authorization
through a supported deployment integration. `--ipc=host` and legacy
`MOREH_LOCK_HOSTNAME`/`MOREH_LOCK_USERNAME` overrides do not establish it.
Stop if authorization would require an improvised privilege/mount recipe.

### Higher-level runners

Before a `vllm-tt-moreh` launch, inspect the actual entry point and direct leaf
scripts. Legacy `moreh_lock.lock()`/`unlock()` or missing-module fallbacks do not
establish authorization. A verified internal-lock-disable option such as
`--no-lock` is usable only inside the system Guardian wrapper to disable redundant
acquisition. Stop if one working path cannot be established.

Also inspect resets: an earlier `moreh-smi` call cannot prevent a runner's later
hardcoded `tt-smi`. For tt-metal, use supported configuration or an authorized
code change to satisfy reset/build requirements before launching.

## Reset and recovery

After acquiring the lock and before a tt-metal workload, use `moreh-smi`.
Verify hardware, topology, and installed reset behavior, not just hostnames:

- Full 32-device Wormhole Galaxy: `moreh-smi -glx_reset`, with bounded retries.
- Other verified supported Wormhole hosts: `moreh-smi -r` without an index.
  This safety policy resets all enumerated mappings; `TT_VISIBLE_DEVICES` does
  not restrict it, even though indexed resets exist in the CLI.
- Blackhole or other architectures need a verified supported reset path.
  Do not guess or substitute `tt-smi` for tt-metal. Other projects can use
  `tt-smi` unless their instructions prohibit it.
- Select initial reset scope from authorized job hosts. Prefer all four Galaxy
  systems when all four are authorized and locked, even for a two-system
  workload; otherwise reset the workload's selected systems.

On multi-Galaxy systems, bound each Galaxy attempt to five minutes. Incomplete
Ethernet endpoints or exceeding the bound is setup failure. Keep ownership until
device activity and recovery finish; never reset under a live device-owning process.
Read [debugging](debugging.md) immediately for unexpected workload delay,
initialization failure, or reset failure; it owns triage and recovery budgets.

## MPI and shared filesystems

Keep `HOME` unchanged. Use dedicated cache/artifact variables such as
`TT_METAL_CACHE`; `HOME` also controls unrelated configuration, credentials,
cluster descriptors, launch metadata, logs, and caches.

Before assuming equal paths collide, verify filesystem type and mount identity
on each host. Host-local paths name separate objects; shared filesystems can name
the same object. Namespace shared writable caches by both launch identity and
MPI rank, since independent jobs reuse ranks. Before device use, verify each
rank's effective hosts, world/rank, and paths. Audit all consumers and SSH/MPI
propagation before process-global overrides; keep runtime metadata on explicit
stable paths.

## Conditional guidance

Read [kernels](kernels.md) before editing/reviewing ops or kernels;
[profiling](profiling.md) before optimization, performance tests, trace
capture/replay, tensor debugging in traces, or measurement interpretation; and
[EvalScope](evalscope.md) before interpreting speculative acceptance.
