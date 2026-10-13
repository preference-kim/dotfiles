# TT device debugging and recovery

The [basic guide](README.md) owns device locks and reset commands. Read it before
device work, and [profiling](profiling.md) before trace-path debugging or
performance interpretation. These hang rules apply to TT device workloads,
not host-only installation, dependency resolution, or Git work.

## Diagnose before recovery

When a TT experiment takes unexpectedly long, inspect its phase, processes, and
output before waiting or retrying. Elapsed time alone does not establish a hang.
If an executing workload has no output for over a minute, check for active JIT
compilers such as GCC's `cc1plus`. If absent, investigate a possible hang.

During initialization (imports, device opening, Fabric/topology, hugepages, or
device-probing test collection), use a runtime error, command timeout, or evidence
that progress stopped. The one-minute threshold does not apply. A live Galaxy
reset can legitimately be quiet for minutes; respect its own bound.

For a suspected workload hang, retain the lock and collect live state before
termination or reset. In the activated checkout:

```bash
python tools/tt-triage.py --run=dump_running_operations
```

Read `tools/triage/tt-triage.md` for workload targeting and further checks.
Preserve triage output and workload logs. Report triage failure and available
evidence before recovery. Stop every live device-owning process before resetting.

## Restore a known device state

Treat the first unusually slow reset or post-reset device-opening failure as a
setup failure. Report stage and impact; stop the live process, reset, and retry
once under the lock unless the user/task specifies another budget. End each
failed reset attempt before retrying. Exclude failed setup from measurements.
Attribute a branch regression only with reproduction from a known-good device
state or other code-specific evidence. Repeated setup failure is an infrastructure
blocker; retain its logs.

If a narrower reset fails, full-cluster recovery requires all four hosts to be
authorized. Release a narrow lock before waiting for the whole-cluster lock;
retain it if already held. Once all target locks are held, verify there are no
live UMD/device mappings before resetting. This reinitializes Ethernet links to
unused neighbors that can otherwise remain incomplete. Every reset remains
subject to [execution location](../../AGENTS.md#execution-location).

Retain the full-cluster lock during recovery. Launch only after required device
counts and Ethernet endpoints are healthy.
