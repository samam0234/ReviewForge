export type Label = "Genuine" | "Suspicious" | "Fake";

export type Highlight = { text: string; reason: string };

export type Analysis = {
  id: string | null;
  reviewText: string;
  fakeProbability: number;
  confidenceScore: number;
  label: Label;
  keywords: string[];
  highlights: Highlight[];
  saved: boolean;
  createdAt: string;
};

export type User = { id: string; email: string; name: string; createdAt: string };

export type AuthResponse = { token: string; user: User };
