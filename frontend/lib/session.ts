import { cookies } from "next/headers";

import { backendFetch } from "./backend";
import type { AuthResponse, User } from "./types";

export const SESSION_COOKIE = "rf_token";
const MAX_AGE_SECONDS = 60 * 60 * 24;

/** cookies() 를 읽으므로 호출하는 컴포넌트는 <Suspense> 안에 있어야 한다. */
export async function getToken(): Promise<string | undefined> {
  return (await cookies()).get(SESSION_COOKIE)?.value;
}

export async function getCurrentUser(): Promise<User | null> {
  const token = await getToken();
  if (!token) return null;
  try {
    return await backendFetch<User>("/api/auth/me", { token });
  } catch {
    return null;
  }
}

/** Route Handler 전용: 백엔드 인증 결과의 토큰을 httpOnly 쿠키로 저장하고 사용자만 돌려준다. */
export async function startSession({ token, user }: AuthResponse): Promise<Response> {
  (await cookies()).set(SESSION_COOKIE, token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: MAX_AGE_SECONDS,
  });
  return Response.json({ user });
}

export async function endSession(): Promise<void> {
  (await cookies()).delete(SESSION_COOKIE);
}
