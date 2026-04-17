from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for batch progress broadcasting."""

    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, batch_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.setdefault(batch_id, []).append(ws)

    def disconnect(self, batch_id: str, ws: WebSocket) -> None:
        conns = self._connections.get(batch_id, [])
        if ws in conns:
            conns.remove(ws)

    async def broadcast(self, batch_id: str, data: dict[str, Any]) -> None:
        conns = self._connections.get(batch_id, [])
        dead: list[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                dead.append(ws)
        for ws in dead:
            conns.remove(ws)


manager = ConnectionManager()


@router.websocket("/ws/batches/{batch_id}")
async def batch_websocket(websocket: WebSocket, batch_id: str) -> None:
    await manager.connect(batch_id, websocket)
    try:
        while True:
            # Keep connection alive; we push from server side
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(batch_id, websocket)
