"use client";
import { useState, FormEvent, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { getAccessToken } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const { login, loading, error } = useAuth();
  const [email, setEmail] = useState("demo@reachgtm.com");
  const [password, setPassword] = useState("demo1234");
  const [autoTrying, setAutoTrying] = useState(true);

  // Auto-login with demo credentials
  useEffect(() => {
    if (!autoTrying) return;
    const token = getAccessToken();
    if (token) {
      router.push("/dashboard");
      return;
    }
    login({ email: "demo2@reachgtm.com", password: "demo1234" })
      .then(() => {
        window.location.href = "/dashboard";
      })
      .catch(() => {
        setAutoTrying(false);
      });
  }, [autoTrying, login, router]);

  // Redirect if already logged in
  useEffect(() => {
    const token = getAccessToken();
    if (token) {
      router.push("/dashboard");
    }
  }, [router]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      await login({ email, password });
      window.location.href = "/dashboard";
    } catch {
      // error already set in useAuth
    }
  }

  if (autoTrying) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="spinner mx-auto mb-4" />
          <p className="text-gray-600">Connecting to ReachGTM...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50">
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4 rounded-xl bg-white p-8 shadow">
        <h1 className="text-2xl font-bold text-gray-900">Sign in to ReachGTM</h1>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <div>
          <label className="block text-sm font-medium text-gray-700">Email</label>
          <input
            type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Password</label>
          <input
            type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </div>
        <button
          type="submit" disabled={loading}
          className="w-full rounded-md bg-blue-600 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Signing in..." : "Sign in"}
        </button>
        <p className="text-center text-sm text-gray-600">
          No account? <a href="/register" className="text-blue-600 hover:underline">Create one</a>
        </p>
      </form>
    </main>
  );
}
