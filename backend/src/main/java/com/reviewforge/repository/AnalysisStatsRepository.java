package com.reviewforge.repository;

import java.util.List;

import com.reviewforge.dto.AnalysisDtos.LabelBucket;

/** {@link AnalysisRepository} 에 붙는 집계 전용 커스텀 조각. */
public interface AnalysisStatsRepository {

	List<LabelBucket> labelBuckets(String userId);

}
