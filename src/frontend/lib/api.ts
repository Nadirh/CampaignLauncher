const API_URL = process.env.API_URL || "http://localhost:8000";

export async function fetchFromApi<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const url = `${API_URL}${path}`;
  const response = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}
