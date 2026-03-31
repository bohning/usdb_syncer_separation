# Demucs separation provider for USDB Syncer

see the main project: https://github.com/bohning/usdb_syncer

This repository is a separation provider. It allows performing stem separation on audio (with optional CUDA acceleration).

## Build

1. [`uv`](https://docs.astral.sh/uv/) is required

2. With CUDA:
`uv run --extra cuda121 pyinstaller -n usdb_syncer_separation_cuda --collect-data demucs run.py`

3. CPU-only:
`uv run --extra cpu pyinstaller -n usdb_syncer_separation_cpu --collect-data demucs run.py`

4. The resulting binary will be in `dist/usdb_syncer_separation_cuda` or `dist/usdb_syncer_separation_cpu`, respectively. You can copy it to a location of your choice (make sure to copy the _internal folder as well) and point the Syncer to it.
