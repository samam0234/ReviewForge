import { backendFetch, errorResponse } from "@/lib/backend";
import { getToken } from "@/lib/session";
import type { Analysis } from "@/lib/types";

/** JSON `{ text }` 또는 multipart `text` + 선택 `image` 를 Spring Boot 로 중계한다. 검증은 백엔드가 한다. */
export async function POST(request: Request) {
  try {
    const multipart = request.headers.get("content-type")?.startsWith("multipart/form-data");
    const body = multipart ? toBackendForm(await request.formData()) : { text: (await request.json()).text };
    const analysis = await backendFetch<Analysis>("/api/analyze", {
      method: "POST",
      body,
      token: await getToken(),
    });
    return Response.json(analysis);
  } catch (e) {
    return errorResponse(e);
  }
}

function toBackendForm(incoming: FormData): FormData {
  const form = new FormData();
  form.set("text", String(incoming.get("text") ?? ""));
  const image = incoming.get("image");
  if (image instanceof File && image.size > 0) {
    form.set("image", image, image.name);
  }
  return form;
}
