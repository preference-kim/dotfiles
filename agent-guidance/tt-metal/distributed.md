## MPI and shared filesystems

- Never change `HOME` to isolate per-rank or per-job artifacts. `HOME` is a session-wide input that may also determine unrelated runtime paths such as cluster descriptors, launch manifests, configuration, credentials, logs, and caches. Use the dedicated cache or artifact variable instead (for example, `TT_METAL_CACHE` for the tt-metal JIT cache).
- Before assuming that equal path strings collide, verify the filesystem type and mount identity on every participating host. The same path on host-local filesystems names separate objects; on NFS or another shared filesystem it may name the same object.
- On a shared writable cache, namespace the dedicated cache path by both launch identity (for example, host set, job ID, or configuration fingerprint) and MPI rank. Rank is unique only within its MPI world, so independent jobs can both have ranks 0 through N-1.
- Before device work, verify the effective host set, MPI world/rank, and relevant paths in every rank. Audit all consumers and SSH/MPI propagation before overriding any process-global environment variable, and keep shared runtime metadata on explicit stable paths.
