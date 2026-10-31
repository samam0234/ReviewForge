import { redirect } from "next/navigation";
import { Suspense } from "react";

import Dashboard from "@/components/Dashboard";
import { backendFetch } from "@/lib/backend";
import { getCurrentUser, getToken } from "@/lib/session";
import type { Analysis, AnalysisStats } from "@/lib/types";

export default function DashboardPage() {
  return (
    <Suspense fallback={<p className="muted">분석 기록을 불러오는 중…</p>}>
      <DashboardContent />
    </Suspense>
  );
}

async function DashboardContent() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");
  const token = await getToken();
  const [analyses, stats] = await Promise.all([
    backendFetch<Analysis[]>("/api/analyses?limit=20", { token }),
    backendFetch<AnalysisStats>("/api/analyses/stats", { token }),
  ]);
  return <Dashboard user={user} analyses={analyses} stats={stats} />;
}
