const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function getCurrencies() {
  const response = await fetch(`${API_BASE_URL}/currencies`);

  if (!response.ok) {
    let message = `HTTP error ${response.status}`;

    try {
      const body = await response.json();
      if (body?.detail) message = body.detail;
    } catch (_) {}

    throw new Error(message);
  }

  return await response.json();
}

export async function convert(payload) {
  const response = await fetch(`${API_BASE_URL}/convert`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let message = `HTTP error ${response.status}`;

    try {
      const body = await response.json();
      if (body?.detail) {
        message = body.detail;
      }
    } catch (_) {}

    throw new Error(message);
  }

  return await response.json();
}
