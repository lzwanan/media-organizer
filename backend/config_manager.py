"""
配置管理器 - JSON 配置文件的读写与管理
存储位置：~/.media-organizer/config.json
"""

import json
import shutil
from pathlib import Path
from typing import Any


def _config_dir() -> Path:
    """返回配置目录，Windows / macOS / Linux 自适应"""
    return Path.home() / ".media-organizer"


def _config_path() -> Path:
    return _config_dir() / "config.json"


def _default_config_path() -> Path:
    """打包后的默认配置模板路径"""
    return Path(__file__).resolve().parent.parent / "config" / "default_config.json"


class ConfigManager:
    """配置管理器：加载、读取、写入、重置配置"""

    _instance: "ConfigManager | None" = None

    def __init__(self):
        self._data: dict[str, Any] = {}
        self._load()

    @classmethod
    def instance(cls) -> "ConfigManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load(self):
        config_path = _config_path()
        config_dir = _config_dir()

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            # 首次启动：复制默认配置到用户目录
            config_dir.mkdir(parents=True, exist_ok=True)
            default = _default_config_path()
            if default.exists():
                shutil.copy(default, config_path)
                with open(config_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            else:
                # 兜底：用内置最小配置
                self._data = self._minimal_config()
                config_dir.mkdir(parents=True, exist_ok=True)
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(self._data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _minimal_config() -> dict:
        return {
            "version": "1.0",
            "scan": {"max_depth": 5, "exclude_hidden": True, "exclude_extensions": [".tmp", ".cache", ".log", ".srt"], "max_file_size_mb": 10240},
            "recognition": {"auto_accept_threshold": 0.85, "data_source": "tmdb", "priority": ["local_history", "tmdb"]},
            "naming": {
                "style": {"movie": "en", "tv": "en", "anime": "en"},
                "templates": {
                    "movie": {"directory": "{title_en} ({year})", "filename": "{title_en} ({year}){suffix}"},
                    "tv": {"directory": "{title_en} ({year})", "season_dir": "Season {season:02d}", "filename": "{title_en} S{season:02d}E{episode:02d}{suffix}"},
                    "anime": {"directory": "{title_en} ({year})", "season_dir": "Season {season:02d}", "filename": "{title_en} S{season:02d}E{episode:02d}{suffix}"},
                },
                "edition_keywords": ["高码", "导演剪辑", "加长", "未分级", "收藏版", "60fps", "HDR"],
            },
            "media_types": {
                "movie": ["movie", "movies", "film", "films", "电影"],
                "tv": ["tv", "tvs", "series", "show", "shows", "电视剧"],
                "anime": ["anime", "动漫", "cartoon"],
                "music": ["music", "musics", "音乐"],
                "other": ["other", "others", "misc", "其他"],
            },
            "tmdb": {"api_key": "", "language": "zh-CN", "cache_ttl_hours": 168},
            "execution": {"conflict_strategy": "skip", "backup_before_rename": True, "dry_run_default": True, "batch_size": 100},
            "custom_patterns": [],
        }

    def get(self, key: str, default: Any = None) -> Any:
        """支持点号分隔的嵌套 key，如 'scan.max_depth'"""
        keys = key.split(".")
        node = self._data
        for k in keys:
            if isinstance(node, dict):
                node = node.get(k)
            else:
                return default
            if node is None:
                return default
        return node

    def set(self, key: str, value: Any):
        """支持点号分隔的嵌套 key"""
        keys = key.split(".")
        node = self._data
        for k in keys[:-1]:
            if k not in node or not isinstance(node[k], dict):
                node[k] = {}
            node = node[k]
        node[keys[-1]] = value

    def save(self):
        config_dir = _config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        with open(_config_path(), "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def reset_to_default(self):
        config_path = _config_path()
        default = _default_config_path()
        if default.exists():
            with open(default, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = self._minimal_config()
        self.save()

    @property
    def all(self) -> dict[str, Any]:
        return dict(self._data)

    @property
    def config_dir(self) -> Path:
        return _config_dir()
