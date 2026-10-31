import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

import UserMenu from "@/components/UserMenu";

import "./globals.css";

export const metadata: Metadata = {
  title: "ReviewForge — AI 가짜 리뷰 탐지",
  description: "리뷰 한 줄로 진짜인지 가짜인지 바로 판단하고 기록하세요.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="ko">
      <body>
        <header className="site-header">
          <nav className="container row">
            <Link href="/" className="brand">
              ReviewForge
            </Link>
            <span className="row">
              <Link href="/analyze">분석하기</Link>
              <Link href="/dashboard">대시보드</Link>
              <Suspense fallback={<span className="muted">…</span>}>
                <UserMenu />
              </Suspense>
            </span>
          </nav>
        </header>
        <main className="container">{children}</main>
      </body>
    </html>
  );
}
