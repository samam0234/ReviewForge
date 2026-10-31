package com.reviewforge.service;

import java.nio.charset.StandardCharsets;
import java.util.Map;

import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientResponseException;

import com.reviewforge.dto.AnalysisDtos.AiAnalyzeResult;
import com.reviewforge.exception.ApiException;

import tools.jackson.core.JacksonException;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** Flask AI 서버 호출 전용. ML 로직은 Flask 에만 둔다. */
@Component
public class AiClient {

	/** 검증을 마친 업로드 이미지. 원본은 Flask 로 넘기기만 하고 저장하지 않는다. */
	public record ImageUpload(byte[] bytes, String filename, MediaType contentType) {
	}

	private static final JsonMapper JSON = JsonMapper.builder().build();

	private final RestClient aiRestClient;

	public AiClient(RestClient aiRestClient) {
		this.aiRestClient = aiRestClient;
	}

	public AiAnalyzeResult analyze(String text) {
		return analyze(text, null);
	}

	public AiAnalyzeResult analyze(String text, ImageUpload image) {
		try {
			RestClient.RequestBodySpec request = aiRestClient.post().uri("/analyze");
			if (image == null) {
				request.contentType(MediaType.APPLICATION_JSON).body(Map.of("text", text));
			} else {
				request.contentType(MediaType.MULTIPART_FORM_DATA).body(multipart(text, image));
			}
			AiAnalyzeResult result = request.retrieve().body(AiAnalyzeResult.class);
			if (result == null) {
				throw new ApiException(HttpStatus.BAD_GATEWAY, "AI 서버 응답이 비어 있습니다.");
			}
			return result;
		} catch (ResourceAccessException e) {
			throw new ApiException(HttpStatus.SERVICE_UNAVAILABLE, "AI 서버에 연결할 수 없습니다.");
		} catch (RestClientResponseException e) {
			throw translate(e);
		}
	}

	/**
	 * FormHttpMessageConverter 가 직렬화하는 multipart 본문.
	 * MultipartBodyBuilder 는 WebClient 용이라 Reactive Streams 가 없는 서블릿 환경에서 NoClassDefFoundError 가 난다.
	 */
	static MultiValueMap<String, Object> multipart(String text, ImageUpload image) {
		HttpHeaders imageHeaders = new HttpHeaders();
		imageHeaders.setContentType(image.contentType());
		imageHeaders.setContentDisposition(
				ContentDisposition.formData().name("image").filename(image.filename(), StandardCharsets.UTF_8).build());
		MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
		body.add("text", text);
		body.add("image", new HttpEntity<>(new ByteArrayResource(image.bytes()), imageHeaders));
		return body;
	}

	/** Flask 의 입력 오류(400·413)는 사용자 메시지를 그대로 전달하고, 그 외는 502 로 감싼다. */
	static ApiException translate(RestClientResponseException e) {
		int status = e.getStatusCode().value();
		if (status == 400 || status == 413) {
			String message = errorMessage(e);
			if (message != null) {
				return new ApiException(HttpStatus.valueOf(status), message);
			}
		}
		return new ApiException(HttpStatus.BAD_GATEWAY, "AI 서버 오류 (" + status + ")");
	}

	private static String errorMessage(RestClientResponseException e) {
		try {
			JsonNode error = JSON.readTree(e.getResponseBodyAsString(StandardCharsets.UTF_8)).path("error");
			return error.isString() ? error.asString() : null;
		} catch (JacksonException ignored) {
			return null;
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
