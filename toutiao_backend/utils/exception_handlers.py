from fastapi import HTTPException
from utils.exception import http_exception_handler, integrity_error_handler, sqlalchemy_error_handler, \
    general_exception_handler
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
def register_exception_handlers(app):
    """
    注册全局异常处理函数：子类在前，父类在后，具体在前，抽象在后
    """
    app.add_exception_handler(HTTPException, http_exception_handler)#业务层异常处理
    app.add_exception_handler(IntegrityError, integrity_error_handler)#数据库完整性异常处理
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)#SQLAlchemy异常处理
    app.add_exception_handler(Exception, general_exception_handler)#默认异常处理
