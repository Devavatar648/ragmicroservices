from fastapi import APIRouter, Depends, UploadFile, File
from app.api.v1.dependencies import get_current_user, get_document_service, get_rag_service, User
from app.services.rag_services import DocumentService, RAGService
from pydantic import BaseModel


# 1. Define a request model
class AskRequest(BaseModel):
    query: str



router = APIRouter(prefix="/api/v1")

@router.post("/upload")
def upload_doc(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    doc_service: DocumentService = Depends(get_document_service)
):
    return doc_service.process_and_store_document(file=file, user_id=current_user.id)

@router.post("/ask")
def ask_question(
    # query: str , it will search for query in the parameters
    payload: AskRequest,
    current_user: User = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service)
):
    return rag_service.answer_query(user_id=current_user.id, query=payload.query)