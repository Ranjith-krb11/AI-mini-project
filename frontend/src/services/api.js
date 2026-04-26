const API_BASE_URL = "http://localhost:8000/api";

export const uploadPdf = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Upload failed");
  }

  return await response.json();
};

export const fetchDatabaseContents = async () => {
  const response = await fetch(`${API_BASE_URL}/database`);
  if (!response.ok) {
    throw new Error("Failed to fetch database contents");
  }
  return await response.json();
};

export const sendChatMessage = async (prompt) => {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    throw new Error("Failed to send message");
  }

  return await response.json();
};
