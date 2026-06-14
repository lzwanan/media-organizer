export default {
  nav: {
    home: "Home",
    history: "History",
    settings: "Settings",
  },
  home: {
    title: "Organize your media library",
    subtitle: "Automatically rename and restructure your movie and TV files into Plex, Emby, and Jellyfin compatible formats.",
    targetDir: "Target directory",
    targetDirPlaceholder: "Paste a directory path…",
    browse: "Browse",
    strategy: "Strategy",
    strategies: {
      smart: { label: "Smart", desc: "Detect media type and reorganize by Plex standard" },
      inplace: { label: "In Place", desc: "Keep folder structure, only rename messy files" },
      renameOnly: { label: "Rename Only", desc: "Rename in place without moving anything" },
    },
    startScan: "Start Scan",
    startScanDisabled: "Enter a directory to begin",
    features: {
      detect: {
        title: "Smart Detection",
        desc: "Extract movie and TV metadata from messy filenames",
      },
      preview: {
        title: "Preview First",
        desc: "Review every change before execution",
      },
      rollback: {
        title: "Safe Rollback",
        desc: "Auto-backup before every operation",
      },
    },
  },
  status: {
    connected: "Connected",
    disconnected: "Disconnected",
  },
  lang: "Language",
}
