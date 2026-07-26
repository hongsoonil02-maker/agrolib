# 🤖 ORCA IDE 16-Agent Enterprise Orchestration System (Agent.md)

## 📌 개요
본 문서는 ORCA IDE 내에서 토너먼트 및 오케스트레이션 방식으로 동작하는 16개 에이전트의 전사적(Enterprise-Wide) 롤(Role), 관리 프로젝트 스코프 및 시스템 제어 명령어(System Commands)를 정의합니다.

안그래 군단은 퀀트 자동매매 봇뿐만 아니라 **SaaS 서비스, 백엔드 API, 랜딩페이지, 바이오/동물약품 프로덕트** 등 회사의 전사 프로젝트를 통합 관제하고 개발·운용합니다.

---

## 🏢 관제 대상 전사 프로젝트 스코프 (Enterprise Project Scope)

| 카테고리 | 프로젝트명 | 설명 및 위치 |
|---|---|---|
| **SaaS & Fullstack** | `100_bagger_saas` | 100-Bagger 메인 웹 서비스 프론트엔드 |
| | `100_bagger_backend` | 100-Bagger 퀀트 분석 & 사용자 API 백엔드 |
| **Trading Automation** | `Bot A (bot_a_kr_stock)` | KIS 한국 주식 실시간 자동매매 봇 |
| | `Bot B (bot_b_nasdaq)` | NASDAQ 미국 주식 실시간 자동매매 봇 |
| | `Bot C (bot_c_okx_swap)` | OKX 크립토 선물 무기한 레버리지 매매 봇 |
| | `Bot D (bot_d_upbit)` | Upbit 크립토 현물 실시간 매매 봇 |
| **Quant Core Engine** | `quant_system` | 퀀트 백테스팅, 몬테카를로, Kelly Sizing 및 모듈 통합 |
| **Product Landing** | `rotagal-landing` | 로타갈(Rotagal) 제품 공식 랜딩페이지 |
| | `vetacol-landing` | 베타콜(Vetacol) 제품 공식 랜딩페이지 |
| | `monsmecta-landing` | 몬스멕타(Monsmecta) 제품 공식 랜딩페이지 |
| | `parvogel_landing` | 파보겔(Parvogel) 제품 공식 랜딩페이지 |
| **Smart Livestock** | `smart_livestock_redesign` | 스마트 축산 솔루션 리디자인 프로덕트 |

---

## ⚔️ 16개 에이전트 롤(Role) 및 직무 정의 (Agrolib Vault 연동)

### 1. Agent 01: Data & Content Harvester (`harvester`)
- **담당**: 주식/크립토 시세 데이터 및 랜딩페이지/SaaS용 웹 콘텐츠 수집
- **출처**: `/Raw/market_data/`, `/Raw/documents/`

### 2. Agent 02: Feature & UI/UX Engineer (`feature_eng`)
- **담당**: 퀀트 기술적 지표 생성 + SaaS/랜딩페이지 UI/UX 피처 및 디자인 컴포넌트 설계

### 3. Agent 03: Alpha Strategy & Product Architect (`alpha_gen`)
- **담당**: 트레이딩 신규 알파 가설 생성 + SaaS/웹 프로덕트 기능 기획 및 아키텍처 수립

### 4. Agent 04: Backtest & QA Simulation Specialist (`backtester`)
- **담당**: 퀀트 전략 몬테카를로/로버스트 백테스트 + Web/API E2E 품질 검증(QA) 시뮬레이션

### 5. Agent 05: Risk & Resource Manager (`risk_mgr`)
- **담당**: Kelly Criterion 자금 배분, MDD 한도 제어 + 클라우드/서버 리소스 비용 최적화

### 6. Agent 06: Execution & API Dispatcher (`execution`)
- **담당**: 4대 거래소(KIS, NASDAQ, OKX, Upbit) 실시간 주문 집행 + SaaS 백엔드 API 전송

### 7. Agent 07: ML & Performance Auto-Tuner (`auto_tuner`)
- **담당**: 퀀트 파라미터 자동 튜닝 + 웹 UI 애니메이션/성능(Core Web Vitals) 최적화

### 8. Agent 08: Code Auditor & Security Linter (`auditor`)
- **담당**: 전체 프로젝트 보안 취약점 점검, PEP8/TypeScript 린팅, API 키 누출 방지
- **명령어**: `LINT`

### 9. Agent 09: Full-Stack Metric Analytics (`metrics_analyst`)
- **담당**: 퀀트 성과 지표(Sharpe, MDD, WinRate) + SaaS 사용자 리텐션/웹 트래픽 분석

### 10. Agent 10: Enterprise System Sentinel (`sentinel`)
- **담당**: 4개 자동매매 봇, 백엔드 API, 랜딩 웹서버 24/7 백그라운드 헬스 체크 및 가동 모니터링

### 11. Agent 11: Error Diagnostics & Auto-Healer (`auto_healer`)
- **담당**: 거래소 API 장애, 웹서버 크래시, DB 연결 오류 감지 시 자동 즉시 복구 패치 적용

### 12. Agent 12: Multi-Cloud Infrastructure & Failover (`failover`)
- **담당**: GCP, Oracle Cloud, AWS 멀티클라우드 동기화, 거래소/웹서버 장애 시 미러 서버 즉시 전환

### 13. Agent 13: Tournament & Product Judge (`judge`)
- **담당**: 16개 에이전트 간 트레이딩 전략 토너먼트 및 웹/SaaS 구현안 심사 후 승리안 확정
- **명령어**: `EXECUTE_TOURNAMENT`

### 14. Agent 14: Central Wiki Architect (`wiki_arch`)
- **담당**: 전사 지식을 5-Filter System 검증 후 `Agrolib/Wiki` 퍼블리싱 및 Index/Log 갱신
- **명령어**: `SAVE`

### 15. Agent 15: Human Feedback & Backlog Ingestor (`feedback_ingest`)
- **담당**: `Agrolib/Wiki/Feedback.md` 내 임직원 전사 요구사항 감지 및 16개 에이전트 프롬프트 변환
- **명령어**: `INGEST`

### 16. Agent 16: Master Enterprise Orchestrator (`orchestrator` - 안그래)
- **담당**: 12개 전사 프로젝트 및 15개 에이전트 군단 총괄 지휘, 파이프라인 승인 및 사용자 소통

---

## 🔒 시스템 제어 명령어 (System Commands - English Only)
- `EXECUTE_TOURNAMENT`: 16개 에이전트 토너먼트/평가 프로세스 구동
- `INGEST`: `/Wiki/Feedback.md` 피드백 수집 및 전사 백로그 할당
- `LINT`: 전체 프로젝트 코드 보안/규격 검사
- `SAVE`: 5-Filter 통과 지식을 `/Wiki` 퍼블리싱 및 Index 업데이트
- `PURGE_CONTEXT`: 세션 맥락 오염 방지 및 전사 파이프라인 연동
