package com.reviewforge;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

/** MongoDB 없이도 컨텍스트가 뜨는지 확인 (인덱스 생성만 끈다. 클라이언트는 지연 연결). */
@SpringBootTest(properties = "spring.data.mongodb.auto-index-creation=false")
class BackendApplicationTests {

	@Test
	void contextLoads() {
	}

}
