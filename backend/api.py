from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agent import BusinessIntelligenceAgent


app = FastAPI(
    title="Skylark Monday BI Agent"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://skylark-monday-bi-agent-dusky.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


agent = BusinessIntelligenceAgent()


class QuestionRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Skylark Monday BI Agent"
    }


@app.post("/ask")
def ask(request: QuestionRequest):

    result = agent.answer(
        request.question
    )

    return result