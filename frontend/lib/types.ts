export type Label = "Genuine" | "Suspicious" | "Fake";

export type Highlight = { text: string; reason: string };

export type ImageResult = {
  fakeProbability: number;
  confidenceScore: number;
  label: Label;
  signals: string[];
  source: string;
  width: number;
  height: number;
};

export type Analysis = {
  id: string | null;
  reviewText: string;
  /** 이미지가 있으면 텍스트·이미지 융합 점수, 없으면 텍스트 점수 */
  fakeProbability: number;
  confidenceScore: number;
  label: Label;
  keywords: string[];
  highlights: Highlight[];
  /** 텍스트 단독 점수 (이 필드가 생기기 전 기록은 null) */
  textFakeProbability: number | null;
  image: ImageResult | null;
  saved: boolean;
  createdAt: string;
};

export type AnalysisStats = {
  total: number;
  avgFakeProbability: number;
  avgConfidenceScore: number;
  labelCounts: Record<Label, number>;
  withImage: number;
};

export type User = { id: string; email: string; name: string; createdAt: string };

export type AuthResponse = { token: string; user: User };
