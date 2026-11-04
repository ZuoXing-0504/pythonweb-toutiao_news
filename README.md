# 头条新闻项目

一个基于网课项目继续独立开发的新闻资讯应用。目前后端仍在开发中，仓库用于记录学习过程和功能迭代。

## 技术栈

- 后端：FastAPI、SQLAlchemy Async、Pydantic、MySQL、aiomysql
- 前端：Vue 3、Vite、Pinia、Vant

## 后端已实现

- 用户注册与登录
- Token 身份认证
- 获取和修改用户资料
- 修改密码
- 新闻分类、分页列表和详情
- 新闻浏览量及相关新闻
- 检查新闻收藏状态
- 统一异常响应

## 开发计划

- [x] 完成收藏的新增、删除、列表和清空接口
- [x] 完成浏览历史接口
- [x] 统一 ORM Base 和响应结构
- [x] 添加 Alembic 数据库迁移
- [x] 添加自动化接口测试
- [ ] 将 AI 请求迁移到后端代理

## 本地启动

1. 进入后端目录并创建虚拟环境。
2. 安装依赖：pip install -r requirements.txt
3. 复制 toutiao_backend/.env.example 为 toutiao_backend/.env，填写本地数据库连接。
4. 在 toutiao_backend 目录运行：uvicorn main:app --reload
5. FastAPI 文档地址：http://127.0.0.1:8000/docs。

## 数据库迁移

- 新数据库：在 `toutiao_backend` 目录运行 `alembic upgrade head`。
- 已有且结构与初始迁移一致的数据库：先运行 `alembic stamp head`，之后再使用正常迁移命令。
- 创建新迁移：`alembic revision --autogenerate -m "变更说明"`。

## 自动化测试

测试使用内存 SQLite，不会修改本地 MySQL 或 Redis 数据。

```bash
pip install -r requirements-dev.txt
pytest
```

> 注意：项目仍在开发中，部分前端功能对应的后端接口尚未完成。

