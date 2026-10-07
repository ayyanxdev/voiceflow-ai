"""WebSocket endpoint for real-time updates."""

import json
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.logging import log

router = APIRouter(tags=["WebSocket"])

# Active connections
active_connections: Set[WebSocket] = set()


async def broadcast(event: dict):
    """Broadcast an event to all connected WebSocket clients."""
    disconnected = set()
    message = json.dumps(event)
    for ws in list(active_connections):
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.add(ws)
    if disconnected:
        active_connections.difference_update(disconnected)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time dashboard updates."""
    await websocket.accept()
    active_connections.add(websocket)
    log.info("WebSocket client connected. Total: %d", len(active_connections))

    try:
        while True:
            # Keep connection alive, handle client messages
            data = await websocket.receive_text()
            # Client can send ping/pong or commands
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        active_connections.discard(websocket)
        log.info("WebSocket client disconnected. Total: %d", len(active_connections))
    except Exception:
        active_connections.discard(websocket)
