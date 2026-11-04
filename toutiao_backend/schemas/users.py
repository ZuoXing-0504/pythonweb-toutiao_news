from typing import Literal, Optional

from pydantic import Field, field_validator

from schemas.base import CamelModel


class UserRequest(CamelModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_]+$")
    password: str = Field(min_length=6, max_length=72)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.strip()
#基础类
class UserInfoBase(CamelModel):
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[Literal["male", "female", "unknown"]] = Field(None, description="性别")
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
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$")

#修改密码时的模型类
class UserChangePasswordRequest(CamelModel):
    old_password: str = Field(..., min_length=6, max_length=72, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=20,description="新密码")
