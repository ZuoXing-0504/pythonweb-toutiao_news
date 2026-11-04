from typing import Any

from schemas.base import ApiResponse


def success_response(message: str = "success", data: Any = None) -> ApiResponse[Any]:
    return ApiResponse(message=message, data=data)

