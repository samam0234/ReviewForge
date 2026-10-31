package com.reviewforge.exception;

import java.util.Map;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.ErrorResponse;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.multipart.MaxUploadSizeExceededException;

@RestControllerAdvice
public class GlobalExceptionHandler {

	private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

	@ExceptionHandler(ApiException.class)
	ResponseEntity<Map<String, String>> handleApi(ApiException e) {
		return error(e.getStatus(), e.getMessage());
	}

	@ExceptionHandler(MethodArgumentNotValidException.class)
	ResponseEntity<Map<String, String>> handleValidation(MethodArgumentNotValidException e) {
		String message = e.getBindingResult().getFieldErrors().stream()
				.map(f -> f.getField() + ": " + f.getDefaultMessage())
				.collect(Collectors.joining(", "));
		return error(HttpStatus.BAD_REQUEST, message);
	}

	@ExceptionHandler(HttpMessageNotReadableException.class)
	ResponseEntity<Map<String, String>> handleUnreadable(HttpMessageNotReadableException e) {
		return error(HttpStatus.BAD_REQUEST, "요청 본문(JSON)을 읽을 수 없습니다.");
	}

	@ExceptionHandler(MaxUploadSizeExceededException.class)
	ResponseEntity<Map<String, String>> handleTooLarge(MaxUploadSizeExceededException e) {
		return error(HttpStatus.CONTENT_TOO_LARGE, "이미지는 5MB 이하로 올려 주세요.");
	}

	@ExceptionHandler(Exception.class)
	ResponseEntity<Map<String, String>> handleUnknown(Exception e) {
		if (e instanceof ErrorResponse spring) {
			String detail = spring.getBody().getDetail();
			return error(HttpStatus.valueOf(spring.getStatusCode().value()), detail != null ? detail : e.getMessage());
		}
		log.error("Unhandled exception", e);
		return error(HttpStatus.INTERNAL_SERVER_ERROR, "서버 오류가 발생했습니다.");
	}

	private ResponseEntity<Map<String, String>> error(HttpStatus status, String message) {
		return ResponseEntity.status(status).body(Map.of("error", message));
	}

}
