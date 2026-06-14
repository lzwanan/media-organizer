"""API 主路由"""

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.config_manager import ConfigManager
from backend.scanner.scanner import FileNode, ScanResult, scan_directory
from backend.recognizer.recognizer import recognize


router = APIRouter(prefix="/api")


# ─── Request/Response models ────────────────────────────

class ScanRequest(BaseModel):
    root_path: str
    strategy: Optional[str] = "smart"


class FileNodeResponse(BaseModel):
    path: str
    name: str
    type: str
    size: int
    parent: str
    depth: int
    extension: str
    recognized: Optional[dict] = None

    @classmethod
    def from_node(cls, node: FileNode, recognized: Optional[dict] = None) -> "FileNodeResponse":
        return cls(
            path=node.path,
            name=node.name,
            type=node.type,
            size=node.size,
            parent=node.parent,
            depth=node.depth,
            extension=node.extension,
            recognized=recognized,
        )


class ScanResponse(BaseModel):
    task_id: str
    root_path: str
    root_type: Optional[str]
    total_count: int
    items: list[FileNodeResponse]


# ─── Routes ─────────────────────────────────────────────

@router.get("/status")
async def status():
    config = ConfigManager.instance()
    return {
        "status": "ok",
        "version": config.get("version", "1.0"),
        "config_dir": str(config.config_dir),
    }


@router.get("/config")
async def get_all_config():
    return {
        "status": "ok",
        "data": ConfigManager.instance().all,
    }


@router.post("/scan", response_model=ScanResponse)
async def scan(req: ScanRequest):
    """扫描指定目录"""
    config = ConfigManager.instance()

    try:
        result = scan_directory(
            root_path=req.root_path,
            max_depth=config.get("scan.max_depth", 5),
            exclude_hidden=config.get("scan.exclude_hidden", True),
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))

    task_id = f"scan_{uuid.uuid4().hex[:12]}"

    # 对每个文件运行识别
    items: list[FileNodeResponse] = []
    for node in result.items:
        rec = None
        if node.type == "file":
            info = recognize(node.name)
            if info:
                rec = info.to_dict()
        items.append(FileNodeResponse.from_node(node, recognized=rec))

    return ScanResponse(
        task_id=task_id,
        root_path=result.root_path,
        root_type=result.root_type,
        total_count=result.total_count,
        items=items,
    )
