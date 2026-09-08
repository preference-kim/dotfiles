## TTNN trace capture, replay, and performance measurement

Read this guide before planning or implementing device-op or model-module
optimization, designing performance tests, or measuring and profiling TTNN work.

By default, unset `TT_METAL_DEVICE_PROFILER` and run performance measurements
without Tracy. Device-profiler instrumentation can lower communication-kernel
performance. Enable it only when device timing or profiling zones are needed for
diagnosis, in a separate process from the performance baseline.

If a device experiment takes unexpectedly long, immediately follow
[device debugging and recovery](debugging.md) for tt-triage and hang detection
before continuing to wait or retry.

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

Warmup excludes compilation and program-cache preparation from timing. Capturing
multiple op executions amortizes the cost of submitting a trace; enqueueing
multiple nonblocking replays avoids a host/device wait after each replay and
amortizes the timer and final synchronization costs. This approximates the
sustained device execution of a traced model while retaining completion time in
the measurement.

Measure it in a fresh process as follows:

1. Unset `TT_METAL_DEVICE_PROFILER`, then execute the op at least once to complete JIT compilation
   and program-cache preparation.
2. Begin trace capture and enqueue the same op `N` times, where `N > 10`, using the shapes and device-buffer addresses that
   replay will retain.
3. End capture, then synchronize the device before timing.
4. Record the start time.
5. Replay the captured trace `M` times with `blocking=False`, where `M > 10`. Do not synchronize between replays.
6. After the final replay, synchronize the device once and record the end time.
7. Compute `time_per_op = elapsed_time / (N * M)`.

Profiler-enabled wall time is not an authoritative latency result. A host wall-clock
measurement without trace replay includes variable dispatch, Python, filesystem,
and other host overhead; do not interpret it as device-op performance.

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

### Device lifetime during profiling

Closing a mesh while device profiling is active and then recreating it can hang
the next device initialization. A device-profiler process must use one mesh-device
lifetime. Open the mesh device before profiled work and close it only after every
profiled case and profiler drain in that process completes. Never close and reopen
a mesh device in the same profiler-enabled process.

Cases may share that lifetime when their device configuration permits it. A
function-scoped pytest mesh fixture closes the device between cases; if cases
require independent fixtures or device configurations, expose separately
invocable test nodes and run each exact parameterized node in a fresh Tracy process.
