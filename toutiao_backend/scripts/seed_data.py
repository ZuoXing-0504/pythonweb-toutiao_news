import asyncio
from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy import select

from config.cache_conf import redis_client
from config.db_conf import AsyncSessionLocal, async_engine
from models.base import utc_now
from models.news import Category, News


@dataclass(frozen=True)
class DemoNews:
    category: str
    title: str
    description: str
    content: str
    author: str = "演示编辑部"


CATEGORIES = [
    "头条",
    "社会",
    "国内",
    "国际",
    "娱乐",
    "体育",
    "科技",
    "财经",
]

DEMO_NEWS = [
    DemoNews("头条", "演示：城市公共服务数字化升级", "多项便民服务实现线上办理。", "城市公共服务平台完成新一轮升级，为居民提供更加便捷的线上办事体验。"),
    DemoNews("社会", "演示：社区开展周末志愿服务", "志愿者为居民提供多项便民服务。", "社区组织志愿者开展周末服务活动，覆盖环境维护、便民咨询和公益宣传。"),
    DemoNews("国内", "演示：多地推进绿色交通建设", "公共交通网络进一步完善。", "多地持续完善公共交通网络，推广绿色出行方式，提升居民通勤体验。"),
    DemoNews("国际", "演示：国际青年创新交流活动举行", "青年代表分享创新项目。", "来自多个国家和地区的青年代表围绕科技创新与可持续发展展开交流。"),
    DemoNews("娱乐", "演示：青年影像展集中展映", "多部青年作品与观众见面。", "青年影像展集中展示多部原创作品，并举办主创交流活动。"),
    DemoNews("体育", "演示：高校校园联赛开幕", "多支高校队伍参加本届赛事。", "高校校园联赛正式开幕，赛事设置多个项目，鼓励学生积极参加体育锻炼。"),
    DemoNews("科技", "演示：人工智能辅助科研取得进展", "新工具帮助研究人员提高数据处理效率。", "研究团队将人工智能工具应用于数据分析，在保证可验证性的前提下提升科研效率。"),
    DemoNews("财经", "演示：小微企业服务平台上线", "平台提供政策查询与融资咨询。", "面向小微企业的综合服务平台上线，提供政策查询、经营咨询和融资对接等服务。"),
]


async def seed_demo_data() -> tuple[int, int]:
    categories_created = 0
    news_created = 0

    async with AsyncSessionLocal() as session:
        existing_categories = {
            item.name: item
            for item in (await session.scalars(select(Category))).all()
        }
        for sort_order, name in enumerate(CATEGORIES, start=1):
            if name not in existing_categories:
                category = Category(name=name, sort_order=sort_order)
                session.add(category)
                existing_categories[name] = category
                categories_created += 1

        await session.flush()
        demo_titles = [item.title for item in DEMO_NEWS]
        existing_titles = set(
            await session.scalars(select(News.title).where(News.title.in_(demo_titles)))
        )
        published_at = utc_now()
        for offset, item in enumerate(DEMO_NEWS):
            if item.title in existing_titles:
                continue
            session.add(
                News(
                    title=item.title,
                    description=item.description,
                    content=item.content,
                    author=item.author,
                    category_id=existing_categories[item.category].id,
                    publish_time=published_at - timedelta(minutes=offset),
                )
            )
            news_created += 1

        await session.commit()

    try:
        await redis_client.delete("news:v1:categories:0:100")
        async for key in redis_client.scan_iter(match="news:v1:list:*"):
            await redis_client.delete(key)
    except Exception:
        # Seeding must still work when Redis is unavailable.
        pass

    return categories_created, news_created


async def main() -> None:
    try:
        categories_created, news_created = await seed_demo_data()
        print(
            "Demo data ready: "
            f"categories_created={categories_created}, news_created={news_created}"
        )
    finally:
        await redis_client.aclose()
        await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
