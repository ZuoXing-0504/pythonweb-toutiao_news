from fastapi import Header, Depends,HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud import users


async def get_current_user(
        authorization: str | None = Header(None, alias="Authorization"),
        db: AsyncSession = Depends(get_db)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少身份凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await users.get_user_by_token(db,token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
