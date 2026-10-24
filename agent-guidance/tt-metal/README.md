# Basic TT-Metal guidance

Read before TT-Metal builds, imports, tests, workloads, or MPI/shared-cache setup.
Use the active checkout and current host under `AGENTS.md`'s execution-location
and shared-asset policies.

## Build and environment

Follow the build command and test conventions in the
[team development policy](../team-development.md).

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

Use the test locations and naming rules from the loaded team development policy.
Read [profiling](profiling.md) before performance-test design or execution.

## Device ownership and recovery

Before device access, load the [team development policy](../team-development.md)
for the site reservation, launcher, reset, and recovery procedures. Missing or
unverified policy blocks device work. Preserve exclusive ownership through device
activity and required cleanup; never reset another owner's device.

Read [debugging](debugging.md) immediately for unexpected workload delay,
initialization failure, or reset failure.

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
