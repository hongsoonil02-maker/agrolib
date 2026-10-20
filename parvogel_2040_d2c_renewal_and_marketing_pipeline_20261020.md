# 파보겔(ParvoGel) 2040 D2C 리뉴얼·보안/성능 최적화 및 마케팅 파이프라인 진단 보고서 (2026-10-20)

## 1. 홈페이지 전면 리뉴얼 및 수정 적용 내역 (`parvogel.kr`)

### ① 몬스멕타(동물병원 전용) 전역 제거 및 타깃 명확화
- **몬스멕타 완전 삭제**: `MonsmectaGateway.jsx`, `MonsmectaNoticeModal.jsx`, `MonsmectaClinicalCase.jsx`, `MonsmectaLineupSection.jsx`, `MonsmectaMoaSection.jsx`, `public/assets/monsmecta-popup-embed.html` 및 29개 안내판 HTML·SEO·사이트맵·마케팅 팩토리 어댑터 내 `몬스멕타` 텍스트 100% 제거 (`0건`).
- **동물병원·수의사 상담 폼 제거**: `OrderForm.jsx` 및 `PartnerNoticeModal.jsx`에서 `동물병원·수의사` 탭 및 병원명/수의사명 입력 필드를 제거하고 **일반 보호자 + 펫샵 + 브리더(번식농장)** 전용 온라인 쇼핑몰 및 B2B 파트너 포털로 일원화.
- **산업동물 (주)엠오바이오 독점 총판 안내 축약**: `AnimalSelector.jsx` 및 `Landing.jsx`에서 송아지·자돈·염소·양·망아지 5개 개별 탭을 단일 안내 탭(`🐮 산업동물 (엠오바이오 총판)`)으로 통합 축약.

### ② 홍효선 대표이사 피드백 반영: 2040 젊은 감각 D2C 펫 헬스케어 리뉴얼
1. **컬러 & 타이포그래피 다이어트**: 어두운 남색/경고등 위주의 카탈로그 톤에서 따뜻한 웜화이트(`#FAF9F6`)·소프트 스카이블루·민트 파스텔 카드 디자인으로 전면 개편.
2. **2040 댕냥집사 공감형 카피라이팅**: `'동물용 활명수'`, `'환축'`, `'신생아 지사 보조제'` 등 올드한 축산·제약 표현을 *"새벽에 갑자기 토하고 설사할 때, 당황하지 말고 입에 대고 1초 톡! ‘파보겔’"*, *"가루약 거품 무는 아이도 간식처럼 냠냠 핥아먹어요 🐾"*로 전면 교체.
3. **히어로 2단 제품 쇼케이스 & 3초 신뢰 뱃지**: 첫 화면(`#hero`) 우측에 실물 제품 이미지(`/images/bottle_front.png`)와 3대 플로팅 캡슐(`🌿 체내 흡수 0% 천연 미네랄`, `💧 주사기 스트레스 ZERO`, `🛡️ 생후 30일 아기 동물 안심`) 및 `Day 1 (응급) ➔ Day 3 (맘마 완식!) ➔ Day 7 (우다다 퇴원!)` 요약 바 배치.
4. **반려동물·브리더 중심 리얼 후기(`#testimonials`)**: 기존 송아지·양돈·한우 농가 후기를 **토이푸들 집사, 다묘 집사, 앵무새 꼬미 집사, 전문 브리더(켄넬), 펫샵 파트너, 하남 사랑동물병원 김동준 원장 임상 총평** 6종으로 전면 개편.
5. **학술 데이터 아코디언 슬림화(`ClinicalEvidence.jsx`)**: 상단에는 `98.5% 독소 포획`, `pH 4.5~5.5 위산 완충`, `≥800 m²/g 나노 표면적` 3초 인포그래픽만 노출하고, 복잡한 입자도·가축 5대 바이러스 표는 아코디언 토글(`[🔬 수의학·브리더용 상세 학술 비교표 펼쳐보기 ▼]`)로 접어 가독성 극대화.

### ③ 개인정보(PII) 보안 조치 및 프론트엔드 번들 최적화
- `public/assets/clean_87_orders.json`, `orders_cleaned.json`, `cleaned_batch_input.tsv` 삭제 및 `src/data/sampleRecipients.json` 내 상세 주소 제거·실명/연락처 마스킹 완료.
- `sampleCheck.js`, `businessVerification.js` 동적 `import()` 지연 로딩으로 초기 엔트리 JS 번들 크기를 **457.20 kB ➔ 237.68 kB (-48%)**로 경량화.
- `window.scrollY` 연속 상태 갱신을 boolean `isScrolled`로 교체해 스크롤 리렌더링 병목 제거.

---

## 2. 마케팅 컨텐츠 생성 및 자동 배포 파이프라인 리뷰 & 개선안

### 🔍 현황 진단 (Audit Findings)
1. **이원화된 파이프라인 구조**:
   - `marketing_factory/` (Python 8채널 오케스트레이터: `core/marketing_master.py`, `content_enricher.py`, `content_formatter.py`, `video_maker.py`, `viral_shortform_engine.py`, `outsource_dispatcher.py`, `adapters/`)
   - `scripts/marketing/` (`parvogel_content_generator.cjs`, `parvogel_marketing_master.py`) 및 `scripts/` 루트 내 110여 개 단발성 스크립트 혼재.
2. **GitHub Actions (`.github/workflows/marketing-factory.yml`) 실행 오류 요인 해결 완료**:
   - 기존 `python-version: "3.14"` (미지원/불안정 버전) ➔ `"3.12"`로 수정.
   - `openai` 패키지 및 리눅스 한글 폰트(`fonts-noto-cjk`, FFmpeg 9:16 쇼츠 자막 렌더링 필수) 누락 ➔ 워크플로우 설치 단계에 추가 완료.
   - `marketing_factory/adapters/naver_blog_adapter.py`, `brand_isolation_registry.json`, `queue_server.py`, `keywords_seo.json` 내 남아 있던 `몬스멕타` 키워드 전량 제거 완료.
3. **채널별 자동 발행 병목 지점**:
   - **Naver Blog (`naver_blog_adapter.py`)**: Playwright `headless=False` 및 로컬 크롬 프로필(`marketing_factory/data/naver_user_profile`, gitignore 처리됨)에 의존하므로 GitHub Actions 클라우드 러너에서는 항상 `SKIPPED_NO_KEY` 처리됨. (로컬 PC 스케줄러 또는 `queue_server.py` + 크롬 확장 프로그램 브릿지로만 작동)
   - **Instagram Reels / Facebook Page (`channels_config.json`)**: 과거 100Bagger 계정 오발송 방지를 위해 현재 `enabled: false`, `publish_mode: "off"`로 꺼져 있음.

### 🚀 단계별 파이프라인 고도화 개선안
1. **1단계 (컨텐츠 타깃 정렬 — 2040 D2C 집사 & 브리더 투트랙화)**:
   - `marketing_factory/data/daily_calendar.json`의 요일별 테마를 리뉴얼된 홈페이지 톤에 맞춰 **[월/수/금: 2040 강아지·고양이 집사 공감(새벽 구토·설사, 주사기 전쟁 해방)]**, **[화/목: 앵무새·소동물 응급 케어]**, **[토/일: 펫샵·브리더 이유기 설사 방어 & 1병 무료샘플 유도]**로 재편.
2. **2단계 (네이버 블로그 발행 자동화 안정화 — 하이브리드 큐 전환)**:
   - GitHub Actions에서는 블로그 원고(`drafts/Naver_Blog_*.md`)와 `marketing_queue.json` 적재까지만 수행하고, 로컬 PC 시작프로그램(또는 Windows 작업 스케줄러)에서 하루 1회 `naver_blog_adapter.py`가 큐를 폴링해 발행하도록 역할을 분리하면 클라우드 세션 만료/캡차 문제를 100% 우회 가능.
3. **3단계 (파보겔 전용 인스타그램 비즈니스 계정 연결 및 Reels 자동 업로드 재가동)**:
   - 파보겔 전용 Instagram 비즈니스 계정 생성 후 `META_IG_ACCOUNT_ID`와 영구 시스템 토큰(`META_ACCESS_TOKEN`)을 교체하면, 이미 구현된 `InstagramAdapter`의 Resumable Upload 엔진으로 매일 9:16 릴스 자동 업로드 즉시 가동 가능.
4. **4단계 (펫샵·브리더 B2B 알리고 문자 퍼널 자동화)**:
   - `scripts/`에 흩어진 40여 개 알리고 문자 발송 스크립트를 `marketing_factory/adapters/aligo_b2b_adapter.py` 하나로 통합하고, 신규 샘플 신청자 발생 시 **[D+0 발송 안내 ➔ D+3 급여 팁 & 기호성 확인 ➔ D+7 도매 전환 특가 안내 (`parvogel.kr/?sample=b2b`)]** 3단계 드립 캠페인을 자동화.


---

## 5. 마케팅 자동화 파이프라인 4대 개선안 구현 완료 (`51b2281`)
- **요일별 2040 D2C & 펫샵·브리더 B2B 멀티 페르소나 확장**:
  - `marketing_factory/data/daily_calendar.json`, `marketing_factory/core/content_enricher.py`, `marketing_factory/core/content_formatter.py` 업그레이드 완료.
  - 월(강아지 새벽 응급) · 화(고양이 스트레스 제로 1초 펌프) · 수(앵무새·특수조류 24h 기력 회복) · 목(55일령 푸들 7일 다큐) · 금(인허가 펫샵·브리더 1병 무료샘플 & VIP 도매) · 토(3일 차 폭풍 먹방) · 일(야간 응급실 30만원 vs 상비키트 3만원 비교) 7일 자동 순환 및 `?sample=petshop`, `?sample=b2b` UTM 자동 주입.
- **클라우드-로컬 하이브리드 네이버 블로그 큐 브릿지**:
  - `marketing_factory/core/marketing_master.py`에서 CI 환경(`GITHUB_ACTIONS=true`) 또는 로컬 크롬 세션 부재 시 `SKIPPED_NO_KEY` 대신 `marketing_queue.json`에 `QUEUED_HYBRID` 상태로 자동 적재.
  - `marketing_factory/run_local_naver_worker.py` 신설 (`python marketing_factory/run_local_naver_worker.py` 실행 시 대기 큐 원고를 로컬 크롬 세션으로 즉시 발행).
- **알리고 B2B 3단계 드립 퍼널 어댑터 (`marketing_factory/adapters/aligo_b2b_adapter.py`)**:
  - `D0_SAMPLE_INVITE` (`?sample=petshop`), `D3_FEEDING_TIP` (`#order`), `D7_VIP_WHOLESALE` (`?sample=b2b`) 3단계 템플릿 및 환경변수 기반 인증·`testmode=True` 안전 가드 내장.
- **로컬 보안 클린업**:
  - `scripts/sa_key_temp.json` 영구 삭제 및 `.gitignore` 보호 확인 완료.
