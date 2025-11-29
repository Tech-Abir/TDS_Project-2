from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agent import run_agent
from dotenv import load_dotenv
import uvicorn
import os
from shared_store import url_time, BASE64_STORE
import time
from pydantic import BaseModel

load_dotenv()

EMAIL = os.getenv("EMAIL") 
SECRET = os.getenv("SECRET")


class SolveRequest(BaseModel):
    url: str
    secret: str

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
START_TIME = time.time()
@app.get("/healthz")
def healthz():
    """Simple liveness check."""
    return {
        "status": "ok",
        "uptime_seconds": int(time.time() - START_TIME)
    }

@app.post("/solve")
async def solve(request: SolveRequest, background_tasks: BackgroundTasks):
    if request.secret != SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    url = request.url
    if not url:
        raise HTTPException(status_code=400, detail="Missing URL")

    # --- CLEAR STATE ---
    url_time.clear()
    BASE64_STORE.clear()

    # --- SET ENV VARS FOR AGENT ---
    os.environ["url"] = url
    os.environ["offset"] = "0"
    url_time[url] = time.time()

    # --- START AGENT ASYNC ---
    background_tasks.add_task(run_agent, url)

    return {"status": "ok", "message": f"Agent started for URL: {url}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
