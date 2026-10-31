package com.reviewforge.auth;

import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

/**
 * Bearer 토큰이 유효하면 요청 속성 {@code userId} 를 채운다.
 * 인증 필수 여부는 각 컨트롤러가 {@code @RequestAttribute} 로 판단한다.
 */
@Component
public class AuthInterceptor implements HandlerInterceptor {

	public static final String USER_ID = "userId";
	private static final String BEARER = "Bearer ";

	private final JwtService jwtService;

	public AuthInterceptor(JwtService jwtService) {
		this.jwtService = jwtService;
	}

	@Override
	public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
		String header = request.getHeader(HttpHeaders.AUTHORIZATION);
		if (header != null && header.startsWith(BEARER)) {
			jwtService.parseUserId(header.substring(BEARER.length()))
					.ifPresent(id -> request.setAttribute(USER_ID, id));
		}
		return true;
	}

}
