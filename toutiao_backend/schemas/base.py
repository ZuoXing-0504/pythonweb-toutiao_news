from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


T = TypeVar("T")


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
    )


class ApiResponse(CamelModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class CategoryResponse(CamelModel):
    id: int
    name: str
    sort_order: int


class NewsItemBase(CamelModel):
    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: int
    views: int
    publish_time: Optional[datetime] = None


class NewsListResponse(CamelModel):
    list: list[NewsItemBase]
    total: int
    has_more: bool


class NewsDetailResponse(NewsItemBase):
    content: str
    related_news: list[NewsItemBase]
