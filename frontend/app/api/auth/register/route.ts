import { backendFetch, errorResponse } from "@/lib/backend";
import { startSession } from "@/lib/session";
import type { AuthResponse } from "@/lib/types";

export async function POST(request: Request) {
  try {
    const auth = await backendFetch<AuthResponse>("/api/auth/register", {
      method: "POST",
      body: await request.json(),
    });
    return startSession(auth);
  } catch (e) {
    return errorResponse(e);
  }
}
