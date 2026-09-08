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

Follow the [test organization and naming conventions](README.md#test-organization)
for test placement and filenames.

When adding an op, implement these tests by default:

- `op_correctness`
- `op_performance`: follow the authoritative steady-state trace-replay measurement contract in [profiling](profiling.md).

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

### Additional kernel constraints

- In TT dataflow kernels, avoid tiny unaligned NOC reads/writes for scalar fields in interleaved tensors or L1 buffers. Read/write an aligned 32-byte (or larger aligned) chunk into scratch, then index the scalar locally. For example, reading one int32 from `TensorAccessor::get_noc_addr(page, elem * sizeof(int32_t))` or an `InterleavedAddrGen` with a 4-byte size can silently fetch the wrong value on device; align the offset down and transfer at least 32 bytes.
- In TT ops, allocate internal L1 scratch/persistent workspace as circular buffers (`CircularBufferConfig` + `CreateCircularBuffer`) and pass/access them by CB index with `get_read_ptr`/`get_write_ptr`; do not allocate scratch L1 with `CreateBuffer(BufferType::L1)` unless you are intentionally creating a real tensor-like/runtime buffer and have verified the pattern in nearby ops. For manually managed L1 storage that is not a tensor, do raw address math from the CB base and explicit NOC coordinates; do not use `TensorAccessor`/`InterleavedAddrGen` on non-tensor scratch, because page/bank mapping can return garbage.
- In TT Fabric dataflow kernels, allocate packet-header CBs with exact fabric header page size `tt::tt_fabric::get_tt_fabric_packet_header_size_bytes()` (96 bytes on the current 2D torus route-buffer-size-35 path) and enough pages for every simultaneously live header. One page is sufficient when a core uses only one header/route at a time, such as a lane choosing either north or south; allocate multiple pages only when the same core keeps multiple headers live concurrently. `RawUInt32` matches common fabric examples, but `UInt32` also works when the page size is exact; do not infer a fabric hang is caused by dtype before isolating semaphore scope and header page/slot sizing.
- For TT Fabric barriers or fabric atomics that use global semaphores, create/pass the semaphore on every core that will read or increment it, including fabric/link-worker cores. Do not create a global semaphore only on logical `(0,0)` when the barrier runs on a separate fabric core row/column. For local semaphores from `CreateSemaphore`, use a `CoreRangeSet` that includes all participating cores.
- In TT dataflow kernels, when using NoC writes followed by a semaphore signal (unicast or multicast), issue the data writes first and then the semaphore increment/set without putting a barrier between them. Before the kernel ends, drain every issued operation with the applicable barrier: `noc_async_write_barrier()` for writes and `noc_async_atomic_barrier()` for atomics such as semaphore increments. A fused-command `flush` does not replace the final write barrier.
- In TT compute kernels, initialize and reconfigure explicitly before every operation family. Put `compute_kernel_hw_startup(...)` near the start as the whole-kernel init. Before `copy_tile`, reconfigure SrcA for the input CB and run the copy init (for example `reconfig_data_format_srca(...)`/`reconfig_data_format(...)` then `copy_tile_to_dst_init_short...`). Before `pack_tile`, call `pack_reconfig_data_format(...)` for the destination CB. Before `tilize_block`/`untilize_block`, run the matching `tilize_init...`/`untilize_init...` with the correct data formats and packer config; do not assume a previous op left unpack/math/pack state valid.
- Instead of magic numbers, derive them from existing constants such as ttnn.TILE_SIZE and the ones in tt-metalium/constants.hpp if possible.
