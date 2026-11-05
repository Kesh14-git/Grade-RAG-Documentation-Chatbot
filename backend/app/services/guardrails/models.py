from pydantic import BaseModel
from typing import Optional, List

class GroundingResult(BaseModel):
    grounded: bool
    score: float
    reason: str

class CitationValidationResult(BaseModel):
    valid: bool
    reason: Optional[str] = None
