package com.reviewforge.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.startsWith;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.content;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.header;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

import java.nio.charset.StandardCharsets;

import org.junit.jupiter.api.Test;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.RestClient;

import com.reviewforge.exception.ApiException;
import com.reviewforge.service.AiClient.ImageUpload;

class AiClientTest {

	private static HttpHeaders json() {
		HttpHeaders headers = new HttpHeaders();
		headers.setContentType(MediaType.APPLICATION_JSON);
		return headers;
	}

	/** 실제 RestClient 직렬화 경로를 거친다 (목 서비스로는 클래스패스 문제를 잡을 수 없다). */
	@Test
	void multipartRequestIsSerializedWithTextAndImageParts() {
		RestClient.Builder builder = RestClient.builder().baseUrl("http://ai");
		MockRestServiceServer server = MockRestServiceServer.bindTo(builder).build();
		server.expect(requestTo("http://ai/analyze"))
				.andExpect(header(HttpHeaders.CONTENT_TYPE, startsWith(MediaType.MULTIPART_FORM_DATA_VALUE)))
				.andExpect(content().string(allOf(
						containsString("name=\"text\""), containsString("배송 3일"),
						containsString("name=\"image\"; filename=\"a.png\""), containsString("Content-Type: image/png"))))
				.andRespond(withSuccess("""
						{"fakeProbability":0.41,"confidenceScore":59,"label":"Suspicious","keywords":[],"highlights":[],
						 "source":"hybrid","textFakeProbability":0.2,
						 "image":{"fakeProbability":0.9,"confidenceScore":90,"label":"Fake","signals":["단색 배경"],
						          "source":"rules","width":300,"height":300}}
						""", MediaType.APPLICATION_JSON));

		var result = new AiClient(builder.build())
				.analyze("배송 3일", new ImageUpload(new byte[] { 1, 2, 3 }, "a.png", MediaType.IMAGE_PNG));

		server.verify();
		assertThat(result.textFakeProbability()).isEqualTo(0.2);
		assertThat(result.image().signals()).containsExactly("단색 배경");
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
