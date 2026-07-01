"""
/v1/chat endpoint.

Day 1 scope: pure passthrough. No detection logic yet — that arrives Day 2+.
We DO already log every transaction to the audit table so the schema/pipeline
is proven out from the start.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import ChatRequest, ChatResponseAllowed
from app.db.database import get_db
from app.db.models import AuditLog
from app.llm.client import generate, LLMClientError

router = APIRouter(prefix="/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponseAllowed)
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    try:
        llm_response = await generate(req.prompt)
    except LLMClientError as e:
        raise HTTPException(status_code=502, detail=f"LLM backend error: {e}")

    # Day 1: no real detection yet, so everything is LOW / not blocked.
    risk_score = 0
    risk_level = "LOW"
    blocked = False

    log_entry = AuditLog(
        user_id=req.user_id,
        endpoint="/v1/chat",
        prompt=req.prompt,
        response=llm_response,
        risk_score=risk_score,
        risk_level=risk_level,
        blocked=blocked,
        detection_reasons=[],
    )
    db.add(log_entry)
    db.commit()

    return ChatResponseAllowed(
        response=llm_response,
        risk_score=risk_score,
        risk_level=risk_level,
        blocked=blocked,
    )
