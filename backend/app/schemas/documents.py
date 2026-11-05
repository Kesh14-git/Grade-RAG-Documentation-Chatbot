from pydantic import BaseModel
from typing import List

class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    
class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
