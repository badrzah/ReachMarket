"use client";

import { useCallback, useState, useEffect } from "react";
import { authApi } from "@/lib/api";
import { setTokens, clearTokens, getAccessToken } from "@/lib/auth";
import type { LoginRequest, RegisterRequest } from "@/types";

export function useAuth() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initialized, setInitialized] = useState(false);

  // Auto-create demo account on first visit if no token exists
  useEffect(() => {
    if (initialized) return;
    const token = getAccessToken();
    if (token) { setInitialized(true); return; }

    const autoLogin = async () => {
      setLoading(true);
      try {
        // Try to login with demo credentials first
        const tokens = await authApi.login({
          email: "demo@reachgtm.com",
          password: "demo1234",
        });
        setTokens(tokens.access_token, tokens.refresh_token);
      } catch {
        // If login fails, create demo account
        try {
          const tokens = await authApi.register({
            email: "demo@reachgtm.com",
            password: "demo1234",
            company_name: "Demo Company",
          });
          setTokens(tokens.access_token, tokens.refresh_token);
        } catch {
          // Both failed — user needs to sign up manually
        }
      }
      setLoading(false);
      setInitialized(true);
    };
    autoLogin();
  }, [initialized]);

  const login = useCallback(async (body: LoginRequest) => {
    setLoading(true);
    try {
      const tokens = await authApi.login(body);
      setTokens(tokens.access_token, tokens.refresh_token);
      return tokens;
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Login failed");
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (body: RegisterRequest) => {
    setLoading(true);
    setError(null);
    try {
      const tokens = await authApi.register(body);
      setTokens(tokens.access_token, tokens.refresh_token);
      return tokens;
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Registration failed");
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    clearTokens();
    window.location.href = "/login";
  }, []);

  return { login, register, logout, loading, error, initialized };
}
