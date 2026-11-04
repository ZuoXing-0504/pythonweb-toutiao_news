from fastapi import APIRouter,Depends,Query,HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.base import ApiResponse
from schemas.history import HistoryListResponse, HistoryRecordResponse

from config.db_conf import get_db
from crud import history
from models.users import User
from schemas.history import HistoryAddRequest
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history",tags=["history"])
#添加历史记录
@router.post("/add", response_model=ApiResponse[HistoryRecordResponse])
async def add_history(
        data:HistoryAddRequest,
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    result = await history.add_history(db,user.id,data.news_id)
    return success_response(message="添加历史记录成功",data=result)

#获取浏览历史列表
@router.get("/list", response_model=ApiResponse[HistoryListResponse])
async def list_history(
        page:int = Query(1,ge =1),
        page_size:int = Query(10,ge =1,le = 100,alias = "pageSize"),
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    history_list,total,has_more = await history.list_history(db,user.id,page,page_size)
    hi_list =[{
        **history.__dict__,
        "history_id":history_id,
        "view_time":view_time,
    } for history,history_id,view_time in history_list]
    return success_response(message="获取浏览历史列表成功",data=HistoryListResponse(list=hi_list,total=total,has_more=has_more))

#删除单条历史记录
@router.delete("/delete/{news_id}", response_model=ApiResponse[None])
async def delete_history(
        news_id:int,
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    result = await history.delete_history(db,user.id,news_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="历史记录不存在",
        )

    return success_response(message="删除历史记录成功")
#清空浏览历史列表
@router.delete("/clear", response_model=ApiResponse[None])
async def clear_history(
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    result = await history.clear_history(db,user.id)
    if result == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="历史记录不存在",
        )
    return success_response(message="清空浏览历史列表成功")
