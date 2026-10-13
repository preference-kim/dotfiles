# TT device debugging and recovery

Read the [basic guide](README.md) before device work. Its lock ownership and
reset-command rules apply throughout diagnosis and recovery. Read
[trace capture and profiling](profiling.md) before debugging a captured/replayed
TTNN path or interpreting performance measurements.

These hang-detection rules apply only while running TT device workloads (for example, long-running experiments after opening devices or launching device-backed tests). For ordinary host-side work such as `pip`/`uv` installs, dependency resolution, git operations, or other CPU-only commands, use task-appropriate judgment instead of device-hang recovery rules.

When a TT device experiment takes unexpectedly long, immediately inspect its
current phase, process activity, and output using this guide. Switch to diagnosis
before continuing to wait or retry; elapsed time alone does not establish a hang.

## Triage a stalled workload

If an already-running TT workload produces no output for more than a minute, inspect the active toolchain processes for ongoing JIT compilation. For GCC, this includes `cc1plus`. If compilation is absent, investigate a possible device hang. This is a diagnostic threshold, not proof of a hang. This rule does **not** apply while the process is still in device/runtime initialization (for example importing TTNN, opening devices, initializing Fabric, topology discovery, hugepage setup, or first-time test collection that probes devices). During initialization, wait for a clear runtime failure, a command timeout, or explicit evidence that initialization has stopped progressing before treating it as a device hang.

For a suspected workload hang, keep the existing device lock and collect live
state before terminating the workload or resetting the device. From the active
checkout, with its environment activated, start with:

```bash
python tools/tt-triage.py --run=dump_running_operations
```

Read the active checkout's `tools/triage/tt-triage.md` for additional checks and
arguments needed to target the workload. Preserve the command output and workload
logs. If triage fails, report the failure and retained evidence before recovery;
do not reset underneath a live workload or another device-owning process.

## Initialization and reset recovery

Galaxy reset can legitimately take several minutes and may produce no output while it is progressing. While the reset process is alive and its own timeout has not expired, do not classify it as hung merely because a generic no-output watchdog elapsed.

Treat an unusually slow reset, or a stall/failure while opening devices after a successful reset, as a device/setup failure on its first occurrence rather than evidence of a branch regression. Briefly report the observed stage and impact, stop any live process before resetting, then reset and retry once under the normal lock protocol unless the task plan or user specifies a different retry budget. Do not count the failed setup attempt as a measurement. Attribute the failure to the branch only when it reproduces from a known-good device state or other evidence connects it to the code; if the device/setup failure repeats, report it as an infrastructure blocker and preserve the relevant logs.

If a narrower reset fails, use a full-cluster reset only when all four hosts
are authorized for the job. Release a narrower lock before waiting for the
cluster-wide whole lock. Keep that lock if already held. With all target locks
held, confirm no target has live UMD/device mappings before resetting.
A full-cluster reset reinitializes Ethernet links to unused neighbors that can
otherwise remain incomplete. Apply the [execution-location rule](../../AGENTS.md#execution-location) to every reset.

End a failed reset attempt before retrying within the budget above.
Retain the full-cluster lock during recovery. Start the workload after the
required device counts and Ethernet endpoints are healthy.
