package com.reviewforge.service;

import java.util.Locale;

import org.springframework.dao.DuplicateKeyException;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import com.reviewforge.auth.JwtService;
import com.reviewforge.domain.User;
import com.reviewforge.dto.AuthDtos.AuthResponse;
import com.reviewforge.dto.AuthDtos.LoginRequest;
import com.reviewforge.dto.AuthDtos.RegisterRequest;
import com.reviewforge.dto.AuthDtos.UserResponse;
import com.reviewforge.exception.ApiException;
import com.reviewforge.repository.UserRepository;

@Service
public class AuthService {

	private final UserRepository users;
	private final PasswordEncoder passwordEncoder;
	private final JwtService jwtService;

	public AuthService(UserRepository users, PasswordEncoder passwordEncoder, JwtService jwtService) {
		this.users = users;
		this.passwordEncoder = passwordEncoder;
		this.jwtService = jwtService;
	}

	public AuthResponse register(RegisterRequest req) {
		String email = req.email().toLowerCase(Locale.ROOT);
		if (users.existsByEmail(email)) {
			throw new ApiException(HttpStatus.CONFLICT, "이미 가입된 이메일입니다.");
		}
		try {
			User saved = users.save(User.create(email, req.name().trim(), passwordEncoder.encode(req.password())));
			return toAuthResponse(saved);
		} catch (DuplicateKeyException e) {
			throw new ApiException(HttpStatus.CONFLICT, "이미 가입된 이메일입니다.");
		}
	}

	public AuthResponse login(LoginRequest req) {
		User user = users.findByEmail(req.email().toLowerCase(Locale.ROOT))
				.filter(u -> passwordEncoder.matches(req.password(), u.passwordHash()))
				.orElseThrow(() -> new ApiException(HttpStatus.UNAUTHORIZED, "이메일 또는 비밀번호가 올바르지 않습니다."));
		return toAuthResponse(user);
	}

	public UserResponse me(String userId) {
		return users.findById(userId).map(UserResponse::from).orElseThrow(ApiException::unauthorized);
	}

	private AuthResponse toAuthResponse(User user) {
		return new AuthResponse(jwtService.issue(user.id(), user.email()), UserResponse.from(user));
	}

}
