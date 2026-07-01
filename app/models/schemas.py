from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user")
    prompt: str = Field(..., description="The prompt to send to the LLM")

class ChatResponseAllowed(BaseModel):
    response: str
    risk_score: int
    risk_level: str
    blocked: bool