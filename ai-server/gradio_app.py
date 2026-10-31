"""Gradio MVP 데모.  실행: ai-server 디렉터리에서 `python gradio_app.py` → http://localhost:7860"""
import os

import gradio as gr
from dotenv import load_dotenv

from app.services import model_service

load_dotenv()

EXAMPLES = [
    ["배송은 3일 걸렸고 포장은 꼼꼼했어요. 사이즈는 평소보다 한 치수 크게 사는 걸 추천합니다."],
    ["인생템!!! 무조건 사세요!!! 진짜 최고최고 강추합니다!!!"],
    ["쿠폰 코드 REVIEW50 입력하면 50% 할인!! 지금 바로 구매하세요"],
    ["화면 밝기는 괜찮은데 배터리가 생각보다 빨리 닳네요."],
]


def run(text: str):
    try:
        result = model_service.analyze(text)
    except ValueError as exc:
        raise gr.Error(str(exc))
    spans = {h["text"]: h["reason"] for h in result["highlights"] if h["text"]}
    highlighted, rest = [], text
    for phrase, reason in sorted(spans.items(), key=lambda kv: text.lower().find(kv[0].lower())):
        idx = rest.lower().find(phrase.lower())
        if idx < 0:
            continue
        highlighted.append((rest[:idx], None))
        highlighted.append((rest[idx:idx + len(phrase)], reason))
        rest = rest[idx + len(phrase):]
    highlighted.append((rest, None))

    p = result["fakeProbability"]
    summary = (
        f"### {result['label']}\n"
        f"- 가짜 확률: **{p * 100:.1f}%**\n"
        f"- 판정 확신도: **{result['confidenceScore']}**\n"
        f"- 분석 방식: `{result['source']}`"
    )
    return summary, {"Fake": p, "Genuine": 1 - p}, highlighted, result


with gr.Blocks(title="ReviewForge Demo") as demo:
    gr.Markdown("# ReviewForge — 가짜 리뷰 탐지 데모")
    with gr.Row():
        with gr.Column():
            text_in = gr.Textbox(label="리뷰 텍스트", lines=6, placeholder="분석할 리뷰를 입력하세요")
            button = gr.Button("분석", variant="primary")
            gr.Examples(EXAMPLES, inputs=text_in)
        with gr.Column():
            summary_out = gr.Markdown()
            prob_out = gr.Label(label="판정 확률")
            highlight_out = gr.HighlightedText(label="근거 하이라이트")
            json_out = gr.JSON(label="원본 응답")
    button.click(run, inputs=text_in, outputs=[summary_out, prob_out, highlight_out, json_out])


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.getenv("GRADIO_PORT", "7860")))
