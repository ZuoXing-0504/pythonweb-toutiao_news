from datetime import datetime, timedelta

from sqlalchemy import func, select
from main import app
from models.favorite import Favorite
from models.history import History
from models.news import Category, News
from models.users import User


async def register(client, username: str = "student_01") -> str:
    response = await client.post(
        "/api/user/register",
        json={"username": username, "password": "password123"},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]["token"]


async def seed_news(session_factory, count: int = 3) -> list[int]:
    async with session_factory() as session:
        category = Category(name="科技", sort_order=1)
        session.add(category)
        await session.flush()
        now = datetime(2026, 11, 4, 12, 0, 0)
        items = [
            News(
                title=f"新闻{i}",
                description=f"简介{i}",
                content=f"内容{i}",
                author="测试作者",
                category_id=category.id,
                views=i,
                publish_time=now - timedelta(hours=i),
            )
            for i in range(count)
        ]
        session.add_all(items)
        await session.commit()
        return [item.id for item in items]


async def test_register_login_and_protected_info(client):
    token = await register(client)

    info = await client.get(
        "/api/user/info",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert info.status_code == 200
    assert info.json()["data"]["username"] == "student_01"

    login = await client.post(
        "/api/user/login",
        json={"username": "student_01", "password": "password123"},
    )
    assert login.status_code == 200
    login_token = login.json()["data"]["token"]
    assert login_token

    wrong_password = await client.put(
        "/api/user/password",
        headers={"Authorization": f"Bearer {login_token}"},
        json={"oldPassword": "wrong123", "newPassword": "newpass123"},
    )
    assert wrong_password.status_code == 400
    assert wrong_password.json()["message"] == "旧密码错误"


async def test_validation_response_does_not_echo_password(client):
    response = await client.post(
        "/api/user/register",
        json={"username": "x", "password": "secret"},
    )

    assert response.status_code == 422
    assert response.json()["message"] == "请求参数校验失败"
    assert "secret" not in response.text


async def test_registration_rolls_back_if_token_creation_fails(
    client, session_factory, monkeypatch
):
    async def fail_to_create_token(*args, **kwargs):
        raise RuntimeError("token service failed")

    monkeypatch.setattr("routers.users.users.create_token", fail_to_create_token)
    response = await client.post(
        "/api/user/register",
        json={"username": "rollback_user", "password": "password123"},
    )
    assert response.status_code == 500

    async with session_factory() as session:
        result = await session.execute(
            select(User).where(User.username == "rollback_user")
        )
        assert result.scalar_one_or_none() is None


async def test_news_list_is_ordered_and_uses_camel_case(client, session_factory):
    await seed_news(session_factory)

    response = await client.get(
        "/api/news/list",
        params={"categoryId": 1, "page": 1, "pageSize": 2},
    )
    body = response.json()

    assert response.status_code == 200
    assert [item["title"] for item in body["data"]["list"]] == ["新闻0", "新闻1"]
    assert body["data"]["hasMore"] is True
    assert "publishTime" in body["data"]["list"][0]
    assert "publish_time" not in body["data"]["list"][0]


async def test_favorite_lifecycle_is_idempotent(client, session_factory):
    news_id = (await seed_news(session_factory, count=1))[0]
    token = await register(client)
    headers = {"Authorization": f"Bearer {token}"}

    first = await client.post(
        "/api/favorite/add", headers=headers, json={"newsId": news_id}
    )
    second = await client.post(
        "/api/favorite/add", headers=headers, json={"newsId": news_id}
    )
    assert first.status_code == second.status_code == 200
    assert first.json()["data"]["id"] == second.json()["data"]["id"]

    async with session_factory() as session:
        count = await session.scalar(select(func.count(Favorite.id)))
        assert count == 1

    removed = await client.delete(
        "/api/favorite/remove", headers=headers, params={"newsId": news_id}
    )
    removed_again = await client.delete(
        "/api/favorite/remove", headers=headers, params={"newsId": news_id}
    )
    assert removed.status_code == removed_again.status_code == 200


async def test_history_upsert_and_delete_are_idempotent(client, session_factory):
    news_id = (await seed_news(session_factory, count=1))[0]
    token = await register(client)
    headers = {"Authorization": f"Bearer {token}"}

    first = await client.post(
        "/api/history/add", headers=headers, json={"newsId": news_id}
    )
    second = await client.post(
        "/api/history/add", headers=headers, json={"newsId": news_id}
    )
    assert first.status_code == second.status_code == 200
    assert first.json()["data"]["id"] == second.json()["data"]["id"]

    async with session_factory() as session:
        count = await session.scalar(select(func.count(History.id)))
        assert count == 1

    deleted = await client.delete(f"/api/history/delete/{news_id}", headers=headers)
    deleted_again = await client.delete(
        f"/api/history/delete/{news_id}", headers=headers
    )
    assert deleted.status_code == deleted_again.status_code == 200


async def test_request_id_is_returned_and_can_be_correlated(client):
    response = await client.get(
        "/",
        headers={"X-Request-ID": "test-request-123"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-123"


async def test_invalid_request_id_is_replaced(client):
    response = await client.get(
        "/",
        headers={"X-Request-ID": "invalid request id"},
    )

    generated_id = response.headers["X-Request-ID"]
    assert generated_id != "invalid request id"
    assert len(generated_id) == 32
