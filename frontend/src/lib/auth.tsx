"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ApiError,
  api,
  clearAuth,
  getStoredUser,
  getToken,
  setStoredUser,
  setToken,
} from "@/lib/api";
import type { TokenResponse, UserPublic } from "@/lib/types";

interface AuthContextValue {
  user: UserPublic | null;
  loading: boolean;
  isAuthenticated: boolean;
  isAdmin: boolean;
  login: (email: string, password: string) => Promise<UserPublic>;
  register: (payload: {
    username: string;
    email: string;
    password: string;
    full_name: string;
  }) => Promise<UserPublic>;
  logout: () => void;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<UserPublic | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = getStoredUser<UserPublic>();

    if (stored && getToken()) {
      setUser(stored);

      api
        .get<UserPublic>("/auth/me")
        .then((fresh) => {
          setUser(fresh);
          setStoredUser(fresh);
        })
        .catch(() => {
          clearAuth();
          setUser(null);
        })
        .finally(() => setLoading(false));

      return;
    }

    setLoading(false);
  }, []);

  const value = useMemo<AuthContextValue>(() => {
    const applyToken = (result: TokenResponse) => {
      setToken(result.access_token);
      setStoredUser(result.user);
      setUser(result.user);
      return result.user;
    };

    return {
      user,
      loading,
      isAuthenticated: Boolean(user),
      isAdmin: user?.role === "admin",

      login: async (email, password) => {
        const result = await api.post<TokenResponse>("/auth/login", {
          email,
          password,
        });
        return applyToken(result);
      },

      register: async (payload) => {
        const result = await api.post<TokenResponse>("/auth/register", payload);
        return applyToken(result);
      },

      logout: () => {
        clearAuth();
        setUser(null);
        router.push("/login");
      },

      refresh: async () => {
        try {
          const fresh = await api.get<UserPublic>("/auth/me");
          setUser(fresh);
          setStoredUser(fresh);
        } catch (error) {
          if (error instanceof ApiError && error.status === 401) {
            clearAuth();
            setUser(null);
          }
        }
      },
    };
  }, [user, loading, router]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}
