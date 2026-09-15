# Obsidian Log — 2026-09-14

## 파보겔 홈페이지 17개선 완료 (parvogel.kr)

### 요약
- 즉시 3가지 + 17개 전 항목 순차 개선, `vite build` 검증 완료
- 번들 516kB → 209kB + vendor 197kB 분리 (gzip 156k→63k)
- 비디오 lazy/poster 적용, BrowserRouter/sitemap/robots 구축, CTA 7→2개 계층화, FAQ/SEO 구조화데이터 확장

### 상세
- [[parvogel-landing/2026-09-14_파보겔_홈페이지_17개선_완료]]
- GitHub: hongsoonil02-maker/parvogel (master)
- 빌드: `src/App.jsx`, `vite.config.js`, `src/components/SEO.jsx` 등 13파일 변경
- 문서: `agrolib/parvogel-landing/2026-09-14_파보겔_홈페이지_17개선_완료.md`

### 커밋
- `feat: 17 improvements — video poster/manualChunks/BrowserRouter + SEO/CRO/신뢰성/A11y`

## [2026-09-14 08:17:00] 파보겔 규격 수정 (50ml -> 500ml)
- index.html 및 hospital-config.js 내 파보겔 표기를 500ml 대용량 겔로 수정 완료.

- [2026-09-14 21:45:10] parvogel_landing: muse spark 1.2 개선안(W-1~W-7, C-1~C-6) 종합 코드 리뷰 수행 및 Apps Script 폴백 누락·CSP 리다이렉트 등 잠재 장애 요인 도출.

- [2026-09-14 21:51:18] parvogel_landing: Apps Script 폴백 URL 복구, CSP connect-src 리다이렉트 보완, 404 SPA 리다이렉트 핸들러 추가 및 A11y 번역 키 복원 완료 (commit: 6e3acde).

- **2026-09-15 09:59:13**: 블랙 앤 화이트(문수미 대표, 광주 서구 봉학길 38) 113번 주문 및 쿠팡 2병 유료 주문 확인 등록 완료, 우체국택배 113건 접수 파일 및 맞춤 A4 알림판(HTML, PDF, PNG) 제작 완료

- **2026-09-15 10:04:08**: 구글시트 샘플 신청(sample_petshop) 연동 실전 테스트 성공(HTTP 200/success 확인), 어제 커밋 히스토리 감사 및 Apps Script URL 폴백/HashRouter/CSP 정합성 최종 점검 완료

- [2026-09-15 10:23:23] vet_animal_hospital: 일반 동물병원 타겟에서 진단키트 제외, 몬스멕타 처방 의약품 단일화 비즈니스 모델 정렬

- [2026-09-15 10:31:49] vet_animal_hospital: 5대 에이전트 토너먼트 배틀 완료 — 모바일 1분 사전 문진표, 진료실 A4 차트 요약 인쇄, 카운터 A4 포스터 및 몬스멕타 파트너 무상 키트 간편 신청 폼 구현 완료 (commit: d1445d5)
- [2026-09-15 10:36:12] vet_animal_hospital: GitHub 원격 저장소 (hongsoonil02-maker/vet-animal-hospital.git) main 브랜치 푸시 완료 (commit: d1445d5)
- [2026-09-15 10:46:31] snj_animal_hospital: 오르카 5-Agent 토너먼트 챔피언 에디션 배포 완료 (VETAZE 3.0 스텝 트리아지, 파보겔 500ml 3D 쇼케이스, B2B 패키지 카트, 임상 SOAP 차트 연동) -> GitHub push (commit: e20e184)

- **2026-09-15 14:47:10**: 구글시트 샘플 신청(sample_petshop) 연동 실전 테스트 성공(HTTP 200/success 확인), 어제 커밋 히스토리 감사 및 Apps Script URL 폴백/HashRouter/CSP 정합성 최종 점검 완료

- **2026-09-15 14:47:20**: 회사 홍대표 직통(전화/문자) 114번 베프경매장(황상필 대표) 신규 샘플 주문 DB 전체 동기화, 구글 시트 웹앱 API 실시간 등록(success), 우체국택배 114건 접수용 엑셀 및 맞춤형 A4 알림판(HTML/PDF/PNG) 생성 완료

- **2026-09-15 16:19:02**: 회사 홍대표 직통(이미지/문자) 115번 우포켄넬(서유석 대표) 신규 샘플 주문 DB 전체 동기화, 구글 시트 웹앱 API 실시간 등록(success), 우체국택배 115건 접수용 엑셀 및 맞춤형 A4 알림판(HTML/PDF/PNG) 생성 완료
