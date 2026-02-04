import fastapi
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
import os
from typing import List

app = fastapi.FastAPI()

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (Frontend)
# We will create a 'tools/static' directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

TELEMETRY_FILE = "simulation_telemetry.jsonl"

@app.get("/")
async def get_index():
    # Serve the main dashboard
    with open(os.path.join(STATIC_DIR, "index.html"), 'r') as f:
        return HTMLResponse(f.read())

@app.get("/events")
async def get_events(start: int = 0):
    """
    Returns a batch of events starting from line 'start'.
    Used for polling/streaming.
    """
    events = []
    if not os.path.exists(TELEMETRY_FILE):
        return {"events": [], "next_start": start}
        
    try:
        with open(TELEMETRY_FILE, 'r') as f:
            # Skip to start line
            for _ in range(start):
                next(f, None)
            
            # Read all new lines
            for line in f:
                if line.strip():
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    except Exception as e:
        print(f"Error reading log: {e}")
        
    return {"events": events, "next_start": start + len(events)}

@app.get("/stats")
async def get_stats():
    """Returns quick aggregate stats if needed."""
    return {"status": "running"}

if __name__ == "__main__":
    print("Starting Web Visualizer on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
