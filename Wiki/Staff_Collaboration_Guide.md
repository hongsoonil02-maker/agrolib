# 📘 임직원 - 안그래 군단 하이브리드 협업 업무 지침서 (Staff_Collaboration_Guide.md)

> **Agrolib Central Obsidian Vault & GitHub Enterprise Collaboration Standard**  
> 본 가이드는 대표 및 임직원(3~4명)이 안그래 16개 에이전트 군단과 함께 전사 12개 프로젝트를 효율적으로 개발·운용하기 위한 단계별(Step-by-Step) 실무 지침서입니다.

---

## 🧭 1. 전사 협업 아키텍처 및 역할 정의

```
┌────────────────────────────────────────────────────────────────────────┐
│                        임직원 팀 (대표 & 3~4명 임직원)                  │
│   - 업무 지시 (GitHub Issue / Feedback.md)                              │
│   - 코드 리뷰 및 PR 승인 (GitHub Pull Request)                         │
└───────────────────┬────────────────────────────────────────────────────┘
                    │ (INGEST)
                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               안그래 (Master Orchestrator) & 16-Agent Army              │
│   - 요구사항 수집 및 16개 에이전트 프롬프트 변환                        │
│   - 퀀트 전략/SaaS 웹/랜딩페이지 토너먼트 개발 및 백테스트               │
│   - LINT 검사 및 5-Filter System 검증                                  │
└───────────────────┬────────────────────────────────────────────────────┘
                    │ (SAVE & GIT SYNC)
                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│              GitHub Repositories & Agrolib Obsidian Vault              │
│   - 자동 Branch 생성, Commit & Push, PR 생성                            │
│   - /Wiki 및 /Schema 중앙 지식베이스 자동 동기화                       │
└────────────────────────────────────────────────────────────────────────┘
```

### 👥 역할 분담 (R&R)
| 구분 | 임직원 (Human Staff) | 안그래 16개 에이전트 (AI Army) |
|---|---|---|
| **업무 지시** | 아이디어, 기획, 목표, 우선순위 결정 | 지시사항 파싱(`INGEST`) 및 파이프라인 수립 |
| **개발/작업** | 코드 리뷰, 최종 승인 및 피드백 | 코드 작성, 백테스트, UI/UX 구현, 린팅(`LINT`) |
| **지식 관리** | 주요 승인 및 결과 검수 | 5-Filter 검증 후 GitHub/Obsidian 저장(`SAVE`) |

---

## 🔄 2. Step-by-Step 협업 4단계 파이프라인

### 📌 Step 1: 업무 지시 및 요구사항 등록 (Task Creation)
임직원은 편한 채널을 통해 지시사항을 등록합니다.

- **방법 A (권장): GitHub Issue 작성**
  - 대상: 퀀트 전략 추가, SaaS 피처 개발, 버그 제보, 랜딩페이지 수정
  - 위치: 해당 프로젝트 GitHub 레포지토리 ➔ `Issues` ➔ `New Issue`
  - 작성 언어: **한국어**
- **방법 B: Obsidian Feedback.md 작성**
  - 대상: 전체적인 아이디어, 기획 구상, 종합 지시
  - 위치: `[agrolib/Wiki/Feedback.md](file:///c:/Users/master/agrolib/Wiki/Feedback.md)`

---

### 📌 Step 2: 안그래 군단의 작업 수집 및 실행 (INGEST & EXECUTE)
1. **Agent 15 (Feedback Ingestor)** 및 안그래가 이슈/피드백을 자동 수집(`INGEST`).
2. 지시 내용에 따라 전문 에이전트 배정:
   - 퀀트 백테스트: Agent 03 (알파), Agent 04 (백테스터), Agent 05 (리스크)
   - SaaS/웹 개발: Agent 02 (UI/UX), Agent 06 (API), Agent 07 (Auto-Tuner)
3. **Agent 08 (Auditor)**가 코드 보안 및 규격 검증(`LINT`) 수행.

---

### 📌 Step 3: 결과물 검증 & PR 생성 (5-Filter & SAVE)
1. **Agent 14 (Wiki Architect)**가 결과를 5-Filter System으로 검증.
2. 검증을 통과한 지식은 `agrolib/Wiki`에 수록하고, 개발 코드는 GitHub 원격 레포지토리에 새 브랜치로 `commit & push` 후 **Pull Request(PR)**를 자동 생성(`SAVE`).

---

### 📌 Step 4: 임직원 검수 및 최종 승인 (Review & Approve)
1. 임직원은 생성된 GitHub PR을 확인하고 리뷰(Review)를 진행.
2. 수정할 내용이 있으면 PR 코멘트로 추가 요청 ➔ 안그래가 즉시 재수정.
3. 승인(Approve & Merge) 시 메인 코드베이스에 반영되며, 필요 시 서버에 자동 배포.

---

## 🛠️ 3. 상황별 실무 레시피 (Use-Case Scenarios)

### 📈 시나리오 1: 퀀트 전략 변경 또는 백테스트 요청 시
1. 임직원이 GitHub Issue에 `"나스닥 봇 B에 Keltner Squeeze 손절폭 1.5%로 변경 후 3개년 백테스트 실행해줘"` 작성.
2. 안그래가 `quant_system` 엔진에서 몬테카를로 백테스트 수행.
3. 결과를 `agrolib/Wiki/Tournament_Winners.md`에 업로드하고, GitHub PR을 작성하여 보고.

### 🌐 시나리오 2: 100-Bagger SaaS 웹 신규 기능 추가 시
1. 임직원이 `100_bagger_saas` 레포 이슈에 `"유저 대시보드에 포트폴리오 수익률 차트 컴포넌트 추가해줘"` 작성.
2. Agent 02와 Agent 06이 React/Next.js 컴포넌트 및 백엔드 API 작성.
3. Agent 08의 `LINT` 통과 후 PR 발송 ➔ 임직원 확인 후 Merge.

### 🌿 시나리오 3: 로타갈/베타콜 랜딩페이지 문구/디자인 수정 시
1. 임직원이 `rotagal-landing` 레포에 이슈 생성.
2. Agent 02 및 Agent 07이 모바일 반응형 및 UI 애니메이션 수정 후 PR 생성.

---

## ⚠️ 4. 임직원 필수 준수 규칙 (Do's & Don'ts)

| 구분 | Do (권장 사항) | Don't (금지 사항) |
|---|---|---|
| **원본 데이터** | `/Raw` 폴더는 참조 및 조회 용도로만 사용 | `/Raw` 내의 로그/백테스트 원본 파일 직접 수정/삭제 금지 |
| **업무 지시** | GitHub Issue 또는 `Feedback.md`에 명확하게 작성 | 구두 전달 후 기록을 남기지 않는 작업 지시 |
| **언어 사용** | 임직원은 **한국어**로 편하게 설명/작성 | 시스템 명령어 구동 시 영문 키워드 규칙 유의 |
| **코드 승인** | 중요한 운영 코드 변경은 반드시 PR 승인 후 적용 | 검증되지 않은 코드 메인 브랜치 직푸시(Direct Push) |

---

## ⚡ 퀵 참고 명령어 & 링크
- 📊 대시보드: `[agrolib/Schema/Index.md](file:///c:/Users/master/agrolib/Schema/Index.md)`
- 🤖 에이전트 롤: `[agrolib/Schema/Agent.md](file:///c:/Users/master/agrolib/Schema/Agent.md)`
- 💬 피드백 창구: `[agrolib/Wiki/Feedback.md](file:///c:/Users/master/agrolib/Wiki/Feedback.md)`
- 🌐 프로젝트 현황: `[agrolib/Wiki/Projects_Overview.md](file:///c:/Users/master/agrolib/Wiki/Projects_Overview.md)`
