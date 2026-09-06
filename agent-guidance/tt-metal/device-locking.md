## Device Locking

This process is required when using shared team device infrastructure. Confirm that the current host is registered with `moreh-lock`. Run `moreh-lock status` to confirm registration; it reports the node and its current holder.

`moreh-lock` is a system installation at `/usr/local/bin/moreh-lock`, independent of any tt-metal checkout. Never vendor, install, or invoke a checkout-local copy. tt-metal removed its bundled `tools/moreh_lock`, so a `moreh-lock` inside a checkout virtual environment is a stale console script that shadows the system binary and fails with `ModuleNotFoundError: No module named 'moreh_lock'`. Delete such a shim rather than working around it. The system wrapper runs Python with `-I`, so a tt-metal `PYTHONPATH` cannot shadow the package once the shim is gone.

Exception: `vllm-tt-moreh` test scripts acquire and release the device lock internally. When running those test scripts, do not acquire `moreh-lock` manually outside the script.

### Lock command to use

Use the CLI wrapper:

```bash
moreh-lock
```

Before running any command that touches Tenstorrent devices (for example, opening a TT device with `ttnn.open_device` / `ttnn.open_mesh_device`, running TT-backed pytest, profiling TT workloads, etc.), check lock status:

```bash
moreh-lock status
```

Prefer the CLI wrapper for device commands:

```bash
moreh-lock run --wait-timeout 3600 --max-hold <seconds> -m "<what you are doing and expected duration>" -- <command> <args>
```

The lock is node-wide. Reservations are node-exclusive, so two jobs never share a node, and `TT_VISIBLE_DEVICES` selects only which devices the workload uses; it never narrows the lock. To lock several hosts for one job, name every host with `--nodes host1,host2`.

If the command needs shell features, wrap it with `bash -lc`:

```bash
moreh-lock run --wait-timeout 3600 --max-hold <seconds> -m "<what you are doing and expected duration>" -- bash -lc 'cd path/to/tests && FOO=1 pytest test.py -v 2>&1 | tee run.log'
```

Use manual hold only when you need an interactive lock window:

```bash
moreh-lock hold -m "<why you need the device>"
```

After a locked command exits, verify the lock was released:

```bash
moreh-lock status
```

Expected final output reports the node with no holder:

```text
NODE	<host>
STATE	FREE
USER	-
JOB	-
```

Do not run device commands outside `moreh-lock run` unless a higher-level tool already acquires the lock for you. Do not manually kill another user's lock process.

When queued for `moreh-lock`, do not kill or cancel your own waiter merely because the lock is taking time; the lock is queue-based, and canceling loses your acquisition opportunity. Only cancel a queued waiter if the user explicitly asks, the command is no longer valid, or continuing would be unsafe.

Use `--wait-timeout` for lock acquisition timeout. Use `--max-hold` for command runtime timeout. Always set `--max-hold` to your best estimate of how long you need the device; do not omit it for non-interactive device commands.

If you are debugging or thinking and no command is actively using the device, release the lock immediately so others can use it.

### Docker / container note

Inside Docker, locking only works across processes if the container shares host IPC:

```bash
--ipc=host
```

Also set the real host/user via environment variables or CLI flags when needed:

```bash
export MOREH_LOCK_HOSTNAME=<host>
export MOREH_LOCK_USERNAME=<user>
```

Ignore the message in other people's locks.
