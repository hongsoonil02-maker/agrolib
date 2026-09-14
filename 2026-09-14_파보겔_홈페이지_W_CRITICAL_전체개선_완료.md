# 파보겔 홈페이지 W-1~W-7 & C-1~C-6 전체 개선 완료 (2026-09-14)

> parvogel_landing `70947ab` → GitHub `hongsoonil02-maker/parvogel` master 푸시 완료, 빌드 189MB / lint 통과

## 요약
- **W-1 i18n** 15개 로케일 hreflang/x-default, 가격 30k/75k 통일, virusTableTitle 로케일별 번역, missingKeyHandler DEV 추가
- **W-2 SEO** VideoObject embedUrl, BreadcrumbList, og:image:alt/author/twitter:alt, sitemap lastmod/image/hreflang + blog 3개 URL
- **W-3 A11y** 로고 Space, AudioTestimonial aria-valuetext/Home/End, 모달 포커스 트랩/복귀, RTL 논리속성(-end/-start)
- **W-4 성능** IntersectionObserver activeSection, requestAnimationFrame scrollY, 문자열 메모이제이션
- **W-5 폼** 전화 01 정규식·사업자 10자리·이메일·수량 1~100 검증, inputMode/pattern/step
- **W-6 최적화** Pretendard preconnect/dns-prefetch+swap, QrCode L→M, width/height CLS 방지
- **W-7 보안** _headers(CSP/HSTS/X-Frame 등), referrerPolicy, .env.example 보완
- **C-1** 하드코딩 폴백 제거(env 필수), 파트너 URL env 단일화
- **C-2** Apps Script 입력검증·CSV인젝션·allowlist·길이제한·MailApp quota 가드·doOptions
- **C-3** 히어로 11MB 비디오 IntersectionObserver 지연 로드 + poster 버튼
- **C-4** public/assets 572→189MB(미참조 24개 mp4 → raw_source_videos/archive), 잔여 10개(초대형 2개는 R2 분리 권장)
- **C-5** 파트너 코드 엄격 allowlist, no-cors 제거 및 전화 정규화·응답 검증
- **C-6** FeedDisclaimer 컴포넌트 신설 및 히어로/다큐 후 배치, copyC “기적→보조사료 사례*” 완화

## 변경 파일 (44 files, +629/-455)
- `src/components/SEO.jsx`, `src/i18n.js`, `src/pages/Landing.jsx`, `src/components/{AudioTestimonial,OrderForm,PartnerNoticeModal,ParvogelClinicalDocumentary,QrCode,StickyBottomCTA,FeedDisclaimer}`, `src/locales/*/translation.json`, `index.html`, `public/sitemap.xml`, `public/_headers`, `google_apps_script.gs`, `.env.example`
- 삭제: `public/assets/Video Project 6_reviced.mp4`, `parvogel_case_03_recovery.mp4` 등 14개 LFS mp4

## 검증
- `npm run build` → 189.43MB, `npm run lint` 통과
- `vite.config.js` base '/', HashRouter 유지, dist/_headers 적용

## 다음 권장
- 초대형 2개(`parvogel_clinical_documentary_v2 42.8MB`, `김동준원장_동영상 6-1 38.5MB`)를 Cloudflare R2/YouTube로 외부 호스팅 후 코드 URL 교체
- `sharp`로 bottle 이미지 WebP/AVIF 생성 및 원본 압축

---
*자동 생성: parvogel_landing 작업 로그 — Obsidian Vault(agrolib) 저장*
