# TT device debugging and recovery

The [basic guide](README.md) loads the private device access policy. Read it before
device work, and [profiling](profiling.md) before trace-path debugging or
performance interpretation. These hang rules apply to TT device workloads,
not host-only installation, dependency resolution, or Git work.

## Diagnose before recovery

When a TT experiment takes unexpectedly long, inspect its phase, processes,
and output before waiting or retrying. Apply the phase-specific no-progress
criteria in the [team development policy](../team-development.md); elapsed time
or quiet output alone does not establish a hang.

For a suspected workload hang, retain the lock and collect live state before
termination or reset. In the activated checkout:

```bash
python tools/tt-triage.py --run=dump_running_operations
```

Read `tools/triage/tt-triage.md` for workload targeting and further checks.
Preserve triage output and workload logs. Report triage failure and available
evidence before recovery. Stop every live device-owning process before resetting.

## Restore a known device state

Load the [team development policy](../team-development.md) for retry budgets,
reset scope, and reservation replacement. Keep ownership until device activity
and required cleanup finish. Treat failed setup separately from measurements;
attribute a code regression only with a known-good device baseline or other
code-specific evidence. Preserve failure logs.
