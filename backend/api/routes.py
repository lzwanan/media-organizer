"""API 主路由"""

import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.config_manager import ConfigManager
from backend.scanner.scanner import FileNode, ScanResult, scan_directory
from backend.recognizer.recognizer import recognize, RecognizedInfo
from backend.recognizer.pattern_matcher import is_junk_name
from backend.namer.generator import NamingGenerator
from backend.clients.translator import translate, get_api_key


router = APIRouter(prefix="/api")


# ─── Request/Response models ────────────────────────────

class ScanRequest(BaseModel):
    root_path: str
    strategy: Optional[str] = "smart"
    style: Optional[str] = "en"  # zh / en / bilingual / en_first


class FileNodeResponse(BaseModel):
    path: str
    name: str
    type: str
    size: int
    parent: str
    depth: int
    extension: str
    recognized: Optional[dict] = None
    junk: bool = False
    empty: bool = False

    @classmethod
    def from_node(cls, node: FileNode, recognized: Optional[dict] = None, junk: bool = False, empty: bool = False) -> "FileNodeResponse":
        return cls(
            path=node.path,
            name=node.name,
            type=node.type,
            size=node.size,
            parent=node.parent,
            depth=node.depth,
            extension=node.extension,
            recognized=recognized,
            junk=junk,
            empty=empty,
        )


class ScanResponse(BaseModel):
    task_id: str
    root_path: str
    root_type: Optional[str]
    total_count: int
    items: list[FileNodeResponse]


# ─── Routes ─────────────────────────────────────────────

class TranslateRequest(BaseModel):
    text: str
    target_lang: str = "zh-CN"
    source_lang: str = "auto"


@router.post("/translate")
async def translate_text(req: TranslateRequest):
    """手动翻译文本（需配置 API Key）"""
    key = get_api_key("google")
    if not key:
        raise HTTPException(
            status_code=400,
            detail="Translation API key not configured. Set GOOGLE_TRANSLATE_API_KEY env var or translators.google.api_key in config.",
        )
    result = await translate(req.text, req.target_lang, req.source_lang)
    if result is None:
        raise HTTPException(status_code=500, detail="Translation failed")
    return {"status": "ok", "translated": result}


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

    # 命名风格取自配置
    naming_style = req.style or config.get("naming.style.movie", "en")
    # en_first 是 bilingual 反向
    if naming_style == "en_first":
        naming_style = "bilingual_en_first"
    namer = NamingGenerator(style=naming_style)

    # 构建 parent→children 映射用于空目录检测
    parent_map: dict[str, list[FileNode]] = {}
    for node in result.items:
        parent_map.setdefault(node.parent, []).append(node)

    # 收集所有包含媒体文件的目录
    dirs_with_media: set[str] = set()
    for node in result.items:
        if node.type == "file":
            # 标记该文件的所有祖先目录为「含媒体」
            p = node.parent
            while p and p.startswith(result.root_path):
                dirs_with_media.add(p)
                # 上级目录
                parent_candidate = str(Path(p).parent)
                if parent_candidate == p or not parent_candidate.startswith(result.root_path):
                    break
                p = parent_candidate

    # 对每个节点运行识别 + 命名预览 + 标签
    items: list[FileNodeResponse] = []
    for node in result.items:
        rec = None
        is_junk = False
        is_empty = False

        if node.type == "file":
            info = recognize(node.name)
            if info:
                rec = info.to_dict()
                naming = namer.generate(info, ext=node.extension if node.extension else ".mkv")
                rec["target_name"] = naming.filename
                rec["target_dir"] = naming.directory
                rec["target_path"] = naming.full_path
            else:
                # 无法识别的文件 → 标记为 junk
                is_junk = True

        elif node.type == "directory":
            # 目录识别
            info = recognize(node.name)
            if info:
                rec = info.to_dict()
                # 目录只生成 target_dir（不生成 filename）
                directory_tmpl = "{title} ({year})" if info.year else "{title}"
                rec["target_name"] = NamingGenerator._render(directory_tmpl, namer._build_vars(info, ""))
                rec["target_dir"] = rec["target_name"]
                rec["target_path"] = rec["target_name"]

            # 垃圾目录检测
            if is_junk_name(node.name):
                is_junk = True

            # 空目录检测（目录本身没有媒体文件后代）
            if node.path not in dirs_with_media:
                is_empty = True

        items.append(FileNodeResponse.from_node(node, recognized=rec, junk=is_junk, empty=is_empty))

    return ScanResponse(
        task_id=task_id,
        root_path=result.root_path,
        root_type=result.root_type,
        total_count=result.total_count,
        items=items,
    )
