from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.generation.rag_service import rag_service

router = APIRouter()

@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    history = []
    if request.history:
        history = [{"role": msg.role, "content": msg.content} for msg in request.history]
        
    return rag_service.answer_query(
        query=request.query,
        history=history,
        document_ids=request.document_ids,
        response_language=request.response_language
    )

@router.post("/stream")
def chat_stream(request: ChatRequest):
    history = []
    if request.history:
        history = [{"role": msg.role, "content": msg.content} for msg in request.history]
        
    return StreamingResponse(
        rag_service.answer_query_stream(
            query=request.query,
            history=history,
            document_ids=request.document_ids,
            response_language=request.response_language
        ),
        media_type="text/event-stream"
    )
