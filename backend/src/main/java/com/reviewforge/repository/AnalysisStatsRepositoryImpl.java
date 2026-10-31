package com.reviewforge.repository;

import static org.springframework.data.mongodb.core.aggregation.Aggregation.group;
import static org.springframework.data.mongodb.core.aggregation.Aggregation.match;
import static org.springframework.data.mongodb.core.aggregation.Aggregation.newAggregation;
import static org.springframework.data.mongodb.core.aggregation.Aggregation.project;
import static org.springframework.data.mongodb.core.query.Criteria.where;

import java.util.Arrays;
import java.util.List;

import org.bson.Document;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.aggregation.Aggregation;
import org.springframework.data.mongodb.core.aggregation.AggregationExpression;

import com.reviewforge.domain.Analysis;
import com.reviewforge.dto.AnalysisDtos.LabelBucket;

class AnalysisStatsRepositoryImpl implements AnalysisStatsRepository {

	/** {@code image} 필드가 있고 null 이 아니면 1 ({@code $gt: ["$image", null]} 는 누락·null 모두 false). */
	private static final AggregationExpression HAS_IMAGE = context -> new Document("$cond",
			Arrays.asList(new Document("$gt", Arrays.asList("$image", null)), 1, 0));

	private final MongoTemplate mongo;

	AnalysisStatsRepositoryImpl(MongoTemplate mongo) {
		this.mongo = mongo;
	}

	/** userId 로 거른 뒤 라벨별 건수·합계를 DB 에서 한 번에 계산한다 (최근 N건이 아니라 전체 기록 기준). */
	@Override
	public List<LabelBucket> labelBuckets(String userId) {
		Aggregation aggregation = newAggregation(
				match(where("userId").is(userId)),
				project("label", "fakeProbability", "confidenceScore").and(HAS_IMAGE).as("hasImage"),
				group("label")
						.count().as("count")
						.sum("fakeProbability").as("sumFakeProbability")
						.sum("confidenceScore").as("sumConfidenceScore")
						.sum("hasImage").as("withImage"));
		return mongo.aggregate(aggregation, mongo.getCollectionName(Analysis.class), Document.class)
				.getMappedResults().stream()
				.map(AnalysisStatsRepositoryImpl::toBucket)
				.toList();
	}

	static LabelBucket toBucket(Document doc) {
		return new LabelBucket(doc.getString("_id"), number(doc, "count").longValue(),
				number(doc, "sumFakeProbability").doubleValue(), number(doc, "sumConfidenceScore").doubleValue(),
				number(doc, "withImage").longValue());
	}

	private static Number number(Document doc, String key) {
		Object value = doc.get(key);
		return value instanceof Number n ? n : 0;
	}

}
