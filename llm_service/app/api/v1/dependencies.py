from app.services.ai_service import AIService
from app.config import settings

def get_ai_service()->AIService:
    return AIService(settings.GOOGLE_API_KEY)