from fastapi.exceptions import HTTPException

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud import news_cache

from crud import news
from schemas.base import ApiResponse, CategoryResponse, NewsDetailResponse, NewsListResponse
from utils.response import success_response

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/categories", response_model=ApiResponse[list[CategoryResponse]])
async def get_categories(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: AsyncSession = Depends(get_db),
):
    categories = await news_cache.get_categories(db,skip,limit)
    return success_response(message="获取新闻分类成功", data=categories)
# 新闻列表
@router.get("/list", response_model=ApiResponse[NewsListResponse])
async def get_news_list(
        category_id: int = Query(..., alias="categoryId", ge=1),
        page: int = Query(1, ge=1),
        page_size: int = Query(10, alias="pageSize", ge=1, le=100),
        db:AsyncSession = Depends(get_db)
):
    news_list = await news_cache.get_news_list(db,category_id,(page-1)*page_size,page_size)
    total = await news.get_news_total(db,category_id)
    has_more = (page-1)*page_size + len(news_list) < total
    data = NewsListResponse(list=news_list, total=total, has_more=has_more)
    return success_response(message="获取新闻列表成功", data=data)
#详情
@router.get("/detail", response_model=ApiResponse[NewsDetailResponse])
async def get_news_detail(
        news_id: int = Query(..., alias="id", ge=1),
        db:AsyncSession = Depends(get_db)
):
    #查询新闻详情+增加浏览量+相关新闻
    news_detail = await news.get_news_detail(db,news_id)
    if not news_detail:
        raise HTTPException(status_code=404,detail="新闻不存在")
    #增加浏览量
    views_res = await news.increase_news_views(db,news_id)
    if not views_res:
        raise HTTPException(status_code=500,detail="增加浏览量失败")
    await db.refresh(news_detail, attribute_names=["views"])
    #查询相关新闻
    related_news = await news.get_related_news(db,news_detail.category_id,news_id)

    data = NewsDetailResponse.model_validate({
        **news_detail.__dict__,
        "related_news": related_news,
    })
    return success_response(message="获取新闻详情成功", data=data)



