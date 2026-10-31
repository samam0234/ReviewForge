package com.reviewforge.controller;

import java.util.Map;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import com.reviewforge.service.AiClient;

@RestController
public class HealthController {

	private final AiClient aiClient;

	public HealthController(AiClient aiClient) {
		this.aiClient = aiClient;
	}

	@GetMapping("/api/health")
	public Map<String, Object> health() {
		return Map.of("status", "ok", "aiServer", aiClient.isHealthy() ? "up" : "down");
	}

}
