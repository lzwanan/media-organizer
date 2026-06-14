import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// 响应拦截：统一错误处理
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || "网络请求失败";
    console.error("[API Error]", message);
    return Promise.reject(error);
  },
);

export interface StatusResponse {
  status: string;
  version: string;
  config_dir: string;
}

export interface ConfigResponse {
  status: string;
  data: Record<string, unknown>;
}

/** 健康检查 */
export async function fetchStatus(): Promise<StatusResponse> {
  const { data } = await api.get<StatusResponse>("/status");
  return data;
}

/** 获取完整配置 */
export async function fetchConfig(): Promise<ConfigResponse> {
  const { data } = await api.get<ConfigResponse>("/config");
  return data;
}

// ─── Scan types ───────────────────────────────────────

export interface RecognizedInfo {
  title: string | null;
  title_zh: string | null;
  title_en: string | null;
  year: number | null;
  season: number | null;
  episode: number | null;
  quality: string | null;
  edition: string | null;
  confidence: number;
  media_type: string;
  source: string;
  target_name?: string;
  target_dir?: string;
  target_path?: string;
}

export interface FileNodeResponse {
  path: string;
  name: string;
  type: string;
  size: number;
  parent: string;
  depth: number;
  extension: string;
  recognized: RecognizedInfo | null;
}

export interface ScanResponse {
  task_id: string;
  root_path: string;
  root_type: string | null;
  total_count: number;
  items: FileNodeResponse[];
}

/** 扫描目录 */
export async function fetchScan(rootPath: string, style = "en"): Promise<ScanResponse> {
  const { data } = await api.post<ScanResponse>("/scan", { root_path: rootPath, strategy: "smart", style });
  return data;
}

export interface RenamePreviewItem {
  path: string;
  target_name: string;
  target_dir: string;
  target_path: string;
}

/** 轻量重命名预览（不重新扫描） */
export async function fetchRenamePreview(items: Array<{ path: string; original_name?: string; title?: string | null; year?: number | null; season?: number | null; episode?: number | null; quality?: string | null; edition?: string | null; media_type?: string; extension?: string }>, style: string): Promise<{ status: string; style: string; items: RenamePreviewItem[] }> {
  const { data } = await api.post("/rename-preview", { items, style });
  return data;
}

export default api;
