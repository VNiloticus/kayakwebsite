from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict

app = FastAPI()

# Mount static folder for frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Kayak data model
class KayakSession(BaseModel):
    user: str
    start_time: datetime
    end_time: Optional[datetime] = None
    active: bool = True

# Simple in-memory storage (no database needed yet)
kayaks: Dict[int, Optional[KayakSession]] = {i: None for i in range(1, 11)}  # 5 kayaks

@app.get("/", response_class=HTMLResponse)
def serve_index():
    return FileResponse("static/index.html")

@app.get("/kayaks")
def get_kayaks():
    """Return current kayak states."""
    return {
        kayak_id: (session.model_dump() if session else None)
        for kayak_id, session in kayaks.items()
    }

@app.post("/start")
def start_kayak(kayak_id: int, user: str):
    """Start a kayak session."""
    if kayak_id not in kayaks:
        return {"error": "Invalid kayak ID"}
    kayaks[kayak_id] = KayakSession(user=user, start_time=datetime.now())
    return {"status": "started", "kayak": kayak_id, "user": user, "start_time": kayaks[kayak_id].start_time}

@app.post("/stop")
def stop_kayak(kayak_id: int):
    """Stop a kayak session."""
    session = kayaks.get(kayak_id)
    if not session or not session.active:
        return {"error": "No active session"}
    session.end_time = datetime.now()
    session.active = False
    kayaks[kayak_id] = session
    return {"status": "stopped", "kayak": kayak_id, "duration": str(session.end_time - session.start_time)}
