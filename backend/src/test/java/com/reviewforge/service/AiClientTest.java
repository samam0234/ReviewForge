package com.reviewforge.service;

import static org.assertj.core.api.Assertions.assertThat;

import java.nio.charset.StandardCharsets;

import org.junit.jupiter.api.Test;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;

import com.reviewforge.exception.ApiException;

class AiClientTest {

	private static HttpHeaders json() {
		HttpHeaders headers = new HttpHeaders();
		headers.setContentType(MediaType.APPLICATION_JSON);
		return headers;
	}

	@Test
	void flaskInputErrorMessageIsPassedThrough() {
		var e = HttpClientErrorException.create(HttpStatus.BAD_REQUEST, "Bad Request", json(),
				"{\"error\":\"이미지 파일을 읽을 수 없습니다.\"}".getBytes(StandardCharsets.UTF_8), StandardCharsets.UTF_8);

		ApiException translated = AiClient.translate(e);

		assertThat(translated.getStatus()).isEqualTo(HttpStatus.BAD_REQUEST);
		assertThat(translated.getMessage()).isEqualTo("이미지 파일을 읽을 수 없습니다.");
	}

	@Test
	void flaskServerErrorBecomesBadGateway() {
		var e = HttpServerErrorException.create(HttpStatus.INTERNAL_SERVER_ERROR, "boom", json(), new byte[0],
				StandardCharsets.UTF_8);

		assertThat(AiClient.translate(e).getStatus()).isEqualTo(HttpStatus.BAD_GATEWAY);
	}

}
