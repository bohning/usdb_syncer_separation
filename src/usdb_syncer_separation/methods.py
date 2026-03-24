"""JSON-RPC methods registration and implementation."""

import asyncio
from typing import Any

from .demucs_runner import separate_audio
from .server import INVALID_PARAMS, JsonRpcError, Server

rpc_server = Server()


MODELS = ["htdemucs", "htdemucs_ft"]


@rpc_server.register("get_spec_version")
async def get_spec_version(_params: Any) -> str:
    return "1"


@rpc_server.register("exit")
async def exit_(_params: Any) -> None:
    raise SystemExit(0)


@rpc_server.register("get_name")
async def get_name(_params: Any) -> str:
    return "usdb-syncer-separation"


@rpc_server.register("get_version")
async def get_version(_params: Any) -> str:
    return "0.1.0"


@rpc_server.register("is_gpu_accelerated")
async def is_gpu_accelerated(_params: Any) -> bool:
    def check_gpu():
        try:
            import torch

            return torch.cuda.is_available() or torch.backends.mps.is_available()
        except ImportError:
            return False

    return await asyncio.to_thread(check_gpu)


@rpc_server.register("get_available_models")
async def get_available_models(_params: Any) -> list[str]:
    return MODELS


@rpc_server.register("split")
async def split(params: Any) -> dict[str, str]:
    if not isinstance(params, dict):
        raise JsonRpcError(
            INVALID_PARAMS, "Params must be an object with input_file and output_dir"
        )

    input_file = params.get("input_file")
    output_dir = params.get("output_dir")
    model = params.get("model", "htdemucs")

    if not input_file or not output_dir:
        raise JsonRpcError(INVALID_PARAMS, "Missing input_file or output_dir")

    if model not in MODELS:
        raise JsonRpcError(
            INVALID_PARAMS, f"Invalid model. Supported models are: {', '.join(MODELS)}"
        )

    loop = asyncio.get_running_loop()
    try:
        vocals, instrumental = await loop.run_in_executor(
            None, separate_audio, input_file, output_dir, model
        )
    except Exception as e:
        raise JsonRpcError(-32603, f"Demucs separation failed: {e!s}") from e
    else:
        return {"output_vocals": vocals, "output_instrumental": instrumental}
