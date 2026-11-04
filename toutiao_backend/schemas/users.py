from typing import Optional

from pydantic import Field

from schemas.base import CamelModel


class UserRequest(CamelModel):
    username: str
    password: str
#基础类
class UserInfoBase(CamelModel):
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个⼈简介")

#user_info 对应的类·
class UserInfoResponse(UserInfoBase):
    id : int
    username : str

#data 数据类型
class UserAuthResponse(CamelModel):
    token: str
    user_info: UserInfoResponse
#更新用户信息的模型类
class UserUpdateRequest(UserInfoBase):
    phone: Optional[str] = None

#修改密码时的模型类
class UserChangePasswordRequest(CamelModel):
    old_password: str = Field(...,description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=20,description="新密码")
