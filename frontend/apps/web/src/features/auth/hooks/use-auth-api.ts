"use client";

import { useMutation } from "@tanstack/react-query";

export type LoginInput = { email: string; password: string };

async function postJson<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = (await res.json().catch(() => ({}))) as T & { error?: { code: string } };
  if (!res.ok) {
    throw new Error(data.error?.code ?? "common.unknown");
  }
  return data;
}

export function useLogin() {
  return useMutation({
    mutationFn: (input: LoginInput) => postJson<{ ok: true }>("/api/auth/login", input),
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: (input: {
      email: string;
      password: string;
      display_name: string;
      locale: string;
    }) => postJson<{ user_id: string }>("/api/auth/register", input),
  });
}

export function useLogout() {
  return useMutation({
    mutationFn: async () => {
      await fetch("/api/auth/logout", { method: "POST" });
    },
  });
}
