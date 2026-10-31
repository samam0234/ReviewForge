package com.reviewforge.domain;

import java.time.Instant;
import java.util.List;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

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
		Instant createdAt) {

	public record Highlight(String text, String reason) {
	}

}
