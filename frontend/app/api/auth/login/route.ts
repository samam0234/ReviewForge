import { backendFetch, errorResponse } from "@/lib/backend";
import { startSession } from "@/lib/session";
import type { AuthResponse } from "@/lib/types";

export async function POST(request: Request) {
  try {
    const auth = await backendFetch<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: await request.json(),
    });
    return startSession(request, auth);
  } catch (e) {
    return errorResponse(e);
  }
}
