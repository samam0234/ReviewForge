package com.reviewforge.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.domain.Pageable;
import org.springframework.data.mongodb.repository.MongoRepository;

import com.reviewforge.domain.Analysis;

public interface AnalysisRepository extends MongoRepository<Analysis, String> {

	List<Analysis> findByUserIdOrderByCreatedAtDesc(String userId, Pageable pageable);

	Optional<Analysis> findByIdAndUserId(String id, String userId);

}
