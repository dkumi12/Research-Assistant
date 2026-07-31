import os
import traceback
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .graph import research_graph
from .schemas import ResearchRequest, ResearchResponse

load_dotenv()

app = FastAPI(title="AI Research Assistant", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/api/research", response_model=ResearchResponse)
async def run_research(request: ResearchRequest):
    try:
        # Run the synchronous graph in a separate thread so Ctrl+C still works!
        result = await asyncio.to_thread(
            research_graph.invoke,
            {
                "question": request.question,
                "depth": request.depth,
                "max_search_rounds": int(os.getenv("MAX_SEARCH_ROUNDS", "2")),
            }
        )
        return result
    except Exception as e:
        print(f"🚨 CRITICAL ERROR DURING RESEARCH 🚨\n{e}")
        raise HTTPException(status_code=500, detail=str(e))