"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

type Mode = "login" | "register";

export default function AuthForm() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("login");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const body = Object.fromEntries(new FormData(e.currentTarget));
    try {
      const res = await fetch(`/api/auth/${mode}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "요청에 실패했습니다.");
      router.push("/dashboard");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "요청에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="card stack narrow">
      <div className="tabs">
        <button type="button" className={mode === "login" ? "" : "ghost"} onClick={() => setMode("login")}>
          로그인
        </button>
        <button type="button" className={mode === "register" ? "" : "ghost"} onClick={() => setMode("register")}>
          회원가입
        </button>
      </div>
      <label>
        이메일
        <input name="email" type="email" required autoComplete="email" />
      </label>
      {mode === "register" && (
        <label>
          이름
          <input name="name" required maxLength={30} autoComplete="name" />
        </label>
      )}
      <label>
        비밀번호
        <input
          name="password"
          type="password"
          required
          minLength={mode === "register" ? 8 : undefined}
          autoComplete={mode === "register" ? "new-password" : "current-password"}
        />
      </label>
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? "처리 중…" : mode === "login" ? "로그인" : "가입하기"}
      </button>
    </form>
  );
}
