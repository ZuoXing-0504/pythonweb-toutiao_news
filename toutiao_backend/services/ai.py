import logging
import httpx
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse

from schemas.ai import AIChatRequest
from config.settings import get_settings


logger = logging.getLogger(__name__)

class AIService:
    def __init__(
        self,
        api_key: str,
        api_url: str,
        model: str,
        timeout_seconds: float,
    ):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.timeout_seconds = timeout_seconds

    async def create_chat_stream(
        self, chat_request: AIChatRequest
    ) -> StreamingResponse:
        client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout_seconds, connect=10.0)
        )
        request = client.build_request(
            "POST",
            self.api_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
                "X-DashScope-SSE": "enable",
            },
            json={
                "model": self.model,
                "messages": [
                    message.model_dump() for message in chat_request.messages
                ],
                "stream": True,
            },
        )

        try:
            upstream = await client.send(request, stream=True)
        except httpx.RequestError as exc:
            await client.aclose()
            logger.warning("AI upstream request failed: %s", type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI 服务暂时不可用，请稍后重试",
            ) from exc

        if upstream.is_error:
            await upstream.aread()
            upstream_status = upstream.status_code
            await upstream.aclose()
            await client.aclose()
            logger.warning("AI upstream returned HTTP %s", upstream_status)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI 服务暂时不可用，请稍后重试",
            )

        async def stream_response():
            try:
                async for chunk in upstream.aiter_raw():
                    yield chunk
            except httpx.HTTPError as exc:
                logger.warning("AI upstream stream interrupted: %s", type(exc).__name__)
            finally:
                await upstream.aclose()
                await client.aclose()

        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )


def get_ai_service() -> AIService:
    settings = get_settings()
    if not settings.ai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI 服务尚未配置",
        )

    return AIService(
        api_key=settings.ai_api_key,
        api_url=settings.ai_api_base_url,
        model=settings.ai_model,
        timeout_seconds=settings.ai_timeout_seconds,
    )
