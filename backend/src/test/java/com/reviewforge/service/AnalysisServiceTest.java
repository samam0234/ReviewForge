package com.reviewforge.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.List;

import org.junit.jupiter.api.Test;

import com.reviewforge.domain.Analysis;
import com.reviewforge.dto.AnalysisDtos.AiAnalyzeResult;
import com.reviewforge.repository.AnalysisRepository;

class AnalysisServiceTest {

	private final AiClient aiClient = mock(AiClient.class);
	private final AnalysisRepository repository = mock(AnalysisRepository.class);
	private final AnalysisService service = new AnalysisService(aiClient, repository);

	private static final AiAnalyzeResult AI_RESULT =
			new AiAnalyzeResult(0.9, 90, "Fake", List.of("최고"), List.of(), "hybrid");

	@Test
	void anonymousAnalysisIsNotSaved() {
		when(aiClient.analyze("최고!!")).thenReturn(AI_RESULT);

		var res = service.analyze("  최고!!  ", null);

		assertThat(res.saved()).isFalse();
		assertThat(res.label()).isEqualTo("Fake");
		verify(repository, never()).save(any());
	}

	@Test
	void loggedInAnalysisIsSaved() {
		when(aiClient.analyze("최고!!")).thenReturn(AI_RESULT);
		when(repository.save(any(Analysis.class))).thenAnswer(inv -> {
			Analysis a = inv.getArgument(0);
			return new Analysis("id-1", a.userId(), a.reviewText(), a.fakeProbability(), a.confidenceScore(),
					a.label(), a.keywords(), a.highlights(), a.createdAt());
		});

		var res = service.analyze("최고!!", "user-1");

		assertThat(res.saved()).isTrue();
		assertThat(res.id()).isEqualTo("id-1");
	}

}
