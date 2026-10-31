package com.reviewforge.dto;

import java.time.Instant;
import java.util.List;

import com.reviewforge.domain.Analysis;
import com.reviewforge.domain.Analysis.Highlight;

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
			String source) {
	}

	public record AnalysisResponse(
			String id,
			String reviewText,
			double fakeProbability,
			int confidenceScore,
			String label,
			List<String> keywords,
			List<Highlight> highlights,
			boolean saved,
			Instant createdAt) {

		public static AnalysisResponse from(Analysis a) {
			return new AnalysisResponse(a.id(), a.reviewText(), a.fakeProbability(), a.confidenceScore(),
					a.label(), a.keywords(), a.highlights(), a.id() != null, a.createdAt());
		}

	}

}
