package com.reviewforge.service;

import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientResponseException;

import com.reviewforge.dto.AnalysisDtos.AiAnalyzeResult;
import com.reviewforge.exception.ApiException;

/** Flask AI 서버 호출 전용. ML 로직은 Flask 에만 둔다. */
@Component
public class AiClient {

	private final RestClient aiRestClient;

	public AiClient(RestClient aiRestClient) {
		this.aiRestClient = aiRestClient;
	}

	public AiAnalyzeResult analyze(String text) {
		try {
			AiAnalyzeResult result = aiRestClient.post()
					.uri("/analyze")
					.contentType(MediaType.APPLICATION_JSON)
					.body(Map.of("text", text))
					.retrieve()
					.body(AiAnalyzeResult.class);
			if (result == null) {
				throw new ApiException(HttpStatus.BAD_GATEWAY, "AI 서버 응답이 비어 있습니다.");
			}
			return result;
		} catch (ResourceAccessException e) {
			throw new ApiException(HttpStatus.SERVICE_UNAVAILABLE, "AI 서버에 연결할 수 없습니다.");
		} catch (RestClientResponseException e) {
			throw new ApiException(HttpStatus.BAD_GATEWAY, "AI 서버 오류 (" + e.getStatusCode().value() + ")");
		}
	}

	public boolean isHealthy() {
		try {
			aiRestClient.get().uri("/health").retrieve().toBodilessEntity();
			return true;
		} catch (RuntimeException e) {
			return false;
		}
	}

}
