# S&J 동물병원 홈페이지 리뷰 및 개선 작업 — 2026-09-14

- **작업일자**: 2026-09-14
- **대상 리포지토리**: `hongsoonil02-maker/snj-animal-hospital` (main, `snj-vet.com`)
- **로컬 경로**: `C:\Users\master\snj_animal_hospital`
- **담당**: Muse Spark (opencode) — 사용자 요청: "홈페이지 리뷰해서 개선해줘" → "잔여권장사항도 개선해줘" → "깃허브 커밋/푸시" → "옵시디언/ agrolib 저장"
- **옵시디언 볼트**: `C:\Users\master\agrolib` (`.obsidian` vault, GitHub `agrolib`)

---

## 1. 초기 리뷰 요약 (Before)

### 발견된 주요 이슈
- **버그**: `index.html:315,338,391`에서 `openOrderModal()` 호출하나 `app.js`에 정의 없음 → B2B 발주 버튼 무동작 (partner.js에만 존재)
- **SEO 불일치**: `canonical`은 `github.io`, `og:url`/`sitemap`은 `snj-vet.com` — 검색엔진 중복 판단 위험
- **성능**: `Noto Sans KR 300-900 7웨이트` 전체 로드, `parvogel_product.png` `loading` 미지정, `sj_logo.png 858KB 720x720`, 스크립트 `defer` 없음
- **UX/a11y**: `style.css:1229` `.mobile-bottom-bar` CSS만 존재하고 HTML 없음, `textarea` `maxlength`/`aria-describedby` 없음, `service-card` `div role=button`이나 키보드 접근 보완 필요, 의료 면책 약함
- **신뢰/컴플라이언스**: `100여 개 파트너사` 수치 표시는 표시광고법 실증 대상, `og:image`가 QR(CTR 저하), `orderEndpoint=""` 시 레이스 조건(`confirm→tel→sms→share`)

---

## 2. 1차 개선 커밋 (이전 세션 요약)

- `app.js:211` `openOrderModal()` 추가
- `index.html:7-27` SEO 통합: canonical → `snj-vet.com`, `keywords/author/theme-color/robots`, JSON-LD `postalCode/description/availableService` 보강
- `index.html:57` 폰트 `400/700/800`으로 경량화, `index.html:373` 이미지 `lazy/width/height`, `defer` 추가, `sitemap lastmod 2026-09-14`
- `index.html:964` 하단 고정바 추가, `index.html:163` triage `maxlength 500 + Ctrl+Enter`, 면책 강조, 푸터 `tel:` 링크
- `partner.html:14` 폰트 동일 경량화

## 3. 잔여 권장 3건 개선 (금일 핵심)

### 3.1 OG 이미지 QR → 1200x630 전용 이미지
- **파일 생성**: `og-image.png` (1200x630, 216KB PNG optimize) + `og-image.webp` (27KB, quality 85) — `Pillow`로 흰 배경 중앙 480px 로고 합성 (`sj_logo.png 720x720 RGBA` 기반)
- **메타 교체**: `index.html:15-27` `og:image` `snj_qr_branded.png` → `og-image.png`, `width 1200 height 630 alt/type` 추가, `twitter:card summary→summary_large_image`, JSON-LD `image`도 `og-image.png`로 통일, `hospital-config.js:29` `ogImage` 필드 추가

### 3.2 "100여 개" 표시광고법 완화
- `index.html:294-304` `100여 개 파트너사를 위한` → `협력 네트워크를 위한`, 각주 추가: `* 협력 네트워크 규모는 경매장 운영 현황에 따라 변동될 수 있으며, 특정 수치를 보장하지 않습니다.`
- `partner.html:44-51` 배지/본문 동일 완화 + 각주 추가

### 3.3 `orderEndpoint` 완전 폴백 + 가이드
- `hospital-config.js:30` 주석에 `order-endpoint-example.gs` 참조 및 가이드 URL 명시, `orderEndpoint=""`여도 로컬 저장+클립보드+전화/문자로 완전 동작 명시
- **신규 파일**: `order-endpoint-example.gs` — GAS `doPost` (시트 append + 선택 이메일) + `doGet` 헬스체크, `YOUR_SHEET_ID_HERE` 교체 후 배포하면 `orderEndpoint`에 URL 입력 즉시 연동
- **로직 재작성**: `app.js:210-272` `handlePreOrderSubmit`을 `localStorage 20건→clipboard→fetch(선택)→showOrderSuccess` Promise 체인으로 재구성, 레이스 제거. `index.html:905` `#orderSuccessModal` 신규 모달 (복사본 `pre`, 상태 배지 `server-ok/fail/local`, 전화/문자/공유 버튼, 가이드 링크). `partner.js:82` 동일 안정화 (partner는 별도 성공 모달 없이 배지+confirm 폴백).

---

## 4. 커밋 및 푸시

- **커밋**: `151b0ea feat(seo,ux,compliance): improve homepage & B2B portal` (2026-09-14 08:28 KST)
  ```
  app.js                    | 116 ++++++++++++++++++++++++++--------------------
   hospital-config.js        |   8 +++-
   index.html                |  93 ++++++++++++++++++++++++++++---------
   og-image.png              | Bin 0 -> 216056 bytes
   og-image.webp             | Bin 0 -> 26944 bytes
   order-endpoint-example.gs |  28 +++++++++++
   partner.html              |   5 +-
   partner.js                |  38 ++++++++-------
   sitemap.xml               |   5 +-
   9 files changed, 199 insertions(+), 94 deletions(-)
  ```
- **푸시**: `a7324e9..151b0ea main -> origin/main` → `https://github.com/hongsoonil02-maker/snj-animal-hospital.git` `push ok`
- **이전 커밋**: `a7324e9 feat(ui/triage): upgrade to Vetaze AI 2.0 triage engine...`

---

## 5. 검증

- `node -c app.js/partner.js/hospital-config.js` Syntax OK
- `index.html`에 `og-image.png`, `1200x630`, `협력 네트워크`, `orderSuccessModal`, `order-endpoint-example` 모두 포함 확인
- `partner.html` `100여 개` 제거 확인, `hospital-config.js` `ogImage` 존재, 생성 파일 `og-image.png/webp`, `order-endpoint-example.gs` 존재 확인

---

## 6. 남은 권장 (선택)

- `sj_logo.png 858KB` 원본은 TinyPNG/cwebp로 추가 압축 권장 (이미 OG는 최적화됨, 원본 로고도 200KB 이하 권장)
- `sitemap.xml`에 `partner.html` 미포함 유지 (noindex 정책)
- Cloudflare `/_headers` 또는 `wrangler`로 OG 캐시 (`Cache-Control: public, max-age=86400`) 설정 고려

---

*본 문서는 옵시디언 볼트 `agrolib` 및 GitHub `agrolib` Wiki에 동시 저장됨. 원본 작업 산출물은 `snj-animal-hospital` 리포지토리 커밋 `151b0ea`에 귀속.*
