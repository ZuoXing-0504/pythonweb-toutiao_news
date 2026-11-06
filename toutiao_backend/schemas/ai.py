from typing import Literal

from pydantic import Field, field_validator, model_validator

from schemas.base import CamelModel


class AIMessage(CamelModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=8000)

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("消息内容不能为空")
        return value


class AIChatRequest(CamelModel):
    messages: list[AIMessage] = Field(min_length=1, max_length=30)

    @model_validator(mode="after")
    def limit_total_content(self):
        if sum(len(message.content) for message in self.messages) > 40000:
            raise ValueError("消息总长度不能超过 40000 个字符")
        return self
