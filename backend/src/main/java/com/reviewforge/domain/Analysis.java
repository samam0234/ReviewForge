package com.reviewforge.domain;

import java.time.Instant;
import java.util.List;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

/**
 * 분석 기록. 이미지가 함께 분석되면 {@code fakeProbability} 는 텍스트·이미지 융합 점수이고
 * {@code textFakeProbability} 에 텍스트 단독 점수, {@code image} 에 이미지 결과가 남는다 (원본 이미지는 저장하지 않는다).
 */
@Document("analyses")
public record Analysis(
		@Id String id,
		@Indexed String userId,
		String reviewText,
		double fakeProbability,
		int confidenceScore,
		String label,
		List<String> keywords,
		List<Highlight> highlights,
		Double textFakeProbability,
		ImageResult image,
		Instant createdAt) {

	public record Highlight(String text, String reason) {
	}

	public record ImageResult(
			double fakeProbability,
			int confidenceScore,
			String label,
			List<String> signals,
			String source,
			int width,
			int height) {
	}

}
