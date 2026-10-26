from pydantic import BaseModel,Field,ConfigDict
from schemas.base import NewsItemBase
from datetime import datetime

class HistoryAddRequest(BaseModel):
    news_id: int = Field(...,alias="newsId")

#历史模型类
class HistoryNewsItemModel(NewsItemBase):
    history_id: int = Field(...,alias="historyId")
    view_time: datetime = Field(..., alias="viewTime")
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
#获取浏览历史列表响应
class HistoryListResponse(BaseModel):
    list: list[HistoryNewsItemModel]
    total: int
    has_more: bool = Field(...,alias="hasMore")
    model_config =ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
