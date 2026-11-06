from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from models.users import User
from schemas.ai import AIChatRequest
from services.ai import AIService, get_ai_service
from utils.auth import get_current_user


router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/chat", response_class=StreamingResponse)
async def chat(
    chat_request: AIChatRequest,
    _current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service),
):
    return await ai_service.create_chat_stream(chat_request)
