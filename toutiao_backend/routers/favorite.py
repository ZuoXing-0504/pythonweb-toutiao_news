from fastapi import status,HTTPException

from fastapi import APIRouter,Depends,Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from models.users import User

from crud import favorite
from utils.auth import get_current_user

from utils.response import success_response
from schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest

router = APIRouter(prefix="/api/favorite",tags=["favorite"])

#检查收藏
@router.get("/check")
async def check_favorite(
        news_id:int = Query(...,alias="newsId"),
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    is_favorite = await favorite.is_news_favorite(db,user.id,news_id)
    return success_response(message="检查收藏状态成功",data=FavoriteCheckResponse(isFavorite=is_favorite))
#添加收藏
@router.post("/add")
async def add_favorite(
        data:FavoriteAddRequest,
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    result = await favorite.add_favorite(db,user.id,data.news_id)
    return success_response(message="添加收藏成功",data=result)

#取消收藏
@router.delete("/remove")
async def remove_favorite(
        news_id:int = Query(...,alias="newsId"),
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    result = await favorite.remove_favorite(db,user.id,news_id)
    if result:
        return success_response(message="取消收藏成功")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="收藏记录不存在")
