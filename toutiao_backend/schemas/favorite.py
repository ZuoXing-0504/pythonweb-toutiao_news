from pydantic import BaseModel,Field

class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(...,alias="isFavorite")
#添加收藏请求
class FavoriteAddRequest(BaseModel):
    news_id: int = Field(...,alias="newsId")
