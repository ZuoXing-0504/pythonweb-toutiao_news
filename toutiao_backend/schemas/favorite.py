from pydantic import BaseModel,Field,ConfigDict
from datetime import datetime
from schemas.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(...,alias="isFavorite")
#添加收藏请求
class FavoriteAddRequest(BaseModel):
    news_id: int = Field(...,alias="newsId")
#收藏模型类
class FavoriteNewsItemModel(NewsItemBase):
    favorite_id: int = Field(...,alias="favoriteId")
    favorite_time: datetime = Field(..., alias="favoriteTime")
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
#获取收藏列表响应
class FavoriteListResponse(BaseModel):
    list: list[FavoriteNewsItemModel]
    total: int
    has_more: bool = Field(...,alias="hasMore")
    model_config =ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
