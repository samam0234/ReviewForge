import Link from "next/link";

import { getCurrentUser } from "@/lib/session";

import LogoutButton from "./LogoutButton";

/** 세션 쿠키를 읽으므로 반드시 <Suspense> 안에서 렌더링한다. */
export default async function UserMenu() {
  const user = await getCurrentUser();
  if (!user) {
    return <Link href="/login">로그인</Link>;
  }
  return (
    <span className="row">
      <span className="muted">{user.name}님</span>
      <LogoutButton />
    </span>
  );
}
