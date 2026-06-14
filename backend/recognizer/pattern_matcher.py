"""正则模式匹配器 — 从文件名中提取元数据"""

import re
from typing import Optional

# RecognizedInfo 用 dict 表示，避免循环导入
# { title, title_zh, title_en, year, season, episode, quality, edition, media_type, confidence, source }

def _none_to_none(s: Optional[str]) -> Optional[str]:
    """空字符串 → None"""
    if s is None or s.strip() == "":
        return None
    return s.strip()


# ─── 内置正则规则 ─────────────────────────────────────────

BUILTIN_PATTERNS = [
    # ── 标准剧集：Show.Name.S01E02.1080p ──
    {
        "name": "standard_tv",
        "pattern": re.compile(
            r"^(.+?)[\.\s_-]+S(\d{2})[\.\s_-]?E(\d{2,3})[\.\s_-]?(\d{3,4}p)?",
            re.IGNORECASE,
        ),
        "media_type": "tv",
        "confidence": 0.90,
        "extract": lambda m: {
            "title": _clean_title(m.group(1)),
            "season": int(m.group(2)),
            "episode": int(m.group(3)),
            "quality": _q(m.group(4)),
        },
    },

    # ── 无季号剧集：Show.Name.E02.1080p ──
    {
        "name": "tv_no_season",
        "pattern": re.compile(
            r"^(.+?)[\.\s_-]+E(\d{2,3})[\.\s_-]?(\d{3,4}p)?",
            re.IGNORECASE,
        ),
        "media_type": "tv",
        "confidence": 0.80,
        "extract": lambda m: {
            "title": _clean_title(m.group(1)),
            "season": 1,
            "episode": int(m.group(2)),
            "quality": _q(m.group(3)),
        },
    },

    # ── 电影含年份：Movie.Name.2023.1080p ──
    {
        "name": "movie_with_year",
        "pattern": re.compile(
            r"^(.+?)[\.\s_-]+(19\d{2}|20\d{2})[\.\s_-]?(\d{3,4}p)?",
            re.IGNORECASE,
        ),
        "media_type": "movie",
        "confidence": 0.85,
        "extract": lambda m: {
            "title": _clean_title(m.group(1)),
            "year": int(m.group(2)),
            "quality": _q(m.group(3)),
        },
    },

    # ── 压制组格式：[Group] Title [1080p] ──
    {
        "name": "fansub_group",
        "pattern": re.compile(
            r"^\[(.+?)\]\s*(.+?)\s*\[(\d{3,4}p?)\]",
            re.IGNORECASE,
        ),
        "media_type": "auto",
        "confidence": 0.75,
        "extract": lambda m: {
            "title": _clean_title(m.group(2)),
            "quality": _q(m.group(3)),
        },
    },

    # ── 中文剧集：片名.第02集.1080p ──
    {
        "name": "chinese_episode",
        "pattern": re.compile(
            r"^(.+?)[\.\s_-]*第\s*(\d{1,3})\s*集[\.\s_-]?(\d{3,4}p)?",
        ),
        "media_type": "tv",
        "confidence": 0.80,
        "extract": lambda m: {
            "title": _clean_title(m.group(1)),
            "season": 1,
            "episode": int(m.group(2)),
            "quality": _q(m.group(3)),
        },
    },

    # ── 纯数字序号：Title.03.mkv ──
    {
        "name": "numeric_sequence",
        "pattern": re.compile(
            r"^(.+?)[\.\s_-]+(\d{1,3})\.(mkv|mp4|avi|mov|ts)$",
            re.IGNORECASE,
        ),
        "media_type": "tv",
        "confidence": 0.70,
        "extract": lambda m: {
            "title": _clean_title(m.group(1)),
            "season": 1,
            "episode": int(m.group(2)),
        },
    },

    # ── 电影格式：Movie.Title (2023) ──
    {
        "name": "movie_paren_year",
        "pattern": re.compile(
            r"^(.+?)\s*\(?(19\d{2}|20\d{2})\)?",
        ),
        "media_type": "movie",
        "confidence": 0.82,
        "extract": lambda m: {
            "title": _clean_title(m.group(1)),
            "year": int(m.group(2)),
        },
    },
]

# ─── 版本关键词 ────────────────────────────────────────────

EDITION_KEYWORDS = {
    "高码": "High Bitrate",
    "导演剪辑": "Director's Cut",
    "加长": "Extended",
    "未分级": "Unrated",
    "收藏版": "Collector's Edition",
    "60fps": "60fps",
    "HDR": "HDR",
    "杜比视界": "Dolby Vision",
    "Dolby Vision": "Dolby Vision",
    "IMAX": "IMAX",
    "修复版": "Remastered",
    "4K": "4K",
    "蓝光": "Blu-ray",
    "Remux": "Remux",
    "Extend": "Extended",
}

# ─── 发布组标识 ────────────────────────────────────────────

RELEASE_GROUP_TAGS = re.compile(
    r"\[.+?\]|【.+?】|\(.+?压制.*?\)|@\S+|By\s+\S+",
    re.IGNORECASE,
)


def _clean_title(raw: str) -> str:
    """清理标题：移除发布组标识、替换分隔符为空格"""
    s = RELEASE_GROUP_TAGS.sub("", raw)
    s = re.sub(r"[\._\-]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _q(val: Optional[str]) -> Optional[str]:
    """标准化画质字符串"""
    if not val:
        return None
    v = val.lower().replace("p", "p").replace(" ", "")
    return v


def extract_edition(filename: str) -> Optional[str]:
    """从文件名中检测版本关键词"""
    for kw, label in EDITION_KEYWORDS.items():
        if kw.lower() in filename.lower():
            return label
    return None


# ─── 广告/垃圾目录模式 ───────────────────────────────────

JUNK_PATTERNS = [
    re.compile(r"【.*?www\.\S+】", re.IGNORECASE),   # 【xxx www.site.com】
    re.compile(r"#recycle", re.IGNORECASE),            # #recycle 回收站
    re.compile(r"@Recycle", re.IGNORECASE),            # Synology @Recycle
    re.compile(r"\.@__thumb", re.IGNORECASE),          # 缩略图缓存
    re.compile(r"^广告|^ad[sv]?$|^推广", re.IGNORECASE),
]


def is_junk_name(name: str) -> bool:
    """判断文件名/目录名是否为广告/垃圾/无用内容"""
    for pat in JUNK_PATTERNS:
        if pat.search(name):
            return True
    return False


def match_filename(filename: str) -> list[dict]:
    """
    对单个文件名执行所有内置规则匹配

    Args:
        filename: 纯文件名（不含路径），如 'Kung.Fu.Hustle.2004.1080p.mkv'

    Returns:
        [ { title, year?, season?, episode?, quality?, media_type, confidence, source }, ... ]
        按置信度降序排列，可能多条
    """
    # 去扩展名
    stem = re.sub(r"\.\w{2,4}$", "", filename.strip())
    edition = extract_edition(filename)

    results = []
    for rule in BUILTIN_PATTERNS:
        m = rule["pattern"].search(stem)
        if not m:
            continue
        info = rule["extract"](m)
        info["media_type"] = rule["media_type"]
        info["confidence"] = rule["confidence"]
        info["source"] = "regex"
        info["edition"] = edition
        results.append(info)

    # 按置信度降序
    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results
