const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

const getAuthHeaders = (token, extraHeaders = {}) => {
  const headers = { ...extraHeaders };
  const activeToken = token || localStorage.getItem('auth_token');
  if (activeToken) {
    headers["Authorization"] = `Bearer ${activeToken}`;
  }
  return headers;
};

// ================= AUTHENTICATION APIS =================

export const registerUser = async (name, email, password) => {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name, email, password }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Registration failed. Please check your details.");
  }

  return await response.json();
};

export const loginUser = async (email, password) => {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Login failed. Invalid email or password.");
  }

  return await response.json();
};

export const fetchCurrentUser = async (token) => {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: getAuthHeaders(token),
  });

  if (!response.ok) {
    throw new Error("Failed to authenticate session");
  }

  return await response.json();
};

// ================= APPLICATION APIS =================

export const uploadPdf = async (file, token) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    headers: getAuthHeaders(token),
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Upload failed");
  }

  return await response.json();
};

export const fetchDatabaseContents = async (token) => {
  const response = await fetch(`${API_BASE_URL}/database`, {
    headers: getAuthHeaders(token),
  });
  if (!response.ok) {
    throw new Error("Failed to fetch database contents");
  }
  return await response.json();
};

export const sendChatMessage = async (prompt, token) => {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: getAuthHeaders(token, {
      "Content-Type": "application/json",
    }),
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to send message");
  }

  return await response.json();
};
