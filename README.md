# Media Organizer

智能媒体文件整理工具 — 将混乱的下载文件重命名为 Plex / Emby / Jellyfin 兼容的标准格式。

[English](#english) | 中文

---

## 📖 目录

- [功能概览](#功能概览)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [页面与流程](#页面与流程)
- [识别规则](#识别规则)
- [命名模板](#命名模板)
- [API 文档](#api-文档)
- [配置说明](#配置说明)
- [翻译集成](#翻译集成)
- [项目结构](#项目结构)
- [开发指南](#开发指南)

---

## 功能概览

| 功能 | 说明 |
|------|------|
| **目录扫描** | 递归扫描指定目录，自动过滤 `.srt` `.nfo` `.jpg` 等非媒体文件，限制扫描深度 |
| **智能识别** | 7 条内置正则规则，从混乱文件名中提取标题、年份、季数、集数、画质、版本 |
| **命名预览** | 扫描后立即展示 before → after 对比，支持 4 种命名风格实时切换 |
| **预览确认** | 执行前 dry-run 预览所有变更，支持逐项勾选、批量删除 |
| **执行整理** | 实际重命名 + 移动文件到 Plex 标准目录结构，支持冲突处理 |
| **操作历史** | 每次整理自动记录到 SQLite，可查看历史详情 |
| **安全回滚** | 执行前自动备份原路径信息（计划中） |
| **国际化** | 中英文双语界面，默认中文 |
| **暗色模式** | 跟随系统偏好或手动切换 |

---

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue 3 + TypeScript | 3.5 |
| UI 组件库 | PrimeVue 4 (Aura 主题) | 4.3 |
| CSS 框架 | Tailwind CSS 4 | 4.0 |
| 状态管理 | Pinia | 2.3 |
| 动画 | @vueuse/motion | 2.2 |
| 国际化 | vue-i18n | 10 |
| 后端框架 | FastAPI (Python) | 0.136 |
| 数据库 | SQLite (aiosqlite) | — |
| HTTP 客户端 | httpx | 0.28 |
| 打包 | PyInstaller (计划中) | — |

---

## 快速开始

### 环境要求

- Python ≥ 3.11
- Node.js ≥ 20
- npm ≥ 9

### 安装与启动

```bash
# 1. 克隆项目
git clone https://github.com/lzwanan/media-organizer.git
cd media-organizer

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 启动后端服务 (http://127.0.0.1:8000)
python main.py

# 4. 另开终端，安装前端依赖
cd frontend
npm install

# 5. 启动前端开发服务器 (http://localhost:5173)
npm run dev
```

浏览器打开 `http://localhost:5173` 即可使用。

---

## 页面与流程

### 完整操作流程

```
首页 (/)
  │
  ├─ 输入目标目录路径
  ├─ 选择整理策略（智能识别 / 原地整理 / 仅重命名）
  └─ 点击「开始扫描」
        │
        ▼
扫描预览页 (/scan)
  │
  ├─ 查看文件树（目录可展开折叠）
  ├─ 切换命名风格（中 / EN / 中+EN / EN+中）
  ├─ 查看每条 before → after 对比
  ├─ 勾选不需要的项目 → 批量删除
  ├─ Filter 筛选（全部 / 电影 / 剧集）
  └─ 点击「Continue」
        │
        ▼
执行预览页 (/execute/:taskId)
  │
  ├─ 查看 dry-run 变更清单
  ├─ 确认无误
  └─ 点击「Confirm & Execute」
        │
        ▼
完成报告页 (/report/:taskId)
  │
  └─ 查看成功/失败/跳过统计
```

### 页面说明

| 路由 | 页面 | 功能 |
|------|------|------|
| `/` | 首页 | 目录输入、策略选择、最近路径快捷入口 |
| `/scan` | 扫描预览 | 文件树、命名预览、风格切换、筛选、勾选删除 |
| `/execute/:taskId` | 执行预览 | dry-run 变更清单，确认执行按钮 |
| `/report/:taskId` | 完成报告 | 成功/失败/跳过统计，返回首页或查看历史 |
| `/history` | 历史记录 | 历次整理记录列表（时间、路径、统计） |
| `/settings` | 设置 | 命名风格配置、TMDB/翻译 API Key |

---

## 识别规则

内置 7 条正则规则，按置信度降序排列：

| # | 规则名称 | 正则模式 | 类型 | 置信度 | 示例 |
|---|---------|---------|------|--------|------|
| 1 | 标准剧集 | `Show.S01E02.1080p` | tv | 0.90 | `Breaking.Bad.S01E05.720p.mkv` |
| 2 | 电影含年份 | `Movie.2023.1080p` | movie | 0.85 | `Kung.Fu.Hustle.2004.1080p.mkv` |
| 3 | 电影括号年份 | `Movie (2023)` | movie | 0.82 | `The Matrix (1999).mkv` |
| 4 | 无季号剧集 | `Show.E02.1080p` | tv | 0.80 | `Show.E05.720p.mkv` |
| 5 | 中文集数 | `片名.第05集.1080p` | tv | 0.80 | `琅琊榜.第05集.1080p.mp4` |
| 6 | 压制组格式 | `[Group] Title [1080p]` | auto | 0.75 | `[CtrlHD] Movie [2160p].mkv` |
| 7 | 纯数字序号 | `Title.03.mkv` | tv | 0.70 | `Show.03.mkv` |

**版本关键词**：高码、导演剪辑、加长、未分级、收藏版、60fps、HDR、杜比视界、IMAX、Remux 等。

**识别流程**：预处理（移除发布组标识）→ 正则匹配 → 取最高置信度 → 返回结构化结果。

---

## 命名模板

### 模板变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `{title}` | 根据命名风格选择的标题 | Kung Fu Hustle |
| `{title_en}` | 英文标题 | Kung Fu Hustle |
| `{title_zh}` | 中文标题 | 功夫 |
| `{year}` | 年份 | 2004 |
| `{season}` | 季数 | 1 |
| `{season:02d}` | 季数（两位补零） | 01 |
| `{episode}` | 集数 | 5 |
| `{episode:02d}` | 集数（两位补零） | 05 |
| `{quality}` | 画质 | 1080p |
| `{edition}` | 版本 | Director's Cut |
| `{suffix}` | 自动后缀 | `[1080p \| 60fps]` |
| `{ext}` | 原始扩展名 | .mkv |

### 默认模板

**电影：**
```
目录:  {title} ({year})
文件:  {title} ({year}){suffix}{ext}
```

**电视剧：**
```
目录:      {title} ({year})
季目录:    Season {season:02d}
文件:      {title} S{season:02d}E{episode:02d}{suffix}{ext}
```

### 示例

| 原文件名 | 风格 | 结果 |
|---------|------|------|
| `Kung.Fu.Hustle.2004.1080p.mkv` | EN | `Kung Fu Hustle (2004) [1080p].mkv` |
| `Kung.Fu.Hustle.2004.1080p.mkv` | 中 | `Kung Fu Hustle (2004) [1080p].mkv` |
| `Breaking.Bad.S01E05.720p.mkv` | EN | `Breaking Bad S01E05 [720p].mkv` |
| `琅琊榜.第05集.1080p.mp4` | 中 | `琅琊榜 S01E05 [1080p].mp4` |

---

## API 文档

### 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/status` | 服务健康检查 |
| GET | `/api/config` | 获取完整配置 |
| PUT | `/api/config/{key}` | 更新单个配置项 |
| POST | `/api/config/reset` | 重置为默认配置 |
| POST | `/api/scan` | 扫描目录 + 识别 + 命名预览 |
| POST | `/api/rename-preview` | 轻量命名预览（不重新扫描） |
| POST | `/api/execute` | 执行整理（dry_run 参数控制） |
| POST | `/api/translate` | 手动调用翻译 |
| GET | `/api/history` | 历史记录列表 |
| GET | `/api/history/{id}` | 历史详情（含变更明细） |

### 示例：扫描目录

```bash
curl -X POST http://127.0.0.1:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"root_path": "/path/to/movies", "style": "en"}'
```

**响应：**
```json
{
  "task_id": "scan_abc123",
  "root_path": "/path/to/movies",
  "root_type": "movie",
  "total_count": 5,
  "items": [
    {
      "path": "/path/to/movies/Kung.Fu.Hustle.2004.mkv",
      "name": "Kung.Fu.Hustle.2004.mkv",
      "type": "file",
      "size": 2147483648,
      "extension": ".mkv",
      "recognized": {
        "title": "Kung Fu Hustle",
        "year": 2004,
        "quality": null,
        "confidence": 0.85,
        "media_type": "movie",
        "source": "regex",
        "target_name": "Kung Fu Hustle (2004).mkv",
        "target_dir": "Kung Fu Hustle (2004)",
        "target_path": "Kung Fu Hustle (2004)/Kung Fu Hustle (2004).mkv"
      }
    }
  ]
}
```

### 示例：执行整理

```bash
# dry_run=true（仅预览，默认）
curl -X POST http://127.0.0.1:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"items": [{"path":"...","target_dir":"...","target_name":"..."}], "root_path": "/movies", "dry_run": true}'

# dry_run=false（实际执行，会写入磁盘）
curl -X POST http://127.0.0.1:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"items": [...], "root_path": "/movies", "dry_run": false, "conflict_strategy": "skip"}'
```

**冲突策略：**
- `skip` — 目标已存在时跳过（默认）
- `rename` — 自动添加 `_1`, `_2` 后缀
- `overwrite` — 覆盖已存在文件

### 示例：翻译

```bash
curl -X POST http://127.0.0.1:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "功夫", "target_lang": "en"}'

# 响应: {"status":"ok","translated":"Kung Fu"}
```

---

## 配置说明

配置文件位置：`~/.media-organizer/config.json`

首次启动时自动从 `config/default_config.json` 复制，也可通过 Settings 页面修改。

### 主要配置项

| 路径 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `scan.max_depth` | int | 5 | 最大扫描深度 |
| `scan.exclude_hidden` | bool | true | 跳过隐藏文件 |
| `scan.exclude_extensions` | list | `[".tmp",".srt",…]` | 排除扩展名 |
| `recognition.auto_accept_threshold` | float | 0.85 | 自动确认阈值 |
| `naming.style.movie` | string | "en" | 电影命名风格 |
| `naming.style.tv` | string | "en" | 剧集命名风格 |
| `naming.style.anime` | string | "en" | 动漫命名风格 |
| `tmdb.api_key` | string | "" | TMDB API Key |
| `translators.google.api_key` | string | "" | Google 翻译 Key |
| `execution.conflict_strategy` | string | "skip" | 冲突处理策略 |
| `execution.dry_run_default` | bool | true | 默认预览模式 |
| `execution.backup_before_rename` | bool | true | 执行前备份 |

### 环境变量

| 变量 | 说明 |
|------|------|
| `GOOGLE_TRANSLATE_API_KEY` | Google 翻译 API Key（优先于配置文件） |
| `TMDB_API_KEY` | TMDB API Key |
| `MEDIA_ORGANIZER_CONFIG_DIR` | 自定义配置目录 |

---

## 翻译集成

支持 Google Translate API 进行标题翻译。

### 配置方式

1. **环境变量**（推荐）：
   ```bash
   export GOOGLE_TRANSLATE_API_KEY=your_key_here
   ```

2. **Settings 页面**：在 `Settings → API Keys → Google Translate API Key` 填入 Key 并保存

3. **配置文件**：编辑 `~/.media-organizer/config.json`，设置 `translators.google.api_key`

### 使用方式

翻译需要**手动触发**，不会在扫描时自动调用。通过 API 调用：

```bash
POST /api/translate  {"text": "功夫", "target_lang": "en"}
```

未配置 API Key 时返回 400 错误，不会产生费用。

---

## 项目结构

```
media-organizer/
├── main.py                         # FastAPI 入口，注册路由，初始化 DB
├── requirements.txt                # Python 依赖
│
├── backend/
│   ├── api/routes.py               # 全部 API 路由（15 个端点）
│   ├── scanner/scanner.py          # 异步目录递归扫描 + 媒体类型推测
│   ├── recognizer/
│   │   ├── recognizer.py           # 识别主引擎（RecognizedInfo 数据结构）
│   │   └── pattern_matcher.py      # 7 条正则规则 + 版本关键词 + 垃圾检测
│   ├── namer/generator.py          # 模板引擎（4 种命名风格，11 个模板变量）
│   ├── executor/executor.py        # 文件重命名/移动 + 冲突处理（skip/rename/overwrite）
│   ├── clients/translator.py       # Google Translate API 客户端
│   ├── db/database.py              # SQLite 连接 + 4 张表初始化 + CRUD
│   └── config_manager.py           # JSON 配置读写 + 平台路径适配
│
├── frontend/
│   ├── index.html
│   ├── vite.config.ts              # Vite 配置 + Tailwind 插件 + API 代理
│   ├── tsconfig.json
│   ├── package.json
│   └── src/
│       ├── main.ts                 # Vue 入口，注册 Pinia/Router/i18n/PrimeVue/Motion
│       ├── App.vue                 # 根组件（Toast + RouterView）
│       ├── router.ts               # 6 个页面路由
│       ├── api/client.ts           # Axios 封装 + 全部 API 调用函数 + 类型定义
│       ├── i18n/
│       │   ├── index.ts            # vue-i18n 实例（默认 zh-CN，localStorage 持久化）
│       │   ├── zh-CN.ts            # 中文语言包
│       │   └── en-US.ts            # 英文语言包
│       ├── stores/
│       │   ├── app.ts              # 全局状态（暗色模式、后端连接状态）
│       │   └── scan.ts             # 扫描结果缓存 + tree getter + 统计
│       ├── views/
│       │   ├── Home.vue            # 首页：目录输入 + 策略选择 + CTA
│       │   ├── Scan.vue            # 扫描预览：文件树 + 命名切换 + Filter + 删除
│       │   ├── Execute.vue         # 执行预览：dry-run 清单 + 确认执行
│       │   ├── Report.vue          # 完成报告：成功/失败/跳过统计
│       │   ├── History.vue         # 历史记录列表
│       │   └── Settings.vue        # 命名风格 + API Key 配置
│       ├── components/
│       │   ├── AppLayout.vue       # 全局布局（导航栏 + 主内容区 + 状态栏）
│       │   ├── NavItem.vue         # 导航链接组件
│       │   ├── StatusBar.vue       # 底部状态栏（连接状态 + 版本）
│       │   ├── SectionCard.vue     # 统一卡片容器
│       │   ├── FolderInput.vue     # 目录输入组件（带清除 + 浏览按钮）
│       │   ├── StrategyPicker.vue  # 策略选择器
│       │   └── TreeNode.vue        # 递归文件树（目录展开/折叠 + 命名预览 + 复选框）
│       └── styles/
│           └── global.css          # Tailwind 主题 + 暗色模式 + 滚动条 + 页面过渡
│
├── config/default_config.json      # 默认配置模板（首次启动复制到 ~/.media-organizer/）
└── README.md
```

---

## 开发指南

### 本地开发

```bash
# 终端 1 — 后端（自动重载）
python main.py

# 终端 2 — 前端（HMR 热更新）
cd frontend && npm run dev
```

后端 `127.0.0.1:8000`，前端 `localhost:5173`（自动代理 API 请求到后端）。

### Git 提交规范

```
feat:     新功能
fix:      Bug 修复
refactor: 重构
docs:     文档更新
style:    代码格式
chore:    构建/工具
```

### 数据库

SQLite 文件位于 `~/.media-organizer/media_organizer.db`，包含 4 张表：

| 表名 | 说明 |
|------|------|
| `history` | 整理操作记录（时间、路径、统计） |
| `changes` | 每次操作的详细变更（原路径 → 新路径） |
| `user_history` | 用户识别缓存（文件名 → 识别结果） |
| `tmdb_cache` | TMDB API 搜索结果缓存 |

---

## License

MIT

---

<a id="english"></a>

## English

**Media Organizer** is a desktop tool that automatically renames and reorganizes your movie and TV show files into Plex / Emby / Jellyfin compatible formats.

### Quick Start

```bash
pip install -r requirements.txt
python main.py                # Backend: http://127.0.0.1:8000

cd frontend && npm install && npm run dev   # Frontend: http://localhost:5173
```

### Key Features

- **Smart Recognition** — 7 regex patterns extract title, year, season, episode, quality from messy filenames
- **Naming Preview** — See before → after comparison before any changes are made
- **4 Naming Styles** — English / Chinese / Bilingual (ZH+EN) / Bilingual (EN+ZH)
- **Dry-run Mode** — Preview all changes without touching files; confirm to execute
- **Operation History** — All operations recorded in SQLite for audit
- **i18n** — Chinese (default) and English UI
- **Dark Mode** — Follows system preference or manual toggle

### Configuration

Translation API key via `GOOGLE_TRANSLATE_API_KEY` env var or Settings page.
Config file: `~/.media-organizer/config.json`
