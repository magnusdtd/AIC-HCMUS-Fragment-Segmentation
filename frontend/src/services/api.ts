import axios, { AxiosInstance, AxiosResponse } from "axios";

const API_BASE_URL = "http://aic-hcmus-noobers.duckdns.org/"

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;