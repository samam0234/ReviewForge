import Link from "next/link";

const GRADIO_URL = process.env.NEXT_PUBLIC_GRADIO_URL ?? "http://localhost:7860";

export default function Home() {
  return (
    <section className="stack hero">
      <h1>리뷰 한 줄로, 진짜인지 가짜인지.</h1>
      <p className="muted">
        ReviewForge 는 리뷰 텍스트의 과장 표현·홍보 문구·반복 패턴을 AI 로 분석해 가짜 확률과 판단 근거를 보여 줍니다.
      </p>
      <div className="row start">
        <Link href="/analyze" className="button">
          리뷰 분석 시작
        </Link>
        <Link href="/dashboard" className="button ghost">
          내 분석 기록
        </Link>
        <a href={GRADIO_URL} target="_blank" rel="noreferrer" className="button ghost">
          모델 데모 (Gradio)
        </a>
      </div>
    </section>
  );
}
