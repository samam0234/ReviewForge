package com.reviewforge.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.ArgumentMatchers.isNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.mock.web.MockMultipartFile;

import com.reviewforge.domain.Analysis;
import com.reviewforge.domain.Analysis.ImageResult;
import com.reviewforge.dto.AnalysisDtos.AiAnalyzeResult;
import com.reviewforge.dto.AnalysisDtos.LabelBucket;
import com.reviewforge.exception.ApiException;
import com.reviewforge.repository.AnalysisRepository;
import com.reviewforge.service.AiClient.ImageUpload;

class AnalysisServiceTest {

	private final AiClient aiClient = mock(AiClient.class);
	private final AnalysisRepository repository = mock(AnalysisRepository.class);
	private final AnalysisService service = new AnalysisService(aiClient, repository);

	private static final AiAnalyzeResult AI_RESULT =
			new AiAnalyzeResult(0.9, 90, "Fake", List.of("최고"), List.of(), "hybrid", 0.9, null);

	@Test
	void anonymousAnalysisIsNotSaved() {
		when(aiClient.analyze(eq("최고!!"), isNull())).thenReturn(AI_RESULT);

		var res = service.analyze("  최고!!  ", null);

		assertThat(res.saved()).isFalse();
		assertThat(res.label()).isEqualTo("Fake");
		verify(repository, never()).save(any());
	}

	@Test
	void loggedInAnalysisIsSaved() {
		when(aiClient.analyze(eq("최고!!"), isNull())).thenReturn(AI_RESULT);
		when(repository.save(any(Analysis.class))).thenAnswer(inv -> {
			Analysis a = inv.getArgument(0);
			return new Analysis("id-1", a.userId(), a.reviewText(), a.fakeProbability(), a.confidenceScore(),
					a.label(), a.keywords(), a.highlights(), a.textFakeProbability(), a.image(), a.createdAt());
		});

		var res = service.analyze("최고!!", "user-1");

		assertThat(res.saved()).isTrue();
		assertThat(res.id()).isEqualTo("id-1");
	}

	@Test
	void imageIsForwardedAndResultKept() {
		var image = new ImageResult(0.7, 70, "Fake", List.of("단색 배경"), "rules", 300, 300);
		when(aiClient.analyze(eq("배송 3일"), any(ImageUpload.class)))
				.thenReturn(new AiAnalyzeResult(0.4, 60, "Suspicious", List.of(), List.of(), "hybrid", 0.2, image));

		var res = service.analyze("배송 3일", new MockMultipartFile("image", "a.png", "image/png", new byte[] { 1, 2 }),
				null);

		assertThat(res.textFakeProbability()).isEqualTo(0.2);
		assertThat(res.image().signals()).containsExactly("단색 배경");
	}

	@Test
	void blankTextAndBadImageAreRejectedBeforeCallingAi() {
		assertThatThrownBy(() -> service.analyze("   ", null, null))
				.isInstanceOfSatisfying(ApiException.class, e -> assertThat(e.getStatus()).isEqualTo(HttpStatus.BAD_REQUEST));
		assertThatThrownBy(() -> service.analyze("좋아요", new MockMultipartFile("image", "a.gif", "image/gif", new byte[] { 1 }), null))
				.isInstanceOfSatisfying(ApiException.class,
						e -> assertThat(e.getStatus()).isEqualTo(HttpStatus.UNSUPPORTED_MEDIA_TYPE));
		assertThatThrownBy(() -> service.analyze("좋아요",
				new MockMultipartFile("image", "a.png", "image/png", new byte[5 * 1024 * 1024 + 1]), null))
				.isInstanceOfSatisfying(ApiException.class,
						e -> assertThat(e.getStatus()).isEqualTo(HttpStatus.CONTENT_TOO_LARGE));
		verifyNoInteractions(aiClient);
	}

	@Test
	void statsUseWeightedAverageOverAllBuckets() {
		// 라벨별 평균을 다시 평균하면 (0.1 + 0.9) / 2 = 0.5 가 되지만, 건수 가중 평균은 (0.3 + 0.9) / 4 = 0.3 이다.
		when(repository.labelBuckets("user-1")).thenReturn(List.of(
				new LabelBucket("Genuine", 3, 0.3, 270, 1),
				new LabelBucket("Fake", 1, 0.9, 90, 0)));

		var stats = service.stats("user-1");

		assertThat(stats.total()).isEqualTo(4);
		assertThat(stats.avgFakeProbability()).isEqualTo(0.3);
		assertThat(stats.avgConfidenceScore()).isEqualTo(90.0);
		assertThat(stats.labelCounts()).containsExactly(
				org.assertj.core.api.Assertions.entry("Genuine", 3L),
				org.assertj.core.api.Assertions.entry("Suspicious", 0L),
				org.assertj.core.api.Assertions.entry("Fake", 1L));
		assertThat(stats.withImage()).isEqualTo(1);
	}

	@Test
	void statsForNewUserAreZero() {
		when(repository.labelBuckets("new")).thenReturn(List.of());

		var stats = service.stats("new");

		assertThat(stats.total()).isZero();
		assertThat(stats.avgFakeProbability()).isZero();
		assertThat(stats.labelCounts()).containsOnlyKeys("Genuine", "Suspicious", "Fake");
	}

}
