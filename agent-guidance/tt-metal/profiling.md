# TTNN trace and performance measurement

Read before op/module optimization, performance-test design, TTNN trace
capture/replay, or measurement and profiling. A delayed device experiment first
needs [debugging](debugging.md)'s locked triage.

For performance baselines, unset `TT_METAL_DEVICE_PROFILER` and run without Tracy.
Instrumentation can reduce communication-kernel performance. Enable profiling
only for required timing/zone diagnosis in a separate process.

## Capture only traceable dispatch

Capture warmed-up, nonblocking device-program dispatch with fixed shapes and
buffer addresses. Capture puts every physical device's system-memory manager in
bypass mode, so the restriction covers every host CQ on the mesh, not only the
CQ with the active trace ID.

Between `begin_trace_capture` and `end_trace_capture`, enqueue only the intended
device operations. Compile/warm them beforehand and retain replay buffers at
fixed addresses. Host-CQ work belongs outside capture and the replayed stream:
transfers, buffer/core reads or writes, `.cpu()`/`to_torch()`, finish/synchronization,
events, profiler drains, and equivalent work hidden in helpers/callbacks.

Use `execute_trace(..., blocking=False)`. Trace lifecycle calls enqueue their
required control work; surrounding input/output, events, and synchronization
remain separate CQ commands. Order them before/after replay on the same CQ or
coordinate CQs with events outside capture.

For project-specific debug helpers, load the
[team development policy](../team-development.md).

For a generic trace-safe approach, preallocate persistent debug tensors, write with warmed-up traceable
device ops, and read only after capture or as a CQ command following replay.
Synchronize outside the trace and finish the host snapshot before another replay
can overwrite the retained buffer.

## Measure steady-state op latency

For fixed-shape, fixed-address repeated TTNN ops, authoritative steady-state
latency is amortized trace-replay wall time. It includes completion while
amortizing dispatch and host timing overhead, and excludes compilation. It does
not represent cold start or ordinary Python API end-to-end latency.

Use a fresh process with the baseline settings above.

1. Execute the op at least once to complete JIT/program-cache preparation.
2. Capture `N > 10` executions with replay's shapes and buffer addresses.
3. End capture, warm up replay, and synchronize before starting a monotonic timer.
4. Enqueue `M > 10` replays with `blocking=False`, without intervening synchronization.
5. Synchronize once after the final replay, stop timing, and compute
   `time_per_op = elapsed_time / (N * M)`.

Define valid replay/state-reset behavior for stateful ops. Retain inputs and
outputs throughout queued work. Release the trace before its buffers after work
completes, including on failure; a hang needs locked recovery first.

Report `N`, `M`, profiler state, blocking setting, every synchronization position,
input/output shapes, memory and program configuration, buffer layout, and device
topology needed to reproduce the result. Profiler-enabled wall time is not this
latency. Ordinary non-trace host timing includes variable dispatch, Python,
filesystem, and other overhead and does not establish device-op performance.

## Attribute with Tracy

Use a separate fresh process with `TT_METAL_DEVICE_PROFILER=1` only when per-op
or per-kernel attribution is needed. Match the baseline's inputs, shapes,
program configuration, caller-owned buffers, warmup, and replay structure.
Profiler options are process-global at startup; changing the environment after
initialization does not create a clean comparison.

Run `python -m tracy -r -p -v main.py` and use the CSV path in its output.
Parse with `csv.DictReader` by header name, requiring `OP CODE`, `OP TYPE`,
`GLOBAL CALL COUNT`, `DEVICE ID`, and `DEVICE KERNEL DURATION [ns]`.
Report missing headers; `DEVICE FW DURATION [ns]` is a separate metric.

Filter device ID `0` or empty only for an explicitly selected single-device
view. Otherwise retain/identify all relevant devices. An empty ID does not prove
a device-kernel event. Kernel duration excludes firmware and can undercount op
time; firmware duration can overcount due to inter-core start/completion skew.
Use both for diagnosis, not authoritative latency.

## Keep one profiled mesh lifetime

A profiler-enabled process must open one mesh and close it only after all cases
and profiler drains finish. Closing then reopening can hang initialization.
Cases can share that lifetime only with compatible device configuration.
For independent configurations or function-scoped pytest fixtures, expose
separately invocable nodes and run each exact parameterized node in a fresh
Tracy process.
