package com.reviewforge.dto;

import java.time.Instant;
import java.util.List;
import java.util.Map;

import com.reviewforge.domain.Analysis;
import com.reviewforge.domain.Analysis.Highlight;
import com.reviewforge.domain.Analysis.ImageResult;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public final class AnalysisDtos {

	private AnalysisDtos() {
	}

	public record AnalyzeRequest(@NotBlank @Size(max = 5000) String text) {
	}

	/** Flask {@code POST /analyze} 응답. */
	public record AiAnalyzeResult(
			double fakeProbability,
			int confidenceScore,
			String label,
			List<String> keywords,
			List<Highlight> highlights,
			String source,
			Double textFakeProbability,
			ImageResult image) {
	}

	public record AnalysisResponse(
			String id,
			String reviewText,
			double fakeProbability,
			int confidenceScore,
			String label,
			List<String> keywords,
			List<Highlight> highlights,
			Double textFakeProbability,
			ImageResult image,
			boolean saved,
			Instant createdAt) {

		public static AnalysisResponse from(Analysis a) {
			return new AnalysisResponse(a.id(), a.reviewText(), a.fakeProbability(), a.confidenceScore(),
					a.label(), a.keywords(), a.highlights(), a.textFakeProbability(), a.image(), a.id() != null,
					a.createdAt());
		}

	}

	/** 라벨별 집계 한 줄 (MongoDB {@code $group} 결과). */
	public record LabelBucket(String label, long count, double sumFakeProbability, double sumConfidenceScore,
			long withImage) {
	}

	/** 사용자 전체 기록 기준 통계. 평균은 라벨별 합계를 더한 뒤 전체 건수로 나눈 가중 평균이다. */
	public record AnalysisStats(
			long total,
			double avgFakeProbability,
			double avgConfidenceScore,
			Map<String, Long> labelCounts,
			long withImage) {

		public static final List<String> LABELS = List.of("Genuine", "Suspicious", "Fake");

		public static AnalysisStats from(List<LabelBucket> buckets) {
			long total = buckets.stream().mapToLong(LabelBucket::count).sum();
			double sumFake = buckets.stream().mapToDouble(LabelBucket::sumFakeProbability).sum();
			double sumConfidence = buckets.stream().mapToDouble(LabelBucket::sumConfidenceScore).sum();
			Map<String, Long> counts = new java.util.LinkedHashMap<>();
			LABELS.forEach(label -> counts.put(label, 0L));
			buckets.forEach(b -> counts.merge(b.label(), b.count(), Long::sum));
			return new AnalysisStats(
					total,
					total == 0 ? 0 : round(sumFake / total, 4),
					total == 0 ? 0 : round(sumConfidence / total, 1),
					counts,
					buckets.stream().mapToLong(LabelBucket::withImage).sum());
		}

		private static double round(double value, int scale) {
			return java.math.BigDecimal.valueOf(value).setScale(scale, java.math.RoundingMode.HALF_UP).doubleValue();
		}

	}

}
