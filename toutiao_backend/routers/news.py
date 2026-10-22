from fastapi.exceptions import HTTPException

from fastapi import APIRouter, Depends,Query,Request
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db


from crud import news
router = APIRouter(prefix="/api/news", tags=["news"])
@router.get("/categories")
async def get_categories(skip: int = 0, limit: int = 100,db:AsyncSession = Depends(get_db)):
    categories = await news.get_categories(db,skip,limit)
    return {
        "code": 200,
        "msg": "success",
        "data": categories
    }
# 新闻列表
@router.get("/list")
async def get_news_list(
        category_id: int = Query(...,alias="categoryId"),
        page: int = 1,
        page_size: int = Query(10, alias="pageSize",le=100),
        db:AsyncSession = Depends(get_db)
):
    news_list = await news.get_news_list(db,category_id,(page-1)*page_size,page_size)
    total = await news.get_news_total(db,category_id)
    has_more = (page-1)*page_size + len(news_list) < total
    return {
        "code": 200,
        "msg": "获取新闻列表成功",
        "data": {
            "list": news_list,
            "total": total,
            "hasMore":has_more
        }
    }
#详情
@router.get("/detail")
async def get_news_detail(
        news_id: int = Query(...,alias="id"),
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
    #查询相关新闻
    related_news = await news.get_related_news(db,news_detail.category_id,news_id)

    return {
              "code": 200,
              "message": "success",
              "data": {
                "id": news_detail.id,
                "title": news_detail.title,
                "content": news_detail.content,
                "image": news_detail.image,
                "author": news_detail.author,
                "publishTime": news_detail.publish_time,
                "categoryId": news_detail.category_id,
                "views": news_detail.views,
                "relatedNews": related_news
              }
    }



