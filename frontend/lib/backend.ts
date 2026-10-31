const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8080";

export class BackendError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

type Options = { method?: "GET" | "POST"; body?: unknown; token?: string };

/**
 * Spring Boot 호출 (서버 전용: Route Handler / Server Component 에서만 사용).
 * body 가 FormData 면 multipart 로 그대로 보낸다 (boundary 는 fetch 가 설정).
 */
export async function backendFetch<T>(path: string, { method = "GET", body, token }: Options = {}): Promise<T> {
  const multipart = body instanceof FormData;
  let res: Response;
  try {
    res = await fetch(`${BACKEND_URL}${path}`, {
      method,
      headers: {
        ...(multipart ? {} : { "Content-Type": "application/json" }),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: body === undefined ? undefined : multipart ? body : JSON.stringify(body),
      cache: "no-store",
    });
  } catch {
    throw new BackendError(503, "백엔드 서버에 연결할 수 없습니다.");
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new BackendError(res.status, data.error ?? `요청 실패 (${res.status})`);
  }
  return data as T;
}

export function errorResponse(e: unknown): Response {
  if (e instanceof BackendError) {
    return Response.json({ error: e.message }, { status: e.status });
  }
  if (e instanceof SyntaxError) {
    return Response.json({ error: "요청 본문(JSON)을 읽을 수 없습니다." }, { status: 400 });
  }
  return Response.json({ error: "알 수 없는 오류가 발생했습니다." }, { status: 500 });
}
