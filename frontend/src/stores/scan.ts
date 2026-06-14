import { defineStore } from "pinia";
import type { ScanResponse, FileNodeResponse } from "@/api/client";

interface ScanState {
  result: ScanResponse | null;
  loading: boolean;
  error: string | null;
}

export const useScanStore = defineStore("scan", {
  state: (): ScanState => ({
    result: null,
    loading: false,
    error: null,
  }),

  getters: {
    /** 文件节点（过滤掉目录，只保留文件） */
    files: (state) => state.result?.items.filter((n) => n.type === "file") ?? [],

    /** 目录节点 */
    dirs: (state) => state.result?.items.filter((n) => n.type === "directory") ?? [],

    /** 构建目录树：{ [parentPath]: children[] } */
    tree(): Record<string, FileNodeResponse[]> {
      const map: Record<string, FileNodeResponse[]> = {};
      if (!this.result) return map;
      for (const node of this.result.items) {
        const key = node.parent;
        if (!map[key]) map[key] = [];
        map[key].push(node);
      }
      return map;
    },
  },

  actions: {
    setResult(result: ScanResponse) {
      this.result = result;
      this.error = null;
    },

    setLoading(v: boolean) {
      this.loading = v;
    },

    setError(msg: string) {
      this.error = msg;
      this.result = null;
    },

    reset() {
      this.result = null;
      this.loading = false;
      this.error = null;
    },
  },
});
