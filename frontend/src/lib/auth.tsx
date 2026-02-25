"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

interface User {
  user_id: string;
  email: string;
  role: string;
  gym_id: string | null;
  first_name: string;
  last_name: string;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setGym: (gymId: string) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
  });

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      api
        .get<{ data: User }>("/v1/auth/me")
        .then((res) => {
          setState({
            user: res.data,
            isLoading: false,
            isAuthenticated: true,
          });
        })
        .catch(() => {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          setState({ user: null, isLoading: false, isAuthenticated: false });
        });
    } else {
      setState({ user: null, isLoading: false, isAuthenticated: false });
    }
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await api.post<{
        data: {
          access_token: string;
          refresh_token: string;
          user: User;
        };
      }>("/v1/auth/login", { email, password });

      localStorage.setItem("access_token", res.data.access_token);
      localStorage.setItem("refresh_token", res.data.refresh_token);
      if (res.data.user.gym_id) {
        localStorage.setItem("gym_id", res.data.user.gym_id);
      }

      setState({
        user: res.data.user,
        isLoading: false,
        isAuthenticated: true,
      });

      router.push("/dashboard");
    },
    [router]
  );

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("gym_id");
    setState({ user: null, isLoading: false, isAuthenticated: false });
    router.push("/login");
  }, [router]);

  const setGym = useCallback((gymId: string) => {
    localStorage.setItem("gym_id", gymId);
  }, []);

  return (
    <AuthContext.Provider
      value={{ ...state, login, logout, setGym }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
