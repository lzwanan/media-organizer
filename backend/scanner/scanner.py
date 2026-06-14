"""目录扫描器 — 异步遍历目录树，识别媒体文件"""

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# 支持的媒体文件扩展名
MEDIA_EXTENSIONS = frozenset({
    ".mkv", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v",
    ".ts", ".m2ts", ".mts", ".vob", ".ogm", ".rmvb",
})

# 默认排除扩展名
EXCLUDE_EXTENSIONS = frozenset({
    ".tmp", ".cache", ".log", ".srt", ".ass", ".ssa",  # 字幕
    ".nfo", ".jpg", ".jpeg", ".png", ".gif", ".bmp",   # 图片
    ".txt", ".md", ".doc", ".pdf",                       # 文档
})


@dataclass
class FileNode:
    """扫描到的文件节点"""
    path: str               # 绝对路径
    name: str               # 文件名（含扩展名）
    type: str               # "file" | "directory"
    size: int               # 文件大小（字节）
    parent: str             # 父目录绝对路径
    depth: int              # 相对根目录的深度
    extension: str          # 扩展名（小写）


@dataclass
class ScanResult:
    """扫描结果"""
    root_path: str
    root_type: Optional[str]  # 根目录推测类型 (movie/tv/anime/music/None)
    items: list[FileNode] = field(default_factory=list)
    total_count: int = 0
    scan_time: str = ""


def guess_root_type(name: str, media_types: dict) -> Optional[str]:
    """根据目录名推测媒体类型"""
    name_lower = name.lower()
    for type_key, keywords in media_types.items():
        for kw in keywords:
            if kw.lower() in name_lower:
                return type_key
    return None


def scan_directory(
    root_path: str,
    *,
    max_depth: int = 5,
    exclude_hidden: bool = True,
    exclude_extensions: frozenset | None = None,
    media_extensions: frozenset | None = None,
    root_type: Optional[str] = None,
) -> ScanResult:
    """
    同步扫描目录（适配 FastAPI 非异步路由，未来可用 run_in_executor）

    Args:
        root_path: 要扫描的根目录绝对路径
        max_depth: 最大扫描深度（相对根目录）
        exclude_hidden: 是否排除隐藏文件/目录
        exclude_extensions: 额外排除的扩展名
        media_extensions: 目标媒体扩展名集合
        root_type: 根目录类型（如果已知）

    Returns:
        ScanResult 包含所有扫描到的文件节点
    """
    start = time.time()
    if exclude_extensions is None:
        exclude_extensions = EXCLUDE_EXTENSIONS
    if media_extensions is None:
        media_extensions = MEDIA_EXTENSIONS

    all_exclude = exclude_extensions
    items: list[FileNode] = []
    root = Path(root_path).resolve()

    if not root.exists():
        raise FileNotFoundError(f"目录不存在: {root_path}")
    if not root.is_dir():
        raise NotADirectoryError(f"路径不是目录: {root_path}")

    # 自动推测根目录类型
    if root_type is None:
        root_type = guess_root_type(root.name, _default_media_types())

    def _walk(current: Path, depth: int, parent_path: str):
        if depth > max_depth:
            return

        try:
            entries = os.scandir(current)
        except PermissionError:
            return
        except OSError:
            return

        for entry in entries:
            name = entry.name

            # 跳过隐藏文件/目录
            if exclude_hidden and name.startswith("."):
                continue

            try:
                entry_path = entry.path
            except OSError:
                continue

            if entry.is_dir(follow_symlinks=False):
                items.append(FileNode(
                    path=entry_path,
                    name=name,
                    type="directory",
                    size=0,
                    parent=parent_path,
                    depth=depth,
                    extension="",
                ))
                _walk(Path(entry_path), depth + 1, entry_path)

            elif entry.is_file(follow_symlinks=False):
                ext = Path(name).suffix.lower()
                if ext in all_exclude:
                    continue
                if ext not in media_extensions:
                    continue

                try:
                    stat = entry.stat(follow_symlinks=False)
                    size = stat.st_size
                except OSError:
                    size = 0

                items.append(FileNode(
                    path=entry_path,
                    name=name,
                    type="file",
                    size=size,
                    parent=parent_path,
                    depth=depth,
                    extension=ext,
                ))

    _walk(root, 0, str(root))

    elapsed = time.time() - start
    return ScanResult(
        root_path=str(root),
        root_type=root_type,
        items=items,
        total_count=sum(1 for i in items if i.type == "file"),
        scan_time=f"{elapsed:.3f}s",
    )


def _default_media_types() -> dict:
    """内置默认媒体类型映射（兜底）"""
    return {
        "movie": ["movie", "movies", "film", "films", "电影"],
        "tv": ["tv", "tvs", "series", "show", "shows", "电视剧"],
        "anime": ["anime", "动漫", "cartoon"],
        "music": ["music", "musics", "音乐"],
    }
