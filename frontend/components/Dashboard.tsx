import type { Analysis, AnalysisStats, Label, User } from "@/lib/types";

const LABELS: Label[] = ["Genuine", "Suspicious", "Fake"];

/** 통계는 백엔드가 전체 기록 기준으로 집계한 값이고, 표는 최근 기록만 보여 준다. */
export default function Dashboard({
  user,
  analyses,
  stats,
}: {
  user: User;
  analyses: Analysis[];
  stats: AnalysisStats;
}) {
  return (
    <div className="stack">
      <h1>{user.name}님의 분석 기록</h1>
      <dl className="stats card">
        <div>
          <dt>전체 분석</dt>
          <dd>{stats.total}건</dd>
        </div>
        <div>
          <dt>평균 가짜 확률</dt>
          <dd>{Math.round(stats.avgFakeProbability * 100)}%</dd>
        </div>
        <div>
          <dt>평균 판정 확신도</dt>
          <dd>{Math.round(stats.avgConfidenceScore)}</dd>
        </div>
        {LABELS.map((label) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{stats.labelCounts[label] ?? 0}</dd>
          </div>
        ))}
        <div>
          <dt>사진 포함</dt>
          <dd>{stats.withImage}</dd>
        </div>
      </dl>

      {analyses.length === 0 ? (
        <p className="muted">아직 분석 기록이 없습니다.</p>
      ) : (
        <>
          <p className="muted small">최근 {analyses.length}건</p>
          <table className="card table">
            <thead>
              <tr>
                <th>일시</th>
                <th>리뷰</th>
                <th>결과</th>
                <th>가짜 확률</th>
                <th>사진</th>
              </tr>
            </thead>
            <tbody>
              {analyses.map((a) => (
                <tr key={a.id}>
                  <td className="nowrap">{new Date(a.createdAt).toLocaleString("ko-KR")}</td>
                  <td className="ellipsis">{a.reviewText}</td>
                  <td>
                    <span className={`badge badge-${a.label.toLowerCase()}`}>{a.label}</span>
                  </td>
                  <td>{Math.round(a.fakeProbability * 100)}%</td>
                  <td>{a.image ? `${Math.round(a.image.fakeProbability * 100)}%` : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
