from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.agent import BusinessIntelligenceAgent


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Skylark Monday BI Agent",
    description="Business Intelligence API powered by Monday.com data",
    version="1.0.0"
)


# =========================================================
# AGENT
# =========================================================

agent = BusinessIntelligenceAgent()


# =========================================================
# REQUEST MODEL
# =========================================================

class QuestionRequest(BaseModel):
    question: str


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "status": "running",
        "message": "Skylark Monday BI Agent API is running"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Skylark Monday BI Agent"
    }


# =========================================================
# ASK QUESTION
# =========================================================

@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:
        result = agent.answer(question)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )