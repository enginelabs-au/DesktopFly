"""Loopback WebSocket bridge.

Binds only to 127.0.0.1. Auth token is never logged. Neural frames do not
authorize connectors.
"""

from __future__ import annotations

import asyncio
import json
import secrets
from dataclasses import dataclass, field
from typing import Any

ALLOWED_CLIENT_TYPES = frozenset(
    {"host_lease", "stop", "pause", "resume", "sensory", "health_subscribe"}
)


@dataclass(frozen=True)
class BridgeConfig:
    bind_host: str = "127.0.0.1"
    max_message_bytes: int = 65536
    token: str = ""

    def __post_init__(self) -> None:
        if self.bind_host != "127.0.0.1":
            raise ValueError("bridge must bind to 127.0.0.1 only")
        if self.max_message_bytes < 256:
            raise ValueError("max_message_bytes too small")


def new_launch_token() -> str:
    return secrets.token_urlsafe(32)


def validate_client_message(
    raw: bytes | str,
    *,
    token: str,
    max_bytes: int = 65536,
) -> dict[str, Any]:
    if isinstance(raw, str):
        raw_bytes = raw.encode("utf-8")
    else:
        raw_bytes = raw
    if len(raw_bytes) > max_bytes:
        raise ValueError("message exceeds max_ws_message_bytes")
    try:
        payload = json.loads(raw_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("malformed JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("message must be an object")
    if payload.get("token") != token:
        raise ValueError("invalid token")
    msg_type = payload.get("type")
    if msg_type not in ALLOWED_CLIENT_TYPES:
        raise ValueError("unsupported message type")
    return payload


@dataclass
class Bridge:
    config: BridgeConfig
    stop_requested: bool = False
    _server: Any = field(default=None, repr=False)

    @classmethod
    def create(cls, policy: dict[str, Any]) -> Bridge:
        bind = policy.get("network_bind", "127.0.0.1")
        if bind != "127.0.0.1":
            raise ValueError("network_bind must be 127.0.0.1")
        cfg = BridgeConfig(
            bind_host=bind,
            max_message_bytes=int(policy.get("max_ws_message_bytes", 65536)),
            token=new_launch_token(),
        )
        return cls(config=cfg)

    def handle(self, raw: bytes | str, supervisor: Any) -> dict[str, Any]:
        msg = validate_client_message(
            raw,
            token=self.config.token,
            max_bytes=self.config.max_message_bytes,
        )
        kind = msg["type"]
        if kind == "stop":
            self.stop_requested = True
            supervisor.request_stop("bridge_stop")
            return {"ok": True, "lifecycle": supervisor.lifecycle.value}
        if kind == "pause":
            supervisor.user_pause()
            return {"ok": True, "lifecycle": supervisor.lifecycle.value}
        if kind == "host_lease":
            supervisor.set_host_lease(bool(msg.get("fresh", False)))
            return {"ok": True, "host_lease_fresh": supervisor.host_lease_fresh}
        if kind == "health_subscribe":
            return {"ok": True, "health": supervisor.health_view().as_dict()}
        if kind == "resume":
            if supervisor.stop_latched:
                return {"ok": False, "reason": "stop_latched"}
            return {"ok": False, "reason": "resume_requires_supervisor_path"}
        if kind == "sensory":
            return {"ok": True, "accepted": True, "connector_authority": False}
        raise ValueError("unhandled message type")

    async def serve(self, supervisor: Any, *, host: str = "127.0.0.1", port: int = 0) -> Any:
        """Start an asyncio websockets server on loopback. Returns the server."""
        if host != "127.0.0.1":
            raise ValueError("bridge must bind to 127.0.0.1 only")
        try:
            from websockets.asyncio.server import serve
        except ImportError:  # pragma: no cover
            from websockets.server import serve  # type: ignore

        async def handler(websocket: Any) -> None:
            async for message in websocket:
                if isinstance(message, bytes) and len(message) > self.config.max_message_bytes:
                    await websocket.close(code=1009, reason="too large")
                    return
                try:
                    result = self.handle(message, supervisor)
                except ValueError as exc:
                    await websocket.send(json.dumps({"ok": False, "error": str(exc)}))
                    continue
                await websocket.send(json.dumps(result))
                if self.stop_requested:
                    await websocket.close()
                    return

        self._server = await serve(handler, host, port)
        return self._server

    async def stop_server(self) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
