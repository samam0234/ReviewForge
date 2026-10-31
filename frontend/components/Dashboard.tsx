import type { Analysis, Label, User } from "@/lib/types";

const LABELS: Label[] = ["Genuine", "Suspicious", "Fake"];

export default function Dashboard({ user, analyses }: { user: User; analyses: Analysis[] }) {
  const count = analyses.length;
  const avgFake = count ? analyses.reduce((s, a) => s + a.fakeProbability, 0) / count : 0;
  const avgConfidence = count ? analyses.reduce((s, a) => s + a.confidenceScore, 0) / count : 0;

  return (
    <div className="stack">
      <h1>{user.name}님의 분석 기록</h1>
      <dl className="stats card">
        <div>
          <dt>최근 분석</dt>
          <dd>{count}건</dd>
        </div>
        <div>
          <dt>평균 가짜 확률</dt>
          <dd>{Math.round(avgFake * 100)}%</dd>
        </div>
        <div>
          <dt>평균 판정 확신도</dt>
          <dd>{Math.round(avgConfidence)}</dd>
        </div>
        {LABELS.map((label) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{analyses.filter((a) => a.label === label).length}</dd>
          </div>
        ))}
      </dl>

      {count === 0 ? (
        <p className="muted">아직 분석 기록이 없습니다.</p>
      ) : (
        <table className="card table">
          <thead>
            <tr>
              <th>일시</th>
              <th>리뷰</th>
              <th>결과</th>
              <th>가짜 확률</th>
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
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
