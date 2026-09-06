## Building

Always use `./build_metal.sh -ce` to compile tt-metal. Never use cmake directly, and never use a unity build. After changing tt-metal source code, complete this build before running tests or device workloads; do not rely on judging whether JIT compilation is sufficient.

Separately, activate the active checkout's virtual environment for tt-metal build, test, import, and workload commands, so they resolve dependencies from that checkout rather than another one:

```bash
source "<absolute path to the active tt-metal checkout>/python_env/bin/activate"
```

If that environment does not exist, create it with `./create_venv.sh` first, then activate it. `create_venv.sh` defaults to `./python_env`, but a checkout may use a different directory such as `.venv`; activate the one that checkout actually has. Activating a virtual environment never replaces the system `moreh-lock`.

### Environment variables

Before building, testing, importing, or running tt-metal, set the environment for the exact tt-metal checkout being used. Be especially careful with worktrees: `TT_METAL_HOME` must point to the active tt-metal worktree, not another checkout. Set all of the following:

```bash
export TT_METAL_HOME="<absolute path to the tt-metal checkout or worktree in use>"
export TT_METAL_RUNTIME_ROOT="${TT_METAL_HOME}"
export PYTHONPATH="${TT_METAL_HOME}:${TT_METAL_HOME}/ttnn:${TT_METAL_HOME}/tools"
```
