#!/usr/bin/env python
import os
import asyncio
import json
import uuid
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Import arena components
from arena.orchestrator import run as orchestrator_run
from arena.agents.memory import memory
from arena.utils.events import EventEmitter
import db

# Settings file path
SETTINGS_PATH = ".arena_settings.json"

# Event queues registry
event_queues = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure DB is initialized
    print("ARENA starting up...")
    db.init_db()
    yield
    # Shutdown: Cleanup
    print("ARENA shutting down...")

app = FastAPI(title="ARENA API", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/run")
async def start_run(request: Request):
    """Start a new autonomous run."""
    data = await request.json()
    goal = data.get("goal")
    settings = data.get("settings", {})
    
    if not goal:
        raise HTTPException(status_code=400, detail="Goal is required")
        
    run_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    # Store run in database
    db.save_run(run_id, goal, "running", created_at)
    
    # Create event queue for this run
    event_queues[run_id] = asyncio.Queue()
    
    # Run orchestrator in background
    asyncio.create_task(background_orchestrator(run_id, goal, settings))
    
    return {"run_id": run_id}


async def background_orchestrator(run_id: str, goal: str, settings: Dict):
    """Run the orchestrator in the background and emit events."""
    queue = event_queues.get(run_id)
    if not queue:
        return
        
    emitter = EventEmitter(queue)
    
    try:
        report = await orchestrator_run(goal, run_id, emit=emitter, settings=settings, verbose=True)
        # Update database with final report
        db.update_run_status(run_id, "complete", report)
    except Exception as e:
        print(f"Error in background run {run_id}: {e}")
        await emitter.error(str(e))
        db.update_run_status(run_id, "failed")
    finally:
        # Signal end of stream
        await queue.put(None)


@app.get("/api/events/{run_id}")
async def get_events(run_id: str):
    """Stream events for a specific run via SSE."""
    if run_id not in event_queues and not db.get_run(run_id):
        raise HTTPException(status_code=404, detail="Run not found")
        
    async def event_generator():
        queue = event_queues.get(run_id)
        if not queue:
            # If run is already finished, emit completion event immediately
            run_data = db.get_run(run_id)
            if run_data:
                yield f"data: {json.dumps({'type': 'run_complete', 'report': run_data['report']})}\n\n"
            return

        while True:
            event = await queue.get()
            if event is None: # End signal
                break
            yield f"data: {json.dumps(event)}\n\n"
        
        # Cleanup queue after stream ends
        if run_id in event_queues:
            del event_queues[run_id]

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/runs")
async def list_runs(limit: int = 10):
    """List recent runs."""
    return db.list_runs(limit)


@app.get("/api/run/{run_id}")
async def get_run(run_id: str):
    """Get details of a specific run."""
    run_data = db.get_run(run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail="Run not found")
    return run_data


@app.delete("/api/run/{run_id}")
async def delete_run(run_id: str):
    """Delete a run."""
    db.delete_run(run_id)
    return {"status": "success"}


@app.get("/api/memory")
async def list_memory(limit: int = 50):
    """Browse stored memories."""
    return await memory.list_all(limit)


@app.post("/api/memory/clear")
async def clear_memory():
    """Clear all memories."""
    await memory.clear()
    return {"status": "success"}


@app.get("/api/settings")
async def get_settings():
    """Get global settings."""
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)
    return {
        "provider": "gemini" if os.getenv("GOOGLE_API_KEY") else "nvidia",
        "max_tasks": 5,
        "max_retries": 1,
        "critic_threshold": 7
    }


@app.post("/api/settings")
async def save_settings(request: Request):
    """Save global settings."""
    settings = await request.json()
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f)
    return {"status": "success"}


@app.get("/health")
async def health_check():
    """Health check."""
    return {
        "status": "healthy",
        "api_key_set": bool(os.getenv("NVIDIA_API_KEY")),
        "db_path": os.getenv("ARENA_DB_PATH", "arena.db")
    }


# Mount static files if exists
if os.path.exists("static"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("ARENA_HOST", "0.0.0.0")
    port = int(os.getenv("ARENA_PORT", "8000"))
    
    print(f"Starting ARENA server on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
