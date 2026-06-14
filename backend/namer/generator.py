"""命名生成器 — 根据识别结果 + 模板生成目标文件名和目录路径

模板变量:
  {title_en}   英文标题
  {title_zh}   中文标题
  {title}      优先使用的标题（根据 style 决定）
  {year}       年份（整数）
  {season}     季数（整数）
  {season:02d} 季数（两位补零）
  {episode}    集数（整数）
  {episode:02d} 集数（两位补零）
  {quality}    画质，如 1080p
  {edition}    版本，如 Director's Cut
  {suffix}     自动构建的后缀，如 " - 1080p"
  {ext}        原始扩展名，如 .mkv
"""

import re
from dataclasses import dataclass
from typing import Optional

from backend.recognizer.recognizer import RecognizedInfo, MediaType


# ─── 默认模板 ────────────────────────────────────────────

TEMPLATES = {
    "movie": {
        "filename": "{title} ({year}){suffix}{ext}",
        "directory": "{title} ({year})",
    },
    "tv": {
        "filename": "{title} S{season:02d}E{episode:02d}{suffix}{ext}",
        "directory": "{title} ({year})",
        "season_dir": "Season {season:02d}",
    },
    "anime": {
        "filename": "{title} S{season:02d}E{episode:02d}{suffix}{ext}",
        "directory": "{title} ({year})",
        "season_dir": "Season {season:02d}",
    },
    "music": {
        "filename": "{title}{suffix}{ext}",
        "directory": "{title}",
    },
    "unknown": {
        "filename": "{title}{ext}",
        "directory": "{title}",
    },
}


@dataclass
class NamingResult:
    """命名生成结果"""
    original_name: str
    directory: str          # 目标目录名（相对于整理根目录）
    season_dir: str         # TV 剧季子目录（如 "Season 01"）
    filename: str           # 目标文件名（含扩展名）
    full_path: str          # 完整相对路径


class NamingGenerator:
    """命名生成器"""

    def __init__(self, style: str = "en"):
        """
        style: "zh" | "en" | "bilingual" | "bilingual_en_first"
        """
        self.style = style

    def generate(self, info: RecognizedInfo, ext: str = ".mkv") -> NamingResult:
        """
        根据识别结果生成目标命名

        Args:
            info: 识别结果
            ext: 文件扩展名（含点号）

        Returns:
            NamingResult 包含目标目录、文件名、完整路径
        """
        media_type = info.media_type.value
        if media_type not in TEMPLATES:
            media_type = "unknown"

        tmpl = TEMPLATES[media_type]
        vars_dict = self._build_vars(info, ext)

        # 渲染各字段
        filename = self._render(tmpl.get("filename", "{title}{ext}"), vars_dict)
        directory = self._render(tmpl.get("directory", "{title}"), vars_dict)
        season_dir = self._render(tmpl.get("season_dir", ""), vars_dict)

        # 构建完整相对路径
        parts = [p for p in [directory, season_dir, filename] if p]
        full_path = "/".join(parts)

        return NamingResult(
            original_name=info.original_name,
            directory=directory,
            season_dir=season_dir,
            filename=filename,
            full_path=full_path,
        )

    def _build_vars(self, info: RecognizedInfo, ext: str) -> dict:
        """构建模板变量字典"""
        # 根据 style 选择标题
        if self.style == "zh":
            title = info.title_zh or info.title_en or info.title
        elif self.style == "en":
            title = info.title_en or info.title
        elif self.style == "bilingual":
            zh = info.title_zh or ""
            en = info.title_en or info.title
            title = f"{zh} {en}".strip()
        elif self.style == "bilingual_en_first":
            zh = info.title_zh or ""
            en = info.title_en or info.title
            title = f"{en} {zh}".strip()
        else:
            title = info.title

        # 构建后缀
        suffix_parts = []
        if info.quality:
            suffix_parts.append(info.quality)
        if info.edition:
            suffix_parts.append(info.edition)
        suffix = f" [{' | '.join(suffix_parts)}]" if suffix_parts else ""

        return {
            "title": title or info.title,
            "title_en": info.title_en or info.title,
            "title_zh": info.title_zh or "",
            "year": info.year or "",
            "season": info.season or 1,
            "episode": info.episode or 1,
            "quality": info.quality or "",
            "edition": info.edition or "",
            "suffix": suffix,
            "ext": ext,
        }

    @staticmethod
    def _render(template: str, vars_dict: dict) -> str:
        """渲染模板字符串，支持 {var:format} 格式说明符"""
        def replacer(m: re.Match) -> str:
            expr = m.group(1)
            if ":" in expr:
                name, fmt = expr.split(":", 1)
                val = vars_dict.get(name, "")
                try:
                    return format(val, fmt)
                except (ValueError, TypeError):
                    return str(val)
            return str(vars_dict.get(expr, ""))

        result = re.sub(r"\{([^}]+)\}", replacer, template)
        # 清理空值残留：移除空的 () 和多余空格
        result = re.sub(r"\(\s*\)", "", result)
        result = re.sub(r"\s{2,}", " ", result)
        return result.strip()


def preview_naming(
    info: RecognizedInfo,
    ext: str = ".mkv",
    style: str = "en",
) -> NamingResult:
    """便捷函数：预览命名结果"""
    gen = NamingGenerator(style=style)
    return gen.generate(info, ext)
