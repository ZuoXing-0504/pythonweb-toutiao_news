from datetime import datetime

from schemas.base import CamelModel, NewsItemBase


class HistoryAddRequest(CamelModel):
    news_id: int


class HistoryRecordResponse(CamelModel):
    id: int
    news_id: int
    view_time: datetime

#历史模型类
class HistoryNewsItemModel(NewsItemBase):
    history_id: int
    view_time: datetime
#获取浏览历史列表响应
class HistoryListResponse(CamelModel):
    list: list[HistoryNewsItemModel]
    total: int
    has_more: bool
