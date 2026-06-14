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

export default api;
