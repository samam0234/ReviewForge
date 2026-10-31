package com.reviewforge.domain;

import java.time.Instant;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

@Document("users")
public record User(
		@Id String id,
		@Indexed(unique = true) String email,
		String name,
		String passwordHash,
		Instant createdAt) {

	public static User create(String email, String name, String passwordHash) {
		return new User(null, email, name, passwordHash, Instant.now());
	}

}
