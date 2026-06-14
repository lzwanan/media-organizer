export default {
  nav: {
    home: "首页",
    history: "历史",
    settings: "设置",
  },
  home: {
    title: "整理你的媒体库",
    subtitle: "自动识别混乱的媒体文件名，重命名为 Plex、Emby、Jellyfin 兼容格式。",
    targetDir: "目标目录",
    targetDirPlaceholder: "输入或粘贴目录路径…",
    browse: "浏览",
    strategy: "整理策略",
    strategies: {
      smart: { label: "智能识别", desc: "自动判断文件类型，按 Plex 标准重组目录" },
      inplace: { label: "原地整理", desc: "保持现有目录结构，仅重命名不规范文件" },
      renameOnly: { label: "仅重命名", desc: "不移动文件位置，只在原地修改名称" },
    },
    startScan: "开始扫描",
    startScanDisabled: "输入目录路径开始",
    features: {
      detect: {
        title: "智能识别",
        desc: "从混乱的文件名中提取电影和剧集元数据",
      },
      preview: {
        title: "预览确认",
        desc: "执行前逐项查看所有变更",
      },
      rollback: {
        title: "安全回滚",
        desc: "操作前自动备份，可随时恢复",
      },
    },
  },
  scan: {
    back: "返回首页",
    noData: "暂无扫描数据，请先扫描一个目录。",
    noFiles: "目录中未发现媒体文件。",
    filters: { all: "全部", movie: "电影", tv: "剧集", junk: "垃圾", empty: "空目录" },
    naming: "命名",
    continue: "继续",
    delete: "删除",
    deleteConfirm: "确认删除",
    deleteMsg: "确定要删除选中的 {count} 项吗？此操作不可撤销。",
    cancel: "取消",
    selected: "已选",
    suggestedRemove: "建议删除",
    pending: "待处理",
  },
  status: {
    connected: "已连接",
    disconnected: "未连接",
  },
  lang: "语言",
}
