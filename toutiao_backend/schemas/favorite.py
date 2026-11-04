from datetime import datetime
from schemas.base import CamelModel, NewsItemBase


class FavoriteCheckResponse(CamelModel):
    is_favorite: bool
#添加收藏请求
class FavoriteAddRequest(CamelModel):
    news_id: int


class FavoriteRecordResponse(CamelModel):
    id: int
    news_id: int
    created_at: datetime


#收藏模型类
class FavoriteNewsItemModel(NewsItemBase):
    favorite_id: int
    favorite_time: datetime
#获取收藏列表响应
class FavoriteListResponse(CamelModel):
    list: list[FavoriteNewsItemModel]
    total: int
    has_more: bool
