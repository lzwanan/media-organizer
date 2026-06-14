import { defineStore } from "pinia";

interface AppState {
  darkMode: boolean;
  backendUrl: string;
  backendStatus: "unknown" | "online" | "offline";
  backendVersion: string;
}

export const useAppStore = defineStore("app", {
  state: (): AppState => ({
    darkMode: window.matchMedia("(prefers-color-scheme: dark)").matches,
    backendUrl: "",
    backendStatus: "unknown",
    backendVersion: "",
  }),

  getters: {
    isOnline: (state) => state.backendStatus === "online",
  },

  actions: {
    _applyDarkMode() {
      document.documentElement.classList.toggle("app-dark", this.darkMode);
    },

    toggleDarkMode() {
      this.darkMode = !this.darkMode;
      this._applyDarkMode();
    },

    setBackendStatus(status: AppState["backendStatus"], version = "") {
      this.backendStatus = status;
      if (version) this.backendVersion = version;
    },

    /** 首次加载时同步 OS 偏好到 DOM */
    init() {
      this._applyDarkMode();
    },
  },
});
