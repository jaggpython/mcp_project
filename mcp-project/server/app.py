from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.agent import run_agent


app = FastAPI(
    title="MCP AI Application",
    description="FastAPI + MCP + Ollama",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
async def root():

    return {
        "message": "MCP AI Application"
    }


@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }


@app.post("/chat")
async def chat(request: ChatRequest):

    result = await run_agent(
        request.message
    )

    return {
        "message": request.message,
        "answer": result["answer"],
        "tool": result.get("tool"),
        "arguments": result.get("arguments", {}),
        "tool_result": result.get("tool_result"),
        "steps": result.get("steps", []),
    }