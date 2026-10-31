package com.reviewforge.service;

import java.time.Instant;
import java.util.List;

import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import com.reviewforge.domain.Analysis;
import com.reviewforge.dto.AnalysisDtos.AiAnalyzeResult;
import com.reviewforge.dto.AnalysisDtos.AnalysisResponse;
import com.reviewforge.exception.ApiException;
import com.reviewforge.repository.AnalysisRepository;

@Service
public class AnalysisService {

	private static final int MAX_LIMIT = 100;

	private final AiClient aiClient;
	private final AnalysisRepository analyses;

	public AnalysisService(AiClient aiClient, AnalysisRepository analyses) {
		this.aiClient = aiClient;
		this.analyses = analyses;
	}

	/** 로그인 사용자({@code userId != null})의 결과만 저장한다. */
	public AnalysisResponse analyze(String text, String userId) {
		String reviewText = text.strip();
		AiAnalyzeResult ai = aiClient.analyze(reviewText);
		Analysis analysis = new Analysis(null, userId, reviewText, ai.fakeProbability(), ai.confidenceScore(),
				ai.label(), ai.keywords(), ai.highlights(), Instant.now());
		return AnalysisResponse.from(userId == null ? analysis : analyses.save(analysis));
	}

	public List<AnalysisResponse> list(String userId, int limit) {
		int size = Math.clamp(limit, 1, MAX_LIMIT);
		return analyses.findByUserIdOrderByCreatedAtDesc(userId, PageRequest.of(0, size)).stream()
				.map(AnalysisResponse::from)
				.toList();
	}

	public AnalysisResponse get(String userId, String id) {
		return analyses.findByIdAndUserId(id, userId)
				.map(AnalysisResponse::from)
				.orElseThrow(() -> ApiException.notFound("분석 기록"));
	}

}
