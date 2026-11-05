import os
import uuid
import tempfile
import logging
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from typing import List
from app.schemas.documents import DocumentResponse, DocumentListResponse
from app.services.document_service import document_service
from app.services.ingestion.pdf_processor import pdf_processor
from app.services.chunking.semantic_chunker import chunker
from app.services.retrieval.vector_store import vector_store
from app.services.retrieval.bm25_store import bm25_store
from app.services.llm.factory import llm_factory

router = APIRouter()
logger = logging.getLogger(__name__)

def process_document_task(file_path: str, doc_id: str, filename: str):
    try:
        # 1. Extract
        blocks = pdf_processor.extract_text_and_metadata(file_path, doc_id, filename)
        
        # 2. Chunk
        chunks = chunker.chunk_documents(blocks)
        
        # 3. Embed (Default)
        embedding_provider = llm_factory.get_embedding_provider()
        texts = [chunk["content"] for chunk in chunks]
        
        # Batch embedding (handle limits if necessary, for hackathon we assume it fits)
        embeddings = embedding_provider.get_embeddings(texts)
        
        # 4. Index (Default)
        vector_store.add_documents(chunks, embeddings)
        bm25_store.add_documents(chunks)

        # 4b. Multilingual Embed & Index
        try:
            from app.services.embeddings.multilingual_model import multilingual_model
            from app.services.retrieval.multilingual_vector_store import multilingual_vector_store
            logger.info(f"Generating multilingual embeddings for {filename}")
            multi_embeddings = multilingual_model.encode(texts)
            multilingual_vector_store.add_documents(chunks, multi_embeddings)
        except Exception as e:
            logger.error(f"Failed to index multilingual embeddings for {filename}: {e}")
        
        # 5. Update Status
        document_service.update_status(doc_id, "completed")
        logger.info(f"Successfully processed document: {filename}")
        
    except Exception as e:
        logger.error(f"Error processing document {filename}: {e}")
        document_service.update_status(doc_id, "error")
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    doc_id = str(uuid.uuid4())
    
    # Save temp file
    temp_fd, temp_path = tempfile.mkstemp(suffix=".pdf")
    os.close(temp_fd)
    
    with open(temp_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    document_service.add_document(doc_id, file.filename)
    
    background_tasks.add_task(process_document_task, temp_path, doc_id, file.filename)
    
    return DocumentResponse(id=doc_id, filename=file.filename, status="processing")

@router.get("", response_model=DocumentListResponse)
def list_documents():
    return DocumentListResponse(documents=document_service.get_documents())

@router.delete("/{doc_id}")
def delete_document(doc_id: str):
    # Remove from stores
    vector_store.delete_document(doc_id)
    bm25_store.delete_document(doc_id)
    
    try:
        from app.services.retrieval.multilingual_vector_store import multilingual_vector_store
        multilingual_vector_store.delete_document(doc_id)
    except Exception:
        pass
        
    document_service.delete_document(doc_id)
    return {"status": "success"}
