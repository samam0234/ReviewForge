package com.reviewforge.auth;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.Duration;
import java.util.List;

import org.junit.jupiter.api.Test;

import com.reviewforge.config.AppProperties;

class JwtServiceTest {

	private static AppProperties props(String secret, Duration expiration) {
		return new AppProperties("http://localhost:5000", Duration.ofSeconds(5), secret, expiration, List.of());
	}

	private final JwtService jwt = new JwtService(props("test-secret-test-secret-test-secret-32", Duration.ofHours(1)));

	@Test
	void issuedTokenRoundTrips() {
		assertThat(jwt.parseUserId(jwt.issue("user-1", "a@b.com"))).contains("user-1");
	}

	@Test
	void tamperedOrForeignTokenIsRejected() {
		JwtService other = new JwtService(props("another-secret-another-secret-another-32", Duration.ofHours(1)));
		assertThat(jwt.parseUserId(other.issue("user-1", "a@b.com"))).isEmpty();
		assertThat(jwt.parseUserId("not-a-jwt")).isEmpty();
	}

	@Test
	void expiredTokenIsRejected() {
		JwtService expired = new JwtService(props("test-secret-test-secret-test-secret-32", Duration.ofSeconds(-1)));
		assertThat(jwt.parseUserId(expired.issue("user-1", "a@b.com"))).isEmpty();
	}

}
