import os
import asyncio
import logging
from contextlib import asynccontextmanager

import py_eureka_client.eureka_client as eureka_client
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent import run_agent

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EUREKA_URL = os.getenv("EUREKA_SERVER_URL", "http://localhost:8761/eureka")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

# Histórico em memória por sessão (substituído pelo memory-service na Entrega 3)
session_store: dict[str, list[dict]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    await eureka_client.init_async(
        eureka_server=EUREKA_URL,
        app_name="agent-service",
        instance_port=APP_PORT,
        instance_host="localhost",
    )
    logger.info("Registrado no Eureka em %s", EUREKA_URL)
    yield
    await eureka_client.stop_async()


app = FastAPI(title="Agent Service", lifespan=lifespan)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.get("/health")
def health():
    return {"status": "up"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    history = session_store.get(req.session_id, [])

    try:
        response_text, updated_history = await run_agent(req.message, history)
    except Exception as e:
        logger.exception("Erro no ciclo agêntico")
        raise HTTPException(status_code=502, detail=f"Erro ao chamar LLM Gateway: {e}")

    session_store[req.session_id] = updated_history
    return ChatResponse(response=response_text, session_id=req.session_id)


@app.delete("/sessions/{session_id}")
def clear_session(session_id: str):
    session_store.pop(session_id, None)
    return {"cleared": session_id}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=APP_PORT, reload=True)
