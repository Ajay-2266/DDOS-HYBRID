import axios from "axios";

const API_BASE = "/api"; // proxy to Spring Boot (see note)

const axiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 60000
});

export default axiosInstance;
