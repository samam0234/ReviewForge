import { backendFetch, errorResponse } from "@/lib/backend";
import { getToken } from "@/lib/session";
import type { Analysis } from "@/lib/types";

export async function POST(request: Request) {
  try {
    const { text } = await request.json();
    const analysis = await backendFetch<Analysis>("/api/analyze", {
      method: "POST",
      body: { text },
      token: await getToken(),
    });
    return Response.json(analysis);
  } catch (e) {
    return errorResponse(e);
  }
}
