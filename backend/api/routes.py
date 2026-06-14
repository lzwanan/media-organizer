"""API 主路由"""

import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.config_manager import ConfigManager
from backend.scanner.scanner import FileNode, ScanResult, scan_directory
from backend.recognizer.recognizer import recognize, RecognizedInfo, MediaType
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


class RenamePreviewRequest(BaseModel):
    items: list[dict]   # [{original_name, title, year, media_type, ...}]
    style: str = "en"


class RenamePreviewItem(BaseModel):
    path: str
    target_name: str
    target_dir: str
    target_path: str


@router.post("/rename-preview")
async def rename_preview(req: RenamePreviewRequest):
    """根据命名风格重新生成目标名称（不重新扫描）"""
    naming_style = req.style
    if naming_style == "en_first":
        naming_style = "bilingual_en_first"

    namer = NamingGenerator(style=naming_style)
    results: list[dict] = []

    for item in req.items:
        title = item.get("title", "")
        year = item.get("year")
        season = item.get("season")
        episode = item.get("episode")
        quality = item.get("quality")
        edition = item.get("edition")
        media_type = item.get("media_type", "unknown")
        ext = item.get("extension", ".mkv")

        # 构建 RecognizedInfo
        info = RecognizedInfo(
            original_name=item.get("original_name", title),
            title=title,
            year=year,
            season=season,
            episode=episode,
            quality=quality,
            edition=edition,
        )
        try:
            info.media_type = MediaType(media_type)
        except ValueError:
            info.media_type = MediaType.UNKNOWN

        naming = namer.generate(info, ext=ext)
        results.append({
            "path": item.get("path", ""),
            "target_name": naming.filename,
            "target_dir": naming.directory,
            "target_path": naming.full_path,
        })

    return {"status": "ok", "style": req.style, "items": results}


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

    # 对每个节点运行识别 + 命名预览
    items: list[FileNodeResponse] = []
    for node in result.items:
        rec = None

        if node.type == "file":
            info = recognize(node.name)
            if info:
                rec = info.to_dict()
                naming = namer.generate(info, ext=node.extension if node.extension else ".mkv")
                rec["target_name"] = naming.filename
                rec["target_dir"] = naming.directory
                rec["target_path"] = naming.full_path

        elif node.type == "directory":
            info = recognize(node.name)
            if info:
                rec = info.to_dict()
                directory_tmpl = "{title} ({year})" if info.year else "{title}"
                rec["target_name"] = NamingGenerator._render(directory_tmpl, namer._build_vars(info, ""))
                rec["target_dir"] = rec["target_name"]
                rec["target_path"] = rec["target_name"]

        items.append(FileNodeResponse.from_node(node, recognized=rec))

    return ScanResponse(
        task_id=task_id,
        root_path=result.root_path,
        root_type=result.root_type,
        total_count=result.total_count,
        items=items,
    )
