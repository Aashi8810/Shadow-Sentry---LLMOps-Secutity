from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import ChatRequest, ChatResponseAllowed
from app.db.database import get_db
from app.db.models import AuditLog
from app.llm.client import generate, LLMClientError
from app.config import settings

# --- New Imports for Day 2 ---
from app.detection.regex_filter import scan_prompt_regex
from app.detection.llama_guard import check_prompt_safety

router = APIRouter(prefix="/v1", tags=["chat"])

@router.post("/chat", response_model=ChatResponseAllowed)
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    reasons = []
    risk_score = 0
    
    # --- PRE-FLIGHT CHECKS ---
    
    # 1. Fast Regex Check
    if settings.enable_regex_filter:
        regex_hits = scan_prompt_regex(req.prompt)
        if regex_hits:
            reasons.extend(regex_hits)
            risk_score += settings.weight_regex_match * len(regex_hits)
            
    # 2. Semantic Check via Llama Guard
    if settings.enable_llama_guard:
        is_unsafe, lg_reason = await check_prompt_safety(req.prompt)
        if is_unsafe:
            reasons.append(lg_reason)
            risk_score += settings.weight_llama_guard_unsafe

    # --- RISK SCORING ---
    blocked = risk_score >= settings.block_threshold
    
    if blocked or risk_score > settings.threshold_high_max:
        risk_level = "BLOCKED" if blocked else "HIGH"
    elif risk_score > settings.threshold_medium_max:
        risk_level = "MEDIUM"
    elif risk_score > settings.threshold_low_max:
        risk_level = "LOW"
    else:
        risk_level = "LOW"

    # --- HANDLE BLOCKED REQUESTS ---
    if blocked:
        # Log the blocked attempt
        log_entry = AuditLog(
            user_id=req.user_id,
            endpoint="/v1/chat",
            prompt=req.prompt,
            response="",  # No LLM response generated
            risk_score=risk_score,
            risk_level=risk_level,
            blocked=True,
            detection_reasons=reasons,
        )
        db.add(log_entry)
        db.commit()
        
        # 403 Forbidden is the standard for WAF/Security blocks
        raise HTTPException(
            status_code=403, 
            detail={
                "blocked": True,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "reasons": reasons
            }
        )

    # --- ALLOWED REQUESTS: CALL MAIN LLM ---
    try:
        llm_response = await generate(req.prompt)
    except LLMClientError as e:
        raise HTTPException(status_code=502, detail=f"LLM backend error: {e}")

    # Log the successful transaction
    log_entry = AuditLog(
        user_id=req.user_id,
        endpoint="/v1/chat",
        prompt=req.prompt,
        response=llm_response,
        risk_score=risk_score,
        risk_level=risk_level,
        blocked=False,
        detection_reasons=reasons,
    )
    db.add(log_entry)
    db.commit()

    return ChatResponseAllowed(
        response=llm_response,
        risk_score=risk_score,
        risk_level=risk_level,
        blocked=False,
    )