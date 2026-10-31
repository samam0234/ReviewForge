package com.reviewforge.service;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.time.Instant;
import java.util.List;
import java.util.Set;

import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import com.reviewforge.domain.Analysis;
import com.reviewforge.dto.AnalysisDtos.AiAnalyzeResult;
import com.reviewforge.dto.AnalysisDtos.AnalysisResponse;
import com.reviewforge.dto.AnalysisDtos.AnalysisStats;
import com.reviewforge.exception.ApiException;
import com.reviewforge.repository.AnalysisRepository;
import com.reviewforge.service.AiClient.ImageUpload;

@Service
public class AnalysisService {

	private static final int MAX_LIMIT = 100;
	private static final int MAX_TEXT_LENGTH = 5000;
	private static final long MAX_IMAGE_BYTES = 5L * 1024 * 1024;
	private static final Set<String> IMAGE_TYPES = Set.of("image/jpeg", "image/png", "image/webp");

	private final AiClient aiClient;
	private final AnalysisRepository analyses;

	public AnalysisService(AiClient aiClient, AnalysisRepository analyses) {
		this.aiClient = aiClient;
		this.analyses = analyses;
	}

	public AnalysisResponse analyze(String text, String userId) {
		return analyze(text, null, userId);
	}

	/** 로그인 사용자({@code userId != null})의 결과만 저장한다. 이미지는 선택이며 원본은 저장하지 않는다. */
	public AnalysisResponse analyze(String text, MultipartFile image, String userId) {
		String reviewText = validateText(text);
		AiAnalyzeResult ai = aiClient.analyze(reviewText, toUpload(image));
		Analysis analysis = new Analysis(null, userId, reviewText, ai.fakeProbability(), ai.confidenceScore(),
				ai.label(), ai.keywords(), ai.highlights(), ai.textFakeProbability(), ai.image(), Instant.now());
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

	public AnalysisStats stats(String userId) {
		return AnalysisStats.from(analyses.labelBuckets(userId));
	}

	/** JSON 경로는 Bean Validation 을 먼저 거치지만, multipart 경로도 같은 규칙을 적용하기 위해 여기서 한 번 더 검사한다. */
	private static String validateText(String text) {
		String stripped = text == null ? "" : text.strip();
		if (stripped.isEmpty()) {
			throw new ApiException(HttpStatus.BAD_REQUEST, "text: 리뷰 텍스트가 비어 있습니다.");
		}
		if (stripped.length() > MAX_TEXT_LENGTH) {
			throw new ApiException(HttpStatus.BAD_REQUEST, "text: 리뷰는 " + MAX_TEXT_LENGTH + "자 이하로 입력해 주세요.");
		}
		return stripped;
	}

	private static ImageUpload toUpload(MultipartFile image) {
		if (image == null || image.isEmpty()) {
			return null;
		}
		if (image.getSize() > MAX_IMAGE_BYTES) {
			throw new ApiException(HttpStatus.CONTENT_TOO_LARGE, "이미지는 5MB 이하로 올려 주세요.");
		}
		String type = image.getContentType();
		if (type == null || !IMAGE_TYPES.contains(type)) {
			throw new ApiException(HttpStatus.UNSUPPORTED_MEDIA_TYPE, "JPEG, PNG, WEBP 이미지만 지원합니다.");
		}
		String filename = image.getOriginalFilename() == null ? "image" : image.getOriginalFilename();
		try {
			return new ImageUpload(image.getBytes(), filename, MediaType.parseMediaType(type));
		} catch (IOException e) {
			throw new UncheckedIOException(e);
		}
	}

}
