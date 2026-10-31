package com.reviewforge.controller;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestAttribute;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.reviewforge.auth.AuthInterceptor;
import com.reviewforge.dto.AnalysisDtos.AnalysisResponse;
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

	@PostMapping("/analyze")
	public AnalysisResponse analyze(@Valid @RequestBody AnalyzeRequest req,
			@RequestAttribute(name = AuthInterceptor.USER_ID, required = false) String userId) {
		return analysisService.analyze(req.text(), userId);
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
