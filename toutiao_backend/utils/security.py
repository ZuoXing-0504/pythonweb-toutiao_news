from passlib.context import CryptContext
#创建密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#密码加密
def get_hash_password(password: str):
    return pwd_context.hash(password)
#验证密码
def verify_password(password: str,hashed_password: str):
    return pwd_context.verify(password,hashed_password)
