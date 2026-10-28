
from config.cache_conf import get_json_cache, set_cache
from typing import Dict, Any, List, Optional
#新闻分类的读取与写入，缓存方法
CATEGORIES_KEY = "news:categories"
#获取新闻分类缓存
async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY)
#写入新闻分类缓存
async def set_cached_categories(data: List[Dict[str, Any]], expire: int = 7200):
    return await set_cache(CATEGORIES_KEY, data, expire)

#新闻列表的读取与写入，缓存方法
NEWS_LIST_KEY = "news_list"
#获取新闻列表缓存
async def get_cached_news_list(category_id:Optional[int],page:int,size:int):
    category_part = category_id if category_id else "all"
    key = f"{NEWS_LIST_KEY}:{category_part}:{page}:{size}"
    return await get_json_cache(key)
#写入新闻列表缓存
async def set_cached_news_list(category_id:Optional[int],page:int,size:int,data:List[Dict[str, Any]], expire: int = 1800):
    category_part = category_id if category_id else "all"
    key = f"{NEWS_LIST_KEY}:{category_part}:{page}:{size}"
    return await set_cache(key, data, expire)
