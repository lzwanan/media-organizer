# Reasonix project memory

Notes the user pinned via the `#` prompt prefix. The whole file is
loaded into the immutable system prefix every session — keep it terse.

- 媒体整理工具 - 详细设计文档

## 文档信息

| 项目 | 内容 |
|------|------|
| 文档版本 | v1.0 |
| 更新日期 | 2026-01-15 |
| 项目名称 | Media Organizer |
| 目标用户 | 需要整理本地媒体资源的个人用户 |

---

## 一、项目概述

### 1.1 项目目标

开发一个轻量级的媒体文件整理工具，解决下载资源命名混乱、无法被媒体服务器（Plex/Emby/Jellyfin）刮削的问题。

### 1.2 核心功能

1. **目录扫描**：扫描用户指定目录，识别媒体文件
2. **智能识别**：从混乱文件名中提取元数据（标题、年份、季数、集数等）
3. **预览对比**：展示整理前后的变化，支持逐项确认
4. **灵活整理**：支持原地整理、按类型重组、仅重命名三种模式
5. **命名配置**：用户可自定义命名风格（中文/英文/双语）
6. **规则管理**：用户可通过界面管理识别规则和命名模板

### 1.3 设计原则

- **开箱即用**：启动服务即可使用，无需手动配置
- **用户可控**：执行前预览所有变更，支持逐项确认
- **安全优先**：支持预览模式，记录操作日志，支持回滚
- **配置可视**：所有配置项在前端界面完成

---

## 二、技术架构

### 2.1 技术栈选型

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 + Element Plus | 管理界面 |
| 后端 | Python 3.11 + FastAPI | API服务 |
| 数据库 | SQLite | 历史记录、用户缓存 |
| 桌面打包 | PyInstaller | 打包为单文件可执行程序 |
| 配置存储 | JSON | 用户配置（位于用户目录） |

### 2.2 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户界面层                               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │ 首页    │ │ 扫描页  │ │ 预览页  │ │ 执行页  │ │ 设置页  │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP/WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          API 层 (FastAPI)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ 目录扫描 │ │ 预览生成 │ │ 确认提交 │ │ 执行整理 │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐                                      │
│  │ 规则管理 │ │ 配置管理 │                                      │
│  └──────────┘ └──────────┘                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         核心服务层                               │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐  │
│  │ 文件扫描器 │ │ 识别引擎   │ │ 命名生成器 │ │ 执行引擎   │  │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘  │
│  ┌────────────┐ ┌────────────┐                                  │
│  │ TMDB客户端 │ │ 配置管理器 │                                  │
│  └────────────┘ └────────────┘                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         数据层                                   │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐                  │
│  │   SQLite   │ │   JSON     │ │   缓存     │                  │
│  │ (历史记录) │ │ (配置文件) │ │ (本地缓存) │                  │
│  └────────────┘ └────────────┘ └────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 项目目录结构

```
media-organizer/
├── main.py                    # 入口文件
├── requirements.txt           # Python依赖
│
├── backend/                   # 后端代码
│   ├── __init__.py
│   ├── api/                   # API路由
│   │   ├── __init__.py
│   │   ├── routes.py          # 主路由
│   │   ├── config_routes.py   # 配置接口
│   │   └── websocket.py       # WebSocket进度推送
│   │
│   ├── scanner/               # 扫描模块
│   │   ├── __init__.py
│   │   ├── scanner.py         # 目录扫描
│   │   └── file_analyzer.py   # 文件分析
│   │
│   ├── recognizer/            # 识别模块
│   │   ├── __init__.py
│   │   ├── recognizer.py      # 主识别引擎
│   │   ├── pattern_matcher.py # 正则匹配
│   │   └── history.py         # 用户历史缓存
│   │
│   ├── namer/                 # 命名模块
│   │   ├── __init__.py
│   │   ├── generator.py       # 命名生成器
│   │   └── template.py        # 模板处理
│   │
│   ├── executor/              # 执行模块
│   │   ├── __init__.py
│   │   ├── executor.py        # 文件操作执行
│   │   └── rollback.py        # 回滚管理
│   │
│   ├── clients/               # 外部API客户端
│   │   ├── __init__.py
│   │   └── tmdb_client.py     # TMDB API
│   │
│   ├── db/                    # 数据库
│   │   ├── __init__.py
│   │   ├── database.py        # SQLite连接
│   │   └── models.py          # 数据模型
│   │
│   └── config_manager.py      # 配置管理器
│
├── frontend/                  # 前端代码
│   ├── index.html
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── views/
│   │   │   ├── Home.vue       # 首页（目录选择）
│   │   │   ├── Scan.vue       # 扫描预览页
│   │   │   ├── Execute.vue    # 执行进度页
│   │   │   ├── Report.vue     # 完成报告页
│   │   │   └── Settings.vue   # 设置页
│   │   ├── components/
│   │   │   ├── FileTree.vue   # 文件树组件
│   │   │   ├── CompareView.vue # 对比视图
│   │   │   └── ProgressBar.vue # 进度条
│   │   └── api/
│   │       └── client.js      # API调用
│   └── package.json
│
├── config/                    # 默认配置模板（首次启动复制到用户目录）
│   └── default_config.json
│
└── build/                     # 打包配置
    └── pyinstaller.spec
```

---

## 三、核心功能详细设计

### 3.1 配置管理模块

#### 3.1.1 配置存储位置

```
Windows: %USERPROFILE%\.media-organizer\config.json
Mac: ~/.media-organizer/config.json
Linux: ~/.media-organizer/config.json
```

#### 3.1.2 默认配置结构

```json
{
  "version": "1.0",
  "scan": {
    "max_depth": 5,
    "exclude_hidden": true,
    "exclude_extensions": [".tmp", ".cache", ".log", ".srt"],
    "max_file_size_mb": 10240
  },
  "recognition": {
    "auto_accept_threshold": 0.85,
    "data_source": "tmdb",
    "priority": ["local_history", "tmdb"]
  },
  "naming": {
    "style": {
      "movie": "en",
      "tv": "en",
      "anime": "en"
    },
    "templates": {
      "movie": {
        "directory": "{title_en} ({year})",
        "filename": "{title_en} ({year}){suffix}"
      },
      "tv": {
        "directory": "{title_en} ({year})",
        "season_dir": "Season {season:02d}",
        "filename": "{title_en} S{season:02d}E{episode:02d}{suffix}"
      },
      "anime": {
        "directory": "{title_en} ({year})",
        "season_dir": "Season {season:02d}",
        "filename": "{title_en} S{season:02d}E{episode:02d}{suffix}"
      }
    },
    "edition_keywords": ["高码", "导演剪辑", "加长", "未分级", "收藏版", "60fps", "HDR"]
  },
  "media_types": {
    "movie": ["movie", "movies", "film", "films", "电影", "📀"],
    "tv": ["tv", "tvs", "series", "show", "shows", "电视剧", "📺"],
    "anime": ["anime", "动漫", "cartoon", "🎬"],
    "music": ["music", "musics", "音乐", "🎵"],
    "other": ["other", "others", "misc", "其他", "📁"]
  },
  "tmdb": {
    "api_key": "",
    "language": "zh-CN",
    "cache_ttl_hours": 168
  },
  "execution": {
    "conflict_strategy": "skip",
    "backup_before_rename": true,
    "dry_run_default": true,
    "batch_size": 100
  },
  "custom_patterns": []
}
```

#### 3.1.3 配置管理器接口

```python
# backend/config_manager.py

class ConfigManager:
    def __init__(self): ...
    def get(self, key: str, default=None) -> Any: ...
    def set(self, key: str, value: Any): ...
    def save(self): ...
    def reset_to_default(self): ...
```

### 3.2 扫描模块

#### 3.2.1 数据结构

```python
# backend/scanner/scanner.py

@dataclass
class FileNode:
    path: str           # 绝对路径
    name: str           # 原始文件名
    type: str           # "file" 或 "directory"
    size: int           # 文件大小（字节）
    parent: str         # 父目录路径
    depth: int          # 相对根目录的深度
    extension: str      # 文件扩展名（小写）

@dataclass
class ScanResult:
    root_path: str
    root_type: Optional[str]
    items: List[FileNode]
    total_count: int
    scan_time: str
```

#### 3.2.2 扫描逻辑

1. 异步遍历目录树
2. 跳过隐藏文件/目录
3. 过滤排除的扩展名
4. 限制扫描深度（max_depth）
5. 返回文件节点列表

### 3.3 识别模块

#### 3.3.1 数据结构

```python
# backend/recognizer/recognizer.py

class MediaType(Enum):
    MOVIE = "movie"
    TV = "tv"
    ANIME = "anime"
    MUSIC = "music"
    UNKNOWN = "unknown"

@dataclass
class RecognizedInfo:
    original_path: str
    original_name: str
    title_zh: Optional[str]    # 中文标题
    title_en: Optional[str]    # 英文标题
    year: Optional[int]
    season: Optional[int]
    episode: Optional[int]
    quality: Optional[str]     # 1080p, 2160p, 4K等
    edition: Optional[str]     # 导演剪辑版、高码版等
    confidence: float          # 0-1
    media_type: MediaType
    source: str                # "local_history" / "tmdb" / "regex" / "manual"
```

#### 3.3.2 识别流程

```
用户文件名
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 1. 预处理                                              │
│    - 移除发布组标识（【xxx】、[xxx]）                  │
│    - 移除多余空格和特殊字符                            │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 2. 查询本地历史缓存（user_history）                    │
│    - 命中且置信度≥阈值 → 返回结果                      │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 3. 正则模式匹配（按用户自定义规则+内置规则）            │
│    - 提取标题、年份、季数、集数、画质                  │
│    - 置信度按规则预设值                                 │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 4. TMDB API 搜索                                       │
│    - 使用提取的标题搜索                                │
│    - 获取官方中文名、英文名、年份                      │
│    - 置信度 = 0.85（TMDB命中）                         │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 5. 返回结果                                            │
│    - 置信度≥0.85 → 可自动确认                          │
│    - 0.5≤置信度<0.85 → 需要用户确认                    │
│    - 置信度<0.5 → 强制用户手动输入                     │
└─────────────────────────────────────────────────────────┘
```

#### 3.3.3 内置正则模式

| 名称 | 正则表达式 | 类型 | 置信度 |
|------|-----------|------|--------|
| 标准剧集 | `(.+?)\.S(\d{2})E(\d{2})\.?(\d{3,4}p)?` | tv | 0.90 |
| 无季号剧集 | `(.+?)\.E(\d{2})\.?(\d{3,4}p)?` | tv | 0.80 |
| 电影含年份 | `(.+?)\.(\d{4})\.?(\d{3,4}p)?` | movie | 0.85 |
| 压制组格式 | `\[(.+?)\](.+?)\[(\d{3,4}p?)\]` | auto | 0.75 |
| 中文集数 | `(.+?)\.第(\d+)集\.?(\d{3,4}p)?` | tv | 0.80 |
| 纯数字序号 | `(.+?)\.(\d{1,3})\.(mkv\|mp4\|avi)` | tv | 0.70 |

### 3.4 TMDB 客户端模块

#### 3.4.1 接口定义

```python
# backend/clients/tmdb_client.py

class TMDBClient:
    def __init__(self, api_key: str = None):
        # 如果未提供API Key，使用内置只读Key
        pass
    
    async def search_movie(self, query: str) -> Optional[Dict]:
        """搜索电影，返回中英文名和年份"""
        pass
    
    async def search_tv(self, query: str) -> Optional[Dict]:
        """搜索电视剧"""
        pass
    
    async def test_connection(self) -> bool:
        """测试连接是否正常"""
        pass
```

#### 3.4.2 API 响应格式

```python
{
    "title_zh": "功夫",
    "title_en": "Kung Fu Hustle",
    "year": 2004,
    "overview": "故事发生在1940年代的上海...",
    "poster_path": "/abc123.jpg"
}
```

#### 3.4.3 缓存策略

- 搜索结果缓存到 SQLite，有效期 config.tmdb.cache_ttl_hours
- 缓存键：query的MD5哈希

### 3.5 命名生成模块

#### 3.5.1 命名风格

| 风格 | 说明 | 示例 |
|------|------|------|
| `zh` | 中文名 | `功夫 (2004)` |
| `en` | 英文名 | `Kung Fu Hustle (2004)` |
| `bilingual` | 中英文双语 | `功夫 Kung Fu Hustle (2004)` |

#### 3.5.2 模板变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `{title_zh}` | 中文标题 | 功夫 |
| `{title_en}` | 英文标题 | Kung Fu Hustle |
| `{year}` | 年份 | 2004 |
| `{season}` | 季数（整数） | 1 |
| `{season:02d}` | 季数（两位） | 01 |
| `{episode}` | 集数（整数） | 1 |
| `{episode:02d}` | 集数（两位） | 01 |
| `{quality}` | 画质 | 1080p |
| `{edition}` | 版本 | 导演剪辑版 |
| `{suffix}` | 自动构建的后缀 | `- 1080p` |

#### 3.5.3 生成逻辑

```python
# backend/namer/generator.py

class NamingGenerator:
    def generate(self, info: RecognizedInfo) -> Dict[str, str]:
        """返回 {directory, season_dir, filename}"""
        pass
    
    def preview(self, info: RecognizedInfo, style: str) -> str:
        """预览指定风格下的命名结果"""
        pass
```

### 3.6 执行模块

#### 3.6.1 执行流程

```
用户确认项列表
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 1. 预览模式（dry_run=true）                            │
│    - 模拟所有文件操作                                   │
│    - 返回变更清单，不实际执行                           │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 2. 备份（如果配置启用）                                 │
│    - 在根目录创建 .organizer_backup 文件夹              │
│    - 保存原文件名清单为 backup.json                     │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 3. 执行文件操作                                         │
│    - 创建目标目录                                       │
│    - 移动/重命名文件                                    │
│    - 记录操作日志                                       │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 4. 冲突处理                                            │
│    - skip: 跳过，记录到跳过列表                         │
│    - overwrite: 覆盖（谨慎使用）                        │
│    - rename: 自动重命名（添加_1,_2）                    │
│    - ask: 弹窗询问用户                                 │
└─────────────────────────────────────────────────────────┘
```

#### 3.6.2 回滚机制

```python
# backend/executor/rollback.py

class RollbackManager:
    def record_operation(self, original: str, new: str): ...
    def rollback(self, steps: int = 0): ...  # steps=0 表示全部回滚
    def get_history(self) -> List[Dict]: ...
```

### 3.7 数据库设计

#### 3.7.1 SQLite 表结构

```sql
-- 整理历史记录
CREATE TABLE history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    root_path TEXT NOT NULL,
    total_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    skipped_count INTEGER DEFAULT 0
);

-- 文件变更记录
CREATE TABLE changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    history_id INTEGER NOT NULL,
    original_path TEXT NOT NULL,
    new_path TEXT NOT NULL,
    status TEXT NOT NULL,  -- 'success', 'failed', 'skipped'
    error_message TEXT,
    FOREIGN KEY (history_id) REFERENCES history(id)
);

-- 用户历史缓存（识别映射）
CREATE TABLE user_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_pattern TEXT NOT NULL,  -- 原文件名模式
    normalized_title TEXT NOT NULL,   -- 规范化标题
    title_zh TEXT,
    title_en TEXT,
    year INTEGER,
    media_type TEXT NOT NULL,
    tmdb_id INTEGER,
    use_count INTEGER DEFAULT 1,
    last_used DATETIME,
    UNIQUE(original_pattern)
);

-- TMDB 搜索结果缓存
CREATE TABLE tmdb_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    query_hash TEXT UNIQUE NOT NULL,
    result_json TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL
);

-- 自定义识别规则
CREATE TABLE custom_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    pattern TEXT NOT NULL,
    media_type TEXT NOT NULL,
    confidence REAL DEFAULT 0.7,
    enabled INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 四、API 接口设计

### 4.1 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/scan` | 扫描目录 |
| POST | `/api/preview` | 生成预览变更 |
| POST | `/api/execute` | 执行整理 |
| GET | `/api/config` | 获取所有配置 |
| GET | `/api/config/{key}` | 获取单个配置 |
| PUT | `/api/config/{key}` | 更新配置 |
| POST | `/api/config/reset` | 重置配置 |
| GET | `/api/config/media-types` | 获取目录类型映射 |
| POST | `/api/config/patterns` | 添加自定义规则 |
| DELETE | `/api/config/patterns/{id}` | 删除自定义规则 |
| GET | `/api/history` | 获取整理历史 |
| GET | `/api/history/{id}` | 获取历史详情 |
| POST | `/api/rollback/{history_id}` | 回滚到某次整理前 |
| GET | `/api/status` | 服务状态 |
| WS | `/ws/progress/{task_id}` | 实时进度推送 |

### 4.2 请求/响应示例

#### 4.2.1 扫描目录

**请求**
```json
POST /api/scan
{
    "root_path": "D:/Downloads/Media",
    "strategy": "smart"
}
```

**响应**
```json
{
    "task_id": "scan_20240115120000",
    "root_path": "D:/Downloads/Media",
    "root_type": null,
    "total_count": 23,
    "items": [
        {
            "path": "D:/Downloads/Media/Kung.Fu.Hustle.2004.mkv",
            "name": "Kung.Fu.Hustle.2004.mkv",
            "type": "file",
            "size": 2147483648,
            "parent": "D:/Downloads/Media",
            "depth": 1,
            "recognized": {
                "original_name": "Kung.Fu.Hustle.2004.mkv",
                "title_zh": "功夫",
                "title_en": "Kung Fu Hustle",
                "year": 2004,
                "quality": null,
                "confidence": 0.85,
                "media_type": "movie",
                "source": "tmdb"
            }
        }
    ]
}
```

#### 4.2.2 执行整理

**请求**
```json
POST /api/execute
{
    "confirmed_items": [
        {
            "item_path": "D:/Downloads/Media/Kung.Fu.Hustle.2004.mkv",
            "action": "confirm",
            "edited_target": null
        }
    ],
    "dry_run": false
}
```

**响应**
```json
{
    "task_id": "exec_20240115120001",
    "status": "running",
    "total": 23,
    "dry_run": false
}
```

### 4.3 WebSocket 进度推送

```json
// 服务端推送消息格式
{
    "type": "progress",
    "task_id": "exec_20240115120001",
    "current": 12,
    "total": 23,
    "percentage": 52,
    "current_file": "Kung.Fu.Hustle.2004.mkv",
    "status": "processing"
}

{
    "type": "complete",
    "task_id": "exec_20240115120001",
    "result": {
        "success": 21,
        "failed": 1,
        "skipped": 1
    }
}

{
    "type": "error",
    "task_id": "exec_20240115120001",
    "error": "Permission denied: D:/Downloads/Media/xxx.mkv"
}
```

---

## 五、前端页面设计

### 5.1 页面结构

```
┌─────────────────────────────────────────────────────────────────┐
│  📦 Media Organizer                    [首页] [历史] [设置]      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [当前页面内容区域]                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 页面列表

| 页面 | 路由 | 功能 |
|------|------|------|
| 首页 | `/` | 目录选择，开始整理 |
| 扫描预览 | `/scan` | 展示扫描结果，逐项确认 |
| 执行进度 | `/execute/:taskId` | 展示执行进度和实时日志 |
| 报告 | `/report/:taskId` | 整理完成统计报告 |
| 历史 | `/history` | 查看历史整理记录 |
| 设置 | `/settings` | 配置管理 |

### 5.3 核心组件

#### 5.3.1 目录选择器（首页）

```
┌─────────────────────────────────────────────────────────────────┐
│  📁 目标目录                                                    │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ D:\Downloads\Media                                    [浏览]││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ⚙️ 整理策略                                                    │
│  ● 智能识别（自动判断目录类型）                                  │
│  ○ 原地整理（保持现有目录结构）                                  │
│  ○ 仅重命名（不移动位置）                                       │
│                                                                 │
│  [开始扫描]                                                      │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.3.2 文件树对比视图（扫描预览页）

```
┌─────────────────────────────────────────────────────────────────┐
│  📁 D:\Downloads\Media                                [全部确认] │
│  │                                                              │
│  ├─ 📁 Movies/                                        [确认目录] │
│  │  │                                                           │
│  │  └─ 📄 Kung.Fu.Hustle.2004.mkv                    [✓确认]   │
│  │     ┌─────────────────────────────────────────────────────┐ │
│  │     │ 执行前: Movies/Kung.Fu.Hustle.2004.mkv              │ │
│  │     │ 执行后: Movies/Kung Fu Hustle (2004)/               │ │
│  │     │         Kung Fu Hustle (2004).mkv                   │ │
│  │     │                              [编辑] [跳过] [确认]   │ │
│  │     └─────────────────────────────────────────────────────┘ │
│  │                                                              │
│  └─ 📁 TV/                                            [确认目录] │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 已确认: 18/23  |  待处理: 5  |  冲突: 0      [执行整理]     ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

#### 5.3.3 设置页面

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚙️ 设置                                              [保存]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─ 🏷️ 命名风格 ─────────────────────────────────────────────┐ │
│  │  电影:   ● 中文  ○ 英文  ○ 中英双语                       │ │
│  │  电视剧: ● 中文  ○ 英文  ○ 中英双语                       │ │
│  │  动漫:   ● 中文  ○ 英文  ○ 中英双语                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─ 📝 命名模板 ─────────────────────────────────────────────┐ │
│  │  电影:   [ {title_en} ({year})              ] [重置]      │ │
│  │  电视剧: [ {title_en} S{season:02d}E{episode:02d} ]      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─ 🎯 识别设置 ─────────────────────────────────────────────┐ │
│  │  自动确认阈值: [━━━━●━━━━━━━━━━━━] 85%                    │ │
│  │  TMDB API Key: [ ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪ ] [测试连接]            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─ 📂 目录类型映射 ─────────────────────────────────────────┐ │
│  │  电影目录关键词: [movie, movies, film, 电影]  [+ 添加]     │ │
│  │  电视剧目录关键词: [tv, series, show, 电视剧] [+ 添加]     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─ 🔧 高级设置 ─────────────────────────────────────────────┐ │
│  │  ▼ 自定义识别规则                                          │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 正则: (.+?)\.(\d{4})\.(\d{3,4}p)    类型: 电影  [删除]│  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  [+ 添加规则]                                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  [恢复默认]                              [保存并应用]           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 六、开发任务分解

### 6.1 第一阶段：基础框架（3天）

| 任务 | 优先级 | 预估工时 |
|------|--------|---------|
| 项目初始化，目录结构搭建 | P0 | 2h |
| 配置管理器实现（JSON读写） | P0 | 3h |
| 基础API框架（FastAPI） | P0 | 2h |
| 前端路由和页面框架（Vue Router） | P0 | 2h |
| 前后端联调基础 | P0 | 1h |

### 6.2 第二阶段：核心功能（5天）

| 任务 | 优先级 | 预估工时 |
|------|--------|---------|
| 目录扫描模块实现 | P0 | 4h |
| 正则识别引擎实现 | P0 | 6h |
| TMDB客户端集成 | P0 | 4h |
| 命名生成器实现 | P0 | 3h |
| 扫描预览页面 | P0 | 5h |
| 文件执行模块 | P0 | 4h |

### 6.3 第三阶段：UI完善（3天）

| 任务 | 优先级 | 预估工时 |
|------|--------|---------|
| 首页目录选择UI | P0 | 2h |
| 文件树对比组件 | P0 | 4h |
| 执行进度页面+WebSocket | P0 | 4h |
| 报告页面 | P1 | 2h |
| 设置页面 | P0 | 4h |
| 历史记录页面 | P1 | 2h |

### 6.4 第四阶段：体验优化（2天）

| 任务 | 优先级 | 预估工时 |
|------|--------|---------|
| 批量操作功能 | P0 | 3h |
| 手动编辑弹窗 | P0 | 3h |
| 错误处理和用户提示 | P0 | 3h |
| 性能优化（大目录扫描） | P1 | 2h |
| 回滚功能 | P1 | 2h |

### 6.5 第五阶段：打包发布（2天）

| 任务 | 优先级 | 预估工时 |
|------|--------|---------|
| PyInstaller打包配置 | P0 | 3h |
| 前端构建优化 | P0 | 2h |
| 跨平台测试（Win/Mac/Linux） | P0 | 4h |
| 文档编写 | P1 | 3h |

**总预估工时**：约 70-80 小时（10-12个工作日）

---

## 七、开发规范

### 7.1 代码规范

- Python: 遵循 PEP8，使用 black 格式化
- JavaScript/Vue: 使用 ESLint + Prettier
- 类型注解: Python 使用 typing，前端使用 TypeScript

### 7.2 Git 提交规范

```
feat: 新功能
fix: Bug修复
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具配置
```

### 7.3 测试要求

- 核心模块（识别引擎、命名生成器）需有单元测试
- API 接口需有集成测试
- 测试覆盖率目标 >70%

---

## 八、风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| TMDB API 不稳定 | 中 | 中 | 增加重试机制；降级到本地缓存 |
| 大目录扫描卡顿 | 中 | 中 | 异步扫描+分页加载；限制扫描深度 |
| 文件名编码问题 | 低 | 中 | 统一使用UTF-8处理 |
| 权限不足无法操作文件 | 中 | 高 | 执行前检查权限；跳过无权限文件 |
| 用户误操作导致数据丢失 | 中 | 高 | 默认预览模式；备份机制；支持回滚 |

---

## 九、参考资料

1. [Plex 命名规范](https://support.plex.tv/articles/naming-and-organizing-your-tv-show-files/)
2. [Emby 命名规范](https://support.emby.media/support/solutions/articles/44001159110-naming-movie-files)
3. [Jellyfin 命名规范](https://jellyfin.org/docs/general/server/media/movies)
4. [TMDB API 文档](https://developers.themoviedb.org/3)
5. [TheTVDB 命名规范](https://www.thetvdb.com/api)

---

## 十、附录

### 附录A：环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `MEDIA_ORGANIZER_CONFIG_DIR` | 配置目录 | `~/.media-organizer` |
| `TMDB_API_KEY` | TMDB API密钥 | （内置只读Key） |
| `LOG_LEVEL` | 日志级别 | `INFO` |

### 附录B：命令行参数

```bash
# 启动服务
media-organizer --port 5173 --host 127.0.0.1

# 静默模式（不打开浏览器）
media-organizer --no-browser

# 指定配置目录
media-organizer --config-dir /path/to/config

# 查看版本
media-organizer --version
```
