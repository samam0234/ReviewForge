package com.reviewforge.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.client.RestClient;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import com.reviewforge.auth.AuthInterceptor;

@Configuration
public class WebConfig implements WebMvcConfigurer {

	private final AppProperties props;
	private final AuthInterceptor authInterceptor;

	public WebConfig(AppProperties props, AuthInterceptor authInterceptor) {
		this.props = props;
		this.authInterceptor = authInterceptor;
	}

	@Override
	public void addCorsMappings(CorsRegistry registry) {
		registry.addMapping("/api/**")
				.allowedOrigins(props.corsOrigins().toArray(String[]::new))
				.allowedMethods("GET", "POST", "OPTIONS")
				.allowedHeaders("*");
	}

	@Override
	public void addInterceptors(InterceptorRegistry registry) {
		registry.addInterceptor(authInterceptor).addPathPatterns("/api/**");
	}

	@Bean
	RestClient aiRestClient() {
		SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
		factory.setConnectTimeout(props.aiTimeout());
		factory.setReadTimeout(props.aiTimeout());
		return RestClient.builder()
				.baseUrl(props.aiServerUrl())
				.requestFactory(factory)
				.build();
	}

	@Bean
	PasswordEncoder passwordEncoder() {
		return new BCryptPasswordEncoder();
	}

}
