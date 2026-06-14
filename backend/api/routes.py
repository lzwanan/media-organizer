"""API 主路由"""

from fastapi import APIRouter

from backend.config_manager import ConfigManager

router = APIRouter(prefix="/api")


@router.get("/status")
async def status():
    """服务健康状态"""
    config = ConfigManager.instance()
    return {
        "status": "ok",
        "version": config.get("version", "1.0"),
        "config_dir": str(config.config_dir),
    }


@router.get("/config")
async def get_all_config():
    """获取完整配置"""
    return {
        "status": "ok",
        "data": ConfigManager.instance().all,
    }
