"""리뷰 이미지 규칙 기반 신호 (메타데이터 + 간단한 화면 통계). 이미지 하이브리드의 규칙 부분."""
from __future__ import annotations

from PIL import Image

EDITOR_KEYWORDS = (
    "photoshop", "lightroom", "illustrator", "gimp", "snapseed", "picsart", "meitu", "canva", "facetune",
)
EXIF_MAKE, EXIF_MODEL, EXIF_SOFTWARE = 0x010F, 0x0110, 0x0131
MIN_SIDE = 400
BORDER_SAMPLE = 64
BORDER_TOLERANCE = 16
UNIFORM_BORDER_RATIO = 0.9


def border_uniform_ratio(image: Image.Image) -> float:
    """가장자리 픽셀 중 가장자리 중앙값 색과 거의 같은 비율. 스튜디오 단색 배경 연출 사진일수록 1 에 가깝다."""
    small = image.convert("RGB").resize((BORDER_SAMPLE, BORDER_SAMPLE))
    n = BORDER_SAMPLE - 1
    coords = {(x, y) for x in range(BORDER_SAMPLE) for y in (0, n)} | {(x, y) for x in (0, n) for y in range(BORDER_SAMPLE)}
    pixels = [small.getpixel(c) for c in coords]
    median = tuple(sorted(p[ch] for p in pixels)[len(pixels) // 2] for ch in range(3))
    close = sum(1 for p in pixels if max(abs(p[ch] - median[ch]) for ch in range(3)) <= BORDER_TOLERANCE)
    return close / len(pixels)


def image_signals(image: Image.Image) -> dict:
    hits: list[dict] = []
    exif = image.getexif()

    software = str(exif.get(EXIF_SOFTWARE, "")).strip()
    if any(k in software.lower() for k in EDITOR_KEYWORDS):
        hits.append({"reason": f"편집 프로그램 흔적 ({software})", "weight": 0.35})

    if not exif.get(EXIF_MAKE) and not exif.get(EXIF_MODEL):
        hits.append({"reason": "촬영 기기 정보(EXIF) 없음 — 캡처·다운로드 이미지 가능성", "weight": 0.1})

    if min(image.size) < MIN_SIDE:
        hits.append({"reason": f"저해상도 이미지 (짧은 변 {min(image.size)}px)", "weight": 0.15})

    if border_uniform_ratio(image) >= UNIFORM_BORDER_RATIO:
        hits.append({"reason": "단색 배경 — 판매자 제공 연출 사진 가능성", "weight": 0.3})

    return {"score": min(1.0, sum(h["weight"] for h in hits)), "hits": hits}
