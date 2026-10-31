import type { Analysis, Highlight } from "@/lib/types";

type Segment = { text: string; reason?: string };

function splitByHighlights(text: string, highlights: Highlight[]): Segment[] {
  const phrases = highlights.filter((h) => h.text.trim());
  const segments: Segment[] = [];
  const lower = text.toLowerCase();
  let cursor = 0;
  while (cursor < text.length) {
    let best: { start: number; h: Highlight } | null = null;
    for (const h of phrases) {
      const start = lower.indexOf(h.text.toLowerCase(), cursor);
      if (start >= 0 && (!best || start < best.start)) best = { start, h };
    }
    if (!best) break;
    if (best.start > cursor) segments.push({ text: text.slice(cursor, best.start) });
    const end = best.start + best.h.text.length;
    segments.push({ text: text.slice(best.start, end), reason: best.h.reason });
    cursor = end;
  }
  if (cursor < text.length) segments.push({ text: text.slice(cursor) });
  return segments;
}

const LABEL_TEXT = { Genuine: "진짜 리뷰로 보여요", Suspicious: "의심스러운 리뷰", Fake: "가짜일 가능성이 높아요" };

export default function ResultCard({ analysis }: { analysis: Analysis }) {
  const percent = Math.round(analysis.fakeProbability * 100);
  const reasons = analysis.highlights.filter((h) => !h.text.trim());
  const image = analysis.image;
  return (
    <section className={`card result result-${analysis.label.toLowerCase()}`}>
      <header className="result-head">
        <span className="badge">{analysis.label}</span>
        <strong>{LABEL_TEXT[analysis.label]}</strong>
      </header>

      <div className="meter" aria-label={`가짜 확률 ${percent}%`}>
        <div className="meter-fill" style={{ width: `${percent}%` }} />
      </div>
      <dl className="stats">
        <div>
          <dt>가짜 확률</dt>
          <dd>{percent}%</dd>
        </div>
        <div>
          <dt>판정 확신도</dt>
          <dd>{analysis.confidenceScore}</dd>
        </div>
        {image && analysis.textFakeProbability != null && (
          <>
            <div>
              <dt>텍스트</dt>
              <dd>{Math.round(analysis.textFakeProbability * 100)}%</dd>
            </div>
            <div>
              <dt>사진</dt>
              <dd>{Math.round(image.fakeProbability * 100)}%</dd>
            </div>
          </>
        )}
      </dl>

      <p className="review-text">
        {splitByHighlights(analysis.reviewText, analysis.highlights).map((s, i) =>
          s.reason ? (
            <mark key={i} title={s.reason}>
              {s.text}
            </mark>
          ) : (
            <span key={i}>{s.text}</span>
          ),
        )}
      </p>

      {analysis.keywords.length > 0 && (
        <ul className="chips">
          {analysis.keywords.map((k) => (
            <li key={k}>{k}</li>
          ))}
        </ul>
      )}
      {reasons.map((r) => (
        <p key={r.reason} className="muted">
          · {r.reason}
        </p>
      ))}
      {image && (
        <div className="image-result">
          <p className="small">
            <strong>사진 분석</strong>{" "}
            <span className={`badge badge-${image.label.toLowerCase()}`}>{image.label}</span>{" "}
            <span className="muted">
              {image.width}×{image.height} ·{" "}
              {image.source === "rules" ? "메타데이터 규칙 (EfficientNet-B3 미학습)" : "EfficientNet-B3 + 규칙"}
            </span>
          </p>
          {image.signals.length === 0 ? (
            <p className="muted small">· 특이 신호 없음</p>
          ) : (
            image.signals.map((s) => (
              <p key={s} className="muted small">
                · {s}
              </p>
            ))
          )}
          <p className="muted small">사진은 텍스트보다 의심도를 높일 때만 반영됩니다.</p>
        </div>
      )}
      <p className="muted small">{analysis.saved ? "분석 기록에 저장되었습니다." : "로그인하면 분석 기록이 저장됩니다."}</p>
    </section>
  );
}
