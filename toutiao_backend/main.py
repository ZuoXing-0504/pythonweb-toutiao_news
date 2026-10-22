from fastapi import FastAPI
from routers import news,users,favorite
from fastapi.middleware.cors import CORSMiddleware


from utils.exception_handlers import register_exception_handlers

app = FastAPI()
#注册异常处理器
register_exception_handlers(app)

origins = ["http://localhost:5173","http://127.0.0.1:5173"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,#允许的来源
    allow_credentials=True,#cookie是否允许跨域
    allow_methods=["*"],
    allow_headers=["*"],
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
