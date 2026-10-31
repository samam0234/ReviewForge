"use client";

import { useState } from "react";

import type { Analysis } from "@/lib/types";

import ResultCard from "./ResultCard";

const MAX_LENGTH = 5000;
const SAMPLES = [
  "배송은 3일 걸렸고 포장은 꼼꼼했어요. 사이즈는 평소보다 한 치수 크게 사는 걸 추천합니다.",
  "인생템!!! 무조건 사세요!!! 진짜 최고최고 강추합니다!!!",
];

export default function ReviewForm() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<Analysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "분석에 실패했습니다.");
      setResult(data);
    } catch (err) {
      setResult(null);
      setError(err instanceof Error ? err.message : "분석에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="stack">
      <form onSubmit={onSubmit} className="card stack">
        <label htmlFor="review">리뷰 텍스트</label>
        <textarea
          id="review"
          rows={6}
          maxLength={MAX_LENGTH}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="분석할 상품/서비스 리뷰를 붙여넣으세요"
        />
        <div className="row">
          <span className="muted small">
            {text.length} / {MAX_LENGTH}
          </span>
          <div className="row">
            {SAMPLES.map((s, i) => (
              <button key={i} type="button" className="ghost" onClick={() => setText(s)}>
                예시 {i + 1}
              </button>
            ))}
            <button type="submit" disabled={loading || !text.trim()}>
              {loading ? "분석 중…" : "분석하기"}
            </button>
          </div>
        </div>
        {error && <p className="error">{error}</p>}
      </form>
      {result && <ResultCard analysis={result} />}
    </div>
  );
}
