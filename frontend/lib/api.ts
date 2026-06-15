import axios from "axios";
import type {
  TokenResponse,
  LoginRequest,
  RegisterRequest,
  StrategyGenerateRequest,
  ContentGenerateRequest,
} from "@/types";
import { setTokens, clearTokens } from "@/lib/auth";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: unknown) => void;
  reject: (reason: unknown) => void;
}> = [];

function processQueue(error: unknown) {
  failedQueue.forEach((p) => {
    if (error) p.reject(error);
    else p.resolve(undefined);
  });
  failedQueue = [];
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem("refresh_token");
      if (!refreshToken) {
        clearTokens();
        window.location.href = "/login";
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(() => {
          originalRequest.headers.Authorization = `Bearer ${localStorage.getItem("access_token")}`;
          return api(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const res = await axios.post<TokenResponse>(
          `${api.defaults.baseURL}/api/v1/auth/refresh`,
          { refresh_token: refreshToken }
        );
        const tokens = res.data;
        setTokens(tokens.access_token, tokens.refresh_token);
        processQueue(null);
        originalRequest.headers.Authorization = `Bearer ${tokens.access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError);
        clearTokens();
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export const authApi = {
  login: (body: LoginRequest) =>
    api.post<TokenResponse>("/api/v1/auth/login", body).then((r) => r.data),
  register: (body: RegisterRequest) =>
    api.post<TokenResponse>("/api/v1/auth/register", body).then((r) => r.data),
  refresh: (refresh_token: string) =>
    api.post<TokenResponse>("/api/v1/auth/refresh", { refresh_token }).then((r) => r.data),
};

export const strategyApi = {
  generate: (body: StrategyGenerateRequest) =>
    api.post("/api/v1/strategy/generate", body).then((r) => r.data),
  get: (id: string) =>
    api.get(`/api/v1/strategy/${id}`).then((r) => r.data),
  list: () =>
    api.get("/api/v1/strategy/").then((r) => r.data),
};

export const contentApi = {
  generate: (body: ContentGenerateRequest) =>
    api.post("/api/v1/content/generate", body).then((r) => r.data),
  list: (params?: { content_type?: string; strategy_id?: string }) =>
    api.get("/api/v1/content/", { params }).then((r) => r.data),
  get: (id: string) =>
    api.get(`/api/v1/content/${id}`).then((r) => r.data),
};

export const knowledgeApi = {
  upload: (file: File, doc_type: string) => {
    const form = new FormData();
    form.append("file", file);
    form.append("doc_type", doc_type);
    return api.post("/api/v1/knowledge/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then((r) => r.data);
  },
  list: () =>
    api.get("/api/v1/knowledge/").then((r) => r.data),
  delete: (id: string) =>
    api.delete(`/api/v1/knowledge/${id}`).then((r) => r.data),
};

export const chatApi = {
  send: (body: { message: string; session_id?: string | null }) =>
    api.post("/api/v1/chat/", body).then((r) => r.data),
};

export default api;
