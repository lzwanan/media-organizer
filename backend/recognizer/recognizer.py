"""识别引擎 — 将文件名映射为结构化元数据"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from backend.recognizer.pattern_matcher import match_filename


class MediaType(str, Enum):
    MOVIE = "movie"
    TV = "tv"
    ANIME = "anime"
    MUSIC = "music"
    UNKNOWN = "unknown"


@dataclass
class RecognizedInfo:
    """识别结果"""
    original_name: str
    title: str = ""                    # 清洗后的标题（可能为英文原名）
    title_zh: Optional[str] = None     # 中文标题（暂用正则，未来由 TMDB 填充）
    title_en: Optional[str] = None     # 英文标题
    year: Optional[int] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    quality: Optional[str] = None      # 1080p / 2160p / 4K
    edition: Optional[str] = None      # Director's Cut / Extended
    confidence: float = 0.0
    media_type: MediaType = MediaType.UNKNOWN
    source: str = ""                   # "regex" | "tmdb" | "manual"

    def to_dict(self) -> dict:
        return {
            "title": self.title or None,
            "title_zh": self.title_zh,
            "title_en": self.title_en,
            "year": self.year,
            "season": self.season,
            "episode": self.episode,
            "quality": self.quality,
            "edition": self.edition,
            "confidence": round(self.confidence, 2),
            "media_type": self.media_type.value,
            "source": self.source,
        }


def recognize(filename: str) -> Optional[RecognizedInfo]:
    """
    识别单个文件名

    Pipeline:
      1. 正则规则匹配（pattern_matcher）
      2. 取最高置信度结果
      3. (未来) 查询本地历史缓存
      4. (未来) TMDB API 查证

    Args:
        filename: 文件名（不含路径），如 'Kung.Fu.Hustle.2004.1080p.mkv'

    Returns:
        RecognizedInfo 或 None（完全无法识别）
    """
    matches = match_filename(filename)
    if not matches:
        return None

    # 取最佳匹配
    best = matches[0]

    info = RecognizedInfo(
        original_name=filename,
        title=best.get("title", ""),
        year=best.get("year"),
        season=best.get("season"),
        episode=best.get("episode"),
        quality=best.get("quality"),
        edition=best.get("edition"),
        confidence=best.get("confidence", 0.0),
        media_type=_parse_media_type(best.get("media_type", "unknown")),
        source=best.get("source", "regex"),
    )
    return info


def _parse_media_type(s: str) -> MediaType:
    mapping = {
        "movie": MediaType.MOVIE,
        "tv": MediaType.TV,
        "anime": MediaType.ANIME,
        "music": MediaType.MUSIC,
    }
    return mapping.get(s, MediaType.UNKNOWN)
