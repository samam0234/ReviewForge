package com.reviewforge.auth;

import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.Optional;

import javax.crypto.SecretKey;

import org.springframework.stereotype.Service;

import com.reviewforge.config.AppProperties;

import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;

@Service
public class JwtService {

	private final SecretKey key;
	private final long expirationMillis;

	public JwtService(AppProperties props) {
		this.key = Keys.hmacShaKeyFor(props.jwtSecret().getBytes(StandardCharsets.UTF_8));
		this.expirationMillis = props.jwtExpiration().toMillis();
	}

	public String issue(String userId, String email) {
		Date now = new Date();
		return Jwts.builder()
				.subject(userId)
				.claim("email", email)
				.issuedAt(now)
				.expiration(new Date(now.getTime() + expirationMillis))
				.signWith(key)
				.compact();
	}

	public Optional<String> parseUserId(String token) {
		try {
			return Optional.ofNullable(
					Jwts.parser().verifyWith(key).build().parseSignedClaims(token).getPayload().getSubject());
		} catch (JwtException | IllegalArgumentException e) {
			return Optional.empty();
		}
	}

}
