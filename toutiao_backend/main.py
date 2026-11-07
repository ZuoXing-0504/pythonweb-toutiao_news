from fastapi import FastAPI
from routers import news,users,favorite,history
from fastapi.middleware.cors import CORSMiddleware


from utils.exception_handlers import register_exception_handlers
from config.settings import get_settings
from utils.logging import RequestLoggingMiddleware, configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI()
#注册异常处理器
register_exception_handlers(app)

app.add_middleware(RequestLoggingMiddleware)


app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),#允许的来源
    allow_credentials=True,#cookie是否允许跨域
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)
