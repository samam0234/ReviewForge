package com.reviewforge.config;

import java.time.Duration;
import java.util.List;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties("reviewforge")
public record AppProperties(
		String aiServerUrl,
		Duration aiTimeout,
		String jwtSecret,
		Duration jwtExpiration,
		List<String> corsOrigins) {
}
