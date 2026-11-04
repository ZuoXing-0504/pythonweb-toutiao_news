from fastapi import APIRouter, Depends,HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User
from utils.auth import get_current_user


from schemas.base import ApiResponse
from schemas.users import UserRequest, UserInfoResponse, UserAuthResponse, UserUpdateRequest, UserChangePasswordRequest
from crud import users
from config.db_conf import get_db
from utils.response import success_response
router = APIRouter(prefix="/api/user", tags=["users"])

@router.post("/register", response_model=ApiResponse[UserAuthResponse])
async def register( user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    existing_user = await users.get_user_by_username( user_data.username,db)
    if existing_user:
        raise HTTPException(status_code=400,detail="用户名已存在")
    user = await users.create_user(db, user_data)
    #生成token
    token = await users.create_token(db,user.id)
    response_data =UserAuthResponse(token = token,user_info = UserInfoResponse.model_validate(user))
    return success_response(message="注册成功",data=response_data)

#登录
@router.post("/login", response_model=ApiResponse[UserAuthResponse])
async def login( user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    user = await users.authenticate_user(db,user_data.username,user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="用户名或密码错误")
    #生成token
    token = await users.create_token(db,user.id)
    response_data =UserAuthResponse(token = token,user_info = UserInfoResponse.model_validate(user))
    return success_response(message="登录成功",data=response_data)

#获取用户信息
@router.get("/info", response_model=ApiResponse[UserInfoResponse])
async def get_user_info(current_user: User = Depends(get_current_user)):
    return success_response(message="获取用户信息成功",data=UserInfoResponse.model_validate(current_user))

#修改用户信息
@router.put("/update", response_model=ApiResponse[UserInfoResponse])
async def update_user_info(
        user_data: UserUpdateRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    user = await users.update_user(db,user.username,user_data)
    return success_response(message="更新用户信息成功",data=UserInfoResponse.model_validate(user))

#修改密码
@router.put("/password", response_model=ApiResponse[None])
async def update_password(
        password_data: UserChangePasswordRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    success = await users.change_password(db,user,password_data.new_password,password_data.old_password)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="旧密码错误")
    return success_response(message="修改密码成功")
