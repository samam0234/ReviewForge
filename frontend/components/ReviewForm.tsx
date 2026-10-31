"use client";

import { useState } from "react";

import type { Analysis } from "@/lib/types";

import ResultCard from "./ResultCard";

const MAX_LENGTH = 5000;
const MAX_IMAGE_BYTES = 5 * 1024 * 1024;
const IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"];
const SAMPLES = [
  "배송은 3일 걸렸고 포장은 꼼꼼했어요. 사이즈는 평소보다 한 치수 크게 사는 걸 추천합니다.",
  "인생템!!! 무조건 사세요!!! 진짜 최고최고 강추합니다!!!",
];

function imageError(file: File): string | null {
  if (!IMAGE_TYPES.includes(file.type)) return "JPEG, PNG, WEBP 이미지만 지원합니다.";
  if (file.size > MAX_IMAGE_BYTES) return "이미지는 5MB 이하로 올려 주세요.";
  return null;
}

export default function ReviewForm() {
  const [text, setText] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [inputKey, setInputKey] = useState(0);
  const [result, setResult] = useState<Analysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function onImageChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] ?? null;
    const message = file && imageError(file);
    setError(message || null);
    setImage(message ? null : file);
    if (message) setInputKey((k) => k + 1);
  }

  function clearImage() {
    setImage(null);
    setInputKey((k) => k + 1);
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      let init: RequestInit;
      if (image) {
        const form = new FormData();
        form.set("text", text);
        form.set("image", image);
        init = { method: "POST", body: form };
      } else {
        init = { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text }) };
      }
      const res = await fetch("/api/analyze", init);
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
        <div className="row start">
          <label htmlFor="review-image" className="file-label">
            리뷰 사진 (선택 · JPEG/PNG/WEBP, 5MB 이하)
          </label>
          <input
            key={inputKey}
            id="review-image"
            type="file"
            accept={IMAGE_TYPES.join(",")}
            onChange={onImageChange}
          />
          {image && (
            <button type="button" className="ghost" onClick={clearImage}>
              사진 빼기
            </button>
          )}
        </div>
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
