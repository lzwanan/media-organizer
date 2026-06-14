"""Media Organizer 入口文件"""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.routes import router as api_router
from backend.db.database import init_db

# 确保 backend 包在路径中
sys.path.insert(0, str(Path(__file__).resolve().parent))


def create_app() -> FastAPI:
    app = FastAPI(
        title="Media Organizer",
        description="轻量级媒体文件整理工具",
        version="1.0.0",
    )

    # CORS — 开发时前端 5173，生产时同端口
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000", "http://127.0.0.1:8000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API 路由
    app.include_router(api_router)

    # 初始化数据库
    init_db()

    # 生产模式：挂载前端静态文件
    frontend_dist = Path(__file__).resolve().parent / "frontend" / "dist"
    if frontend_dist.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
