const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ApiResponse<T> {
  data: T;
  pagination?: {
    next_cursor: string | null;
    has_more: boolean;
    limit: number;
  };
}

interface ApiError {
  error: {
    code: string;
    message: string;
  };
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }

  private getGymId(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("gym_id");
  }

  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    const gymId = this.getGymId();

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    if (gymId) {
      headers["X-Gym-ID"] = gymId;
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401) {
        const refreshed = await this.refreshToken();
        if (refreshed) {
          headers["Authorization"] = `Bearer ${this.getToken()}`;
          const retryResponse = await fetch(`${this.baseUrl}${path}`, {
            ...options,
            headers,
          });
          if (retryResponse.ok) {
            if (retryResponse.status === 204) return undefined as T;
            return retryResponse.json();
          }
        }
        if (typeof window !== "undefined") {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          window.location.href = "/login";
        }
      }
      const error: ApiError = await response.json().catch(() => ({
        error: { code: "unknown", message: "An error occurred" },
      }));
      throw new Error(error.error?.message || "Request failed");
    }

    if (response.status === 204) return undefined as T;
    return response.json();
  }

  private async refreshToken(): Promise<boolean> {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) return false;

    try {
      const response = await fetch(`${this.baseUrl}/v1/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) return false;

      const data = await response.json();
      localStorage.setItem("access_token", data.data.access_token);
      if (data.data.refresh_token) {
        localStorage.setItem("refresh_token", data.data.refresh_token);
      }
      return true;
    } catch {
      return false;
    }
  }

  async get<T>(path: string): Promise<T> {
    return this.request<T>(path);
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async put<T>(path: string, body: unknown): Promise<T> {
    return this.request<T>(path, {
      method: "PUT",
      body: JSON.stringify(body),
    });
  }

  async patch<T>(path: string, body: unknown): Promise<T> {
    return this.request<T>(path, {
      method: "PATCH",
      body: JSON.stringify(body),
    });
  }

  async delete(path: string): Promise<void> {
    await this.request(path, { method: "DELETE" });
  }
}

export const api = new ApiClient(API_BASE);
export type { ApiResponse, ApiError };
