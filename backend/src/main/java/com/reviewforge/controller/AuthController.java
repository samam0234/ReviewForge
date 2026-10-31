package com.reviewforge.controller;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestAttribute;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import com.reviewforge.auth.AuthInterceptor;
import com.reviewforge.dto.AuthDtos.AuthResponse;
import com.reviewforge.dto.AuthDtos.LoginRequest;
import com.reviewforge.dto.AuthDtos.RegisterRequest;
import com.reviewforge.dto.AuthDtos.UserResponse;
import com.reviewforge.exception.ApiException;
import com.reviewforge.service.AuthService;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

	private final AuthService authService;

	public AuthController(AuthService authService) {
		this.authService = authService;
	}

	@PostMapping("/register")
	@ResponseStatus(HttpStatus.CREATED)
	public AuthResponse register(@Valid @RequestBody RegisterRequest req) {
		return authService.register(req);
	}

	@PostMapping("/login")
	public AuthResponse login(@Valid @RequestBody LoginRequest req) {
		return authService.login(req);
	}

	@GetMapping("/me")
	public UserResponse me(@RequestAttribute(name = AuthInterceptor.USER_ID, required = false) String userId) {
		if (userId == null) {
			throw ApiException.unauthorized();
		}
		return authService.me(userId);
	}

}
