"""
CONSUL-AI — FastAPI + LangGraph バックエンド
HuggingFace Spaces (Docker SDK) での動作を想定
"""
import json
import asyncio
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from graph.state import ConsultingState
from graph.workflow import build_graph


app = FastAPI(
    title="CONSUL-AI",
    description="Multi-Agent Consulting Orchestration API (LangGraph + FastAPI)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    client_input: str
    api_key: str


NODE_LABELS = {
    "issue_analysis":  {"icon": "🔍", "name": "課題分析 Agent"},
    "roi_estimation":  {"icon": "📊", "name": "ROI試算 Agent"},
    "roadmap":         {"icon": "🗺️",  "name": "ロードマップ Agent"},
    "final_proposal":  {"icon": "📝", "name": "提案書サマリー Agent"},
}

RESULT_KEYS = {
    "issue_analysis": "issue_analysis_result",
    "roi_estimation": "roi_estimation_result",
    "roadmap":        "roadmap_result",
    "final_proposal": "final_proposal_result",
}


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def run_graph_stream(client_input: str, api_key: str) -> AsyncGenerator[str, None]:
    graph = build_graph()

    initial_state: ConsultingState = {
        "client_input": client_input,
        "_api_key": api_key,
        "issue_analysis_result": "",
        "roi_estimation_result": "",
        "roadmap_result": "",
        "final_proposal_result": "",
        "current_agent": "issue_analysis",
        "error": "",
    }

    yield sse("start", {"message": "オーケストレーション開始"})

    try:
        # stream_mode="updates" はdict形式で返る: {node_name: state_update}
        async for chunk in graph.astream(initial_state, stream_mode="updates"):
            for node_name, state_update in chunk.items():
                if node_name == "__end__":
                    continue

                label = NODE_LABELS.get(node_name, {"icon": "🤖", "name": node_name})
                result_key = RESULT_KEYS.get(node_name)
                result_text = state_update.get(result_key, "") if result_key else ""

                yield sse("node_complete", {
                    "node": node_name,
                    "icon": label["icon"],
                    "name": label["name"],
                    "result": result_text,
                })

                await asyncio.sleep(0.1)

        yield sse("done", {"message": "全エージェント完了"})

    except Exception as e:
        yield sse("error", {"message": str(e)})


@app.post("/api/run")
async def run_consulting(req: RunRequest):
    if not req.client_input.strip():
        raise HTTPException(status_code=400, detail="client_input is required")
    if not req.api_key.strip():
        raise HTTPException(status_code=400, detail="api_key is required")

    return StreamingResponse(
        run_graph_stream(req.client_input, req.api_key),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "CONSUL-AI"}


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
