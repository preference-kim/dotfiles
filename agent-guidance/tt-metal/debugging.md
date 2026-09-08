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

If no JIT compilation is running (no `cc1plus` process — only `python`) and there has been no output for more than a minute during an already-running TT device workload, assume the device may be hung. This rule does **not** apply while the process is still in device/runtime initialization (for example importing TTNN, opening devices, initializing Fabric, topology discovery, hugepage setup, or first-time test collection that probes devices). During initialization, wait for a clear runtime failure, a command timeout, or explicit evidence that initialization has stopped progressing before treating it as a device hang.

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
