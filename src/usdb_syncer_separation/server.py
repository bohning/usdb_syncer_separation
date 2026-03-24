"""JSON-RPC server implementation over stdin/stdout."""

import asyncio
import json
import logging
import sys
from collections.abc import Awaitable, Callable
from typing import Any, TypeAlias

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

RpcParams = dict[str, Any] | list | None
RpcResponse = dict[str, Any]
HandlerFunc: TypeAlias = Callable[[RpcParams], Awaitable[Any]]  # noqa: UP040


class JsonRpcError(Exception):
    """Exception raised for JSON-RPC errors."""

    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        result = {"code": self.code, "message": self.message}
        if self.data is not None:
            result["data"] = self.data
        return result


# Standard Error Codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


class Server:
    """JSON-RPC 2.0 Server handling requests over stdin and stdout."""

    def __init__(self):
        self.methods: dict[str, HandlerFunc] = {}

    def register(self, name: str):
        """Register a method with the server."""

        def decorator(func: HandlerFunc):
            self.methods[name] = func
            return func

        return decorator

    async def _handle_request(self, request: Any) -> RpcResponse | None:
        if not isinstance(request, dict):
            return self._build_error_response(None, INVALID_REQUEST, "Invalid Request")

        req_id = request.get("id")
        if request.get("jsonrpc") != "2.0":
            return self._build_error_response(
                req_id,
                INVALID_REQUEST,
                "Invalid Request: missing or invalid jsonrpc version",
            )

        method = request.get("method")
        if not isinstance(method, str):
            return self._build_error_response(
                req_id, INVALID_REQUEST, "Invalid Request: missing or invalid method"
            )

        params = request.get("params")

        if method not in self.methods:
            return self._build_error_response(
                req_id, METHOD_NOT_FOUND, "Method not found"
            )

        try:
            handler = self.methods[method]
            result = await handler(params)
        except JsonRpcError as e:
            return self._build_error_response(req_id, e.code, e.message, e.data)
        except Exception:
            logger.exception(f"Internal error processing method {method}")
            return self._build_error_response(req_id, INTERNAL_ERROR, "Internal error")
        else:
            if req_id is not None:
                return {"jsonrpc": "2.0", "result": result, "id": req_id}
            return None  # Notification (no id)

    def _build_error_response(
        self, req_id: Any, code: int, message: str, data: Any = None
    ) -> RpcResponse | None:
        if req_id is None and code != PARSE_ERROR and code != INVALID_REQUEST:
            # Notifications do not have an ID and do not return errors unless it's a parse/invalid request error
            return None

        error_obj = {"code": code, "message": message}
        if data is not None:
            error_obj["data"] = data

        return {"jsonrpc": "2.0", "error": error_obj, "id": req_id}

    async def serve(self):  # noqa: C901
        logger.info("JSON-RPC Server started listening on stdin.")

        try:
            while True:
                line = await asyncio.to_thread(sys.stdin.readline)
                if not line:
                    break  # EOF

                line_str = line.strip()
                if not line_str:
                    continue

                try:
                    request = json.loads(line_str)
                except json.JSONDecodeError:
                    response = self._build_error_response(
                        None, PARSE_ERROR, "Parse error"
                    )
                    if response:
                        self._write_response(response)
                    continue

                if isinstance(request, list):
                    if not request:
                        response = self._build_error_response(
                            None, INVALID_REQUEST, "Invalid Request"
                        )
                        if response:
                            self._write_response(response)
                        continue

                    responses = []
                    for req in request:
                        res = await self._handle_request(req)
                        if res is not None:
                            responses.append(res)
                    if responses:
                        self._write_response(responses)
                else:
                    response = await self._handle_request(request)
                    if response is not None:
                        self._write_response(response)

        except Exception:
            logger.exception("Fatal error in server loop")
        finally:
            logger.info("JSON-RPC Server exiting.")

    def _write_response(self, response: Any):
        try:
            output = json.dumps(response) + "\n"
            sys.stdout.write(output)
            sys.stdout.flush()
        except Exception:
            logger.exception("Failed to write response")
