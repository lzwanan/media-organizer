# Media Organizer

智能媒体文件整理工具 — 自动识别混乱的电影/剧集文件名，重命名为 Plex / Emby / Jellyfin 兼容的标准格式。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + PrimeVue 4 + Tailwind CSS 4 + Pinia |
| 后端 | Python 3.11 + FastAPI + SQLite |
| 桌面打包 | PyInstaller（计划中） |

## 快速开始

```bash
# 1. 安装后端依赖
pip install -r requirements.txt

# 2. 启动后端 (http://127.0.0.1:8000)
python main.py

# 3. 安装前端依赖
cd frontend && npm install

# 4. 启动前端 (http://localhost:5173)
npm run dev
```

打开浏览器访问 `http://localhost:5173`。

## 功能

- **目录扫描** — 递归扫描指定目录，自动过滤非媒体文件
- **智能识别** — 7 条内置正则规则，从文件名提取标题、年份、季集、画质
- **命名预览** — before → after 对比，支持中/EN/中+EN 四种命名风格
- **预览确认** — 执行前 dry-run 预览所有变更，支持逐项勾选删除
- **执行整理** — 重命名 + 移动文件到 Plex 标准目录结构
- **操作历史** — 每次整理自动记录，支持查看历史
- **国际化** — 中英文双语，默认中文
- **暗色模式** — 跟随系统或手动切换

## 项目结构

```
├── main.py                    # FastAPI 入口
├── requirements.txt           # Python 依赖
├── backend/
│   ├── api/routes.py          # API 路由
│   ├── scanner/scanner.py     # 目录扫描
│   ├── recognizer/            # 识别引擎
│   │   ├── recognizer.py      # 主引擎
│   │   └── pattern_matcher.py # 正则规则
│   ├── namer/generator.py     # 命名生成器
│   ├── executor/executor.py   # 执行引擎
│   ├── clients/translator.py  # 翻译客户端
│   ├── db/database.py         # SQLite 数据库
│   └── config_manager.py      # 配置管理
├── frontend/
│   ├── src/
│   │   ├── views/             # 页面 (Home/Scan/Execute/Report/History/Settings)
│   │   ├── components/        # 复用组件 (AppLayout/TreeNode/SectionCard…)
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── api/client.ts      # API 调用层
│   │   └── i18n/              # 国际化语言包
│   └── package.json
└── config/default_config.json # 默认配置
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/status` | 服务状态 |
| POST | `/api/scan` | 扫描目录 |
| POST | `/api/rename-preview` | 命名预览 |
| POST | `/api/execute` | 执行整理 |
| POST | `/api/translate` | 手动翻译 |
| GET | `/api/history` | 历史记录 |
| GET/PUT | `/api/config` | 配置读写 |

## 配置

- 翻译 API Key：`GOOGLE_TRANSLATE_API_KEY` 环境变量，或在 Settings 页面配置
- 配置文件位置：`~/.media-organizer/config.json`

## License

MIT
