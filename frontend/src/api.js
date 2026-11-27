import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

const api = axios.create({ baseURL: API_BASE });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("sca_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const auth = {
  signup: (name, email, password) => api.post("/api/auth/signup", { name, email, password }),
  login: (email, password) => api.post("/api/auth/login", { email, password }),
  me: () => api.get("/api/auth/me"),
};

export const datasets = {
  upload: (file) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/api/datasets/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  list: () => api.get("/api/datasets"),
  preview: (id) => api.get(`/api/datasets/${id}/preview`),
};

export const query = {
  submit: (dataset_id, queryText) => api.post("/api/query", { dataset_id, query: queryText }),
};

export const history = {
  list: () => api.get("/api/history"),
  get: (id) => api.get(`/api/history/${id}`),
};

export const reports = {
  // Protected endpoint -> fetch as blob (carries the JWT header) then trigger a save.
  download: async (historyId, fmt) => {
    const res = await api.get(`/api/reports/${historyId}/${fmt}`, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `supply_chain_report_${historyId}.${fmt}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};

export default api;
