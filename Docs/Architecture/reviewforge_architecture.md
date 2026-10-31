# ReviewForge 시스템 아키텍처

**프로젝트**: ReviewForge  
**버전**: 1.0  
**작성일**: 2026-11-01

## 계층 구조

1. **Presentation Layer**: Next.js (App Router)
   - UI, 폼, 대시보드, 인증 UI
2. **Orchestration Layer**: Spring Boot
   - API Gateway, 비즈니스 로직, MongoDB 연동, Flask 프록시
3. **AI/ML Layer**: Flask
   - 텍스트 전처리, NLP 분류 모델 추론, Gradio
4. **Data Layer**: MongoDB Atlas
   - User, Analysis 컬렉션

## 데이터 흐름

```
사용자 입력 (Next.js)
    ↓
Spring Boot (검증 + 오케스트레이션)
    ↓
Flask (ML 추론)
    ↓
Spring Boot (결과 저장 + 응답)
    ↓
Next.js (시각화)
    ↓
MongoDB Atlas (영속화)
```

## 포트 및 환경

| 서비스 | 포트 | 비고 |
|--------|------|------|
| Next.js | 3000 | Frontend |
| Spring Boot | 8080 | Orchestrator |
| Flask | 5000 | AI Server + Gradio |
| MongoDB Atlas | - | 클라우드 |

자세한 내용은 루트 `ReviewForge_인수인계.md` 및 `AGENTS.md`를 참조하세요.
