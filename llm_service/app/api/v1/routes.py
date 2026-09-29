from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies import get_ai_service
from app.services.ai_service import AIService
from app.schemas.ai_schema import AIChatResponse, ChatRequest

router = APIRouter(
    prefix='/ai',
    tags=['ai']
)

@router.post("/embedd", status_code=status.HTTP_200_OK)
def get_embeddings(data: list[str], service: AIService = Depends(get_ai_service)):
    print(data)
    return service.generate_embiddings(data)

@router.post("/chat", response_model=AIChatResponse, status_code=status.HTTP_200_OK)
def get_chat_response(body: ChatRequest, service: AIService = Depends(get_ai_service)):
    print("this is body")
    print(body)
    return service.generate_response(body.context, body.prompt)
