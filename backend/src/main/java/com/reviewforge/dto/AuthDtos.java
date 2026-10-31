package com.reviewforge.dto;

import java.time.Instant;

import com.reviewforge.domain.User;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public final class AuthDtos {

	private AuthDtos() {
	}

	public record RegisterRequest(
			@NotBlank @Email String email,
			@NotBlank @Size(max = 30) String name,
			@NotBlank @Size(min = 8, max = 64) String password) {
	}

	public record LoginRequest(@NotBlank @Email String email, @NotBlank String password) {
	}

	public record UserResponse(String id, String email, String name, Instant createdAt) {

		public static UserResponse from(User user) {
			return new UserResponse(user.id(), user.email(), user.name(), user.createdAt());
		}

	}

	public record AuthResponse(String token, UserResponse user) {
	}

}
