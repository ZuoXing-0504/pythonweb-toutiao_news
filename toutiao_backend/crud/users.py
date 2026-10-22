#根据用户名查询数据库
import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy import select,update
from sqlalchemy.ext.asyncio import AsyncSession
from utils import security
from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest, UserChangePasswordRequest


async def get_user_by_username( username: str,db: AsyncSession):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()
#创建用户
async def create_user( db: AsyncSession, user_data: UserRequest):
    #密码加密
    hashed_password = security.get_hash_password(user_data.password)
    user = User(username=user_data.username,password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)#读回最新的用户信息
    return user
#生成token
async def create_token(db: AsyncSession,user_id: int):
     token = str(uuid.uuid4())
     expires_at = datetime.now() + timedelta(days=7)
     query = select(UserToken).where(UserToken.user_id == user_id)
     result = await db.execute(query)
     user_token = result.scalar_one_or_none()
     if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
     else:
        user_token = UserToken(user_id=user_id,token=token,expires_at=expires_at)
     db.add(user_token)
     await db.commit()
     return token
#认证密码
async def authenticate_user( db: AsyncSession,username: str,password: str):
    user = await get_user_by_username(username,db)
    if not user:
        return None
    if not security.verify_password(password,user.password):
        return None
    return user
#查token，查用户->封装utils
async def get_user_by_token(db: AsyncSession,token: str):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()
    if not db_token or db_token.expires_at < datetime.now():
        return None
    query = select(User).where(User.id == db_token.user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    return user

#更新用户信息
async def update_user(db: AsyncSession,username: str,user_data: UserUpdateRequest):
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    ))
    result = await db.execute(query)
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404,detail="用户不存在")
    user = await get_user_by_username(username,db)
    return user

#修改密码
async def change_password(db: AsyncSession,user: User,new_password: str,old_password: str):
    if not security.verify_password(old_password,user.password):
        return False
    user.password = security.get_hash_password(new_password)
    db.add(user)#添加到会话中,由SqlAlchemy真正接管user对象,规避session过期或关闭导致的数据库操作失败
    await db.commit()
    await db.refresh(user)
    return True





