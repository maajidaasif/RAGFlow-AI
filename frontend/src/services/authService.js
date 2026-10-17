import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:5000",
});

// ==========================
// Request Interceptor
// Automatically attach JWT token to every request
// ==========================
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// ==========================
// Response Interceptor
// Handle 401 Unauthorized globally — clear session and
// redirect to login without creating an infinite loop.
// ==========================
API.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const requestUrl = error.config?.url || "";

    // Only redirect on 401 for protected routes.
    // Never redirect on login or register failures —
    // those return 401 for bad credentials, not expired tokens.
    const isAuthEndpoint =
      requestUrl.includes("/login") ||
      requestUrl.includes("/register");

    if (status === 401 && !isAuthEndpoint) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      localStorage.removeItem("userName");
      window.location.href = "/";
    }

    return Promise.reject(error);
  }
);


// ==========================
// Register User
// ==========================
export const registerUser = async (userData) => {
  return await API.post("/register", userData);
};


// ==========================
// Login User
// ==========================
export const loginUser = async (userData) => {
  const response = await API.post("/login", userData);

  // Save JWT token after successful login
  if (response.data.access_token) {
    localStorage.setItem(
      "access_token",
      response.data.access_token
    );
  }

  return response;
};


// ==========================
// Get User Profile
// ==========================
export const getProfile = async () => {
  return await API.get("/profile");
};


// Export API instance for use in all pages/components
export default API;
