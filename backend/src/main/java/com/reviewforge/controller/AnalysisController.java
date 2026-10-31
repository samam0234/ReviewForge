package com.reviewforge.controller;

import java.util.List;

import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestAttribute;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.reviewforge.auth.AuthInterceptor;
import com.reviewforge.dto.AnalysisDtos.AnalysisResponse;
import com.reviewforge.dto.AnalysisDtos.AnalysisStats;
import com.reviewforge.dto.AnalysisDtos.AnalyzeRequest;
import com.reviewforge.exception.ApiException;
import com.reviewforge.service.AnalysisService;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api")
public class AnalysisController {

	private final AnalysisService analysisService;

	public AnalysisController(AnalysisService analysisService) {
		this.analysisService = analysisService;
	}

	@PostMapping(value = "/analyze", consumes = MediaType.APPLICATION_JSON_VALUE)
	public AnalysisResponse analyze(@Valid @RequestBody AnalyzeRequest req,
			@RequestAttribute(name = AuthInterceptor.USER_ID, required = false) String userId) {
		return analysisService.analyze(req.text(), userId);
	}

	/** 리뷰 텍스트 + 선택 리뷰 사진. 텍스트 검증은 서비스에서 JSON 경로와 같은 규칙으로 한다. */
	@PostMapping(value = "/analyze", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
	public AnalysisResponse analyzeWithImage(@RequestParam(required = false) String text,
			@RequestPart(required = false) MultipartFile image,
			@RequestAttribute(name = AuthInterceptor.USER_ID, required = false) String userId) {
		return analysisService.analyze(text, image, userId);
	}

	@GetMapping("/analyses/stats")
	public AnalysisStats stats(@RequestAttribute(name = AuthInterceptor.USER_ID, required = false) String userId) {
		return analysisService.stats(requireUser(userId));
	}

	@GetMapping("/analyses")
	public List<AnalysisResponse> list(@RequestParam(defaultValue = "20") int limit,
			@RequestAttribute(name = AuthInterceptor.USER_ID, required = false) String userId) {
		return analysisService.list(requireUser(userId), limit);
	}

	@GetMapping("/analyses/{id}")
	public AnalysisResponse get(@PathVariable String id,
			@RequestAttribute(name = AuthInterceptor.USER_ID, required = false) String userId) {
		return analysisService.get(requireUser(userId), id);
	}

	private static String requireUser(String userId) {
		if (userId == null) {
			throw ApiException.unauthorized();
		}
		return userId;
	}

}
