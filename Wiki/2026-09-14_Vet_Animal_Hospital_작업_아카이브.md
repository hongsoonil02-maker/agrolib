# Vet Animal Hospital (vet_animal_hospital) 작업 아카이브 — 2026-09-14

- **작업일자**: 2026-09-06 ~ 2026-09-14
- **로컬 폴더**: `C:\Users\master\vet_animal_hospital`
- **GitHub 리포지토리**: `hongsoonil02-maker/vet-animal-hospital` (public) — `https://github.com/hongsoonil02-maker/vet-animal-hospital`
- **옵시디언 볼트**: `C:\Users\master\agrolib` (`.obsidian` vault, 동일 GitHub `agrolib` Wiki에 이중 보관)
- **프로젝트 성격**: VetLink AI — 전국 5,000개 동물병원용 SaaS 포털 스캐폴드 (Vite + Cloudflare Pages + 로컬 QR)

---

## 1. 리포지토리 개요

- **현재 버전**: `2.5.0` (`package.json:2`)
- **스택**: Vanilla HTML/CSS/JS + Vite 5.4 + Wrangler 3.80 + `qrcode 1.5.4` (로컬 생성)
- **빌드**: `npm run build → vite build && node scripts/copy-static.mjs → dist/` → `wrangler pages deploy dist`
- **배포 대상**: `vet-animal-hospital.net` (Cloudflare Pages, `wrangler.jsonc: pages_build_output_dir: ./dist`, `compatibility_date: 2025-12-01`)
- **브랜치**: `main` — 5 commits, clean working tree (2026-09-14 기준)

### 디렉터리 구조 (실제)
```
index.html                # 랜딩 + Studio + Simulator
hospital.html             # ?hospital= 테넌트 렌더러
privacy.html / terms.html # 법무 필수
config/
  hospital.schema.json    # JSON Schema (hospitalId 패턴, theme enum 등)
  examples/*.json         # happy-animal, seoul-central, busan-pet
assets/
  css/style.css
  js/app.js
  js/hospital-config.js   # 마스터 컨피그 (쿼리 hospital= 라우팅)
  js/hospital-data.js     # 단일 소스 중앙화 (v2.5 신규)
  js/tenant.js            # 테넌트 동적 렌더
  img/og-vetlink.png (31KB, 1200x630), favicon-512.png (11KB), favicon.svg
public/_headers, _redirects, sitemap.xml, robots.txt
scripts/copy-static.mjs
dist/ (빌드 산출, 90 modules)
```

---

## 2. Git 전체 이력 (요약)

| 커밋 | 일자 | 메시지 및 핵심 |
|------|------|---------------|
| `f6b80ac` | 2026-09-06 | `feat: initial release of vet-animal-hospital.net standard enterprise platform` — 엔터프라이즈 표준 플랫폼 초판 |
| `59d5f30` | 2026-09-06 | `feat: SaaS scaffold v2.4 - config/hospital.schema + tenant portal + a11y/mobile + legal/SEO infra` — SaaS 스캐폴드, 스키마·테넌트·a11y·법무·SEO 인프라 일괄 |
| `4d3e85b` | 2026-09-06 | `fix: wrangler pages_build_output_dir for Pages deploy` — `wrangler.jsonc` Pages 경로 수정 |
| `42375f8` | 2026-09-06 | `feat: reposition to Monsmecta partner kit - free ops kit (was SaaS sales)` — 타이틀/메타/OG를 SaaS 판매→몬스멕타 파트너 무상 운영키트로 리포지셔닝, `index.html 91줄` 수정 (유료 50/25 제거, 정규 공급 파트너 무료 1키트) |
| `239e677` | 2026-09-14 | `feat: harden vet portal v2.5 - local QR, CSP/HSTS, OG, sitemap, tenant DRY, triage fix` — 금번 하드닝 (18 files, 512 insertions) |

### 최신 커밋 상세 (`239e677`, 2026-09-14 08:09)
- **build**: `type=module` 번들링 (90 modules), 중복 css/js 복사 제거 (`scripts/copy-static.mjs:2` 수정)
- **security**: 로컬 `qrcode` 모듈로 교체 (`api.qrserver.com` 외부 유출 제거), `public/_headers` CSP 강화 (HSTS `max-age=63072000`, `frame-ancestors none`, `object-src none`, `Cross-Origin-*`)
- **seo**: 실제 1200x630 OG 이미지 `assets/img/og-vetlink.png` (31KB) + `public/favicon.png` (1KB), `sitemap.xml` 쿼리 파라미터 제거, `/h/*` redirects (`public/_redirects: /h/* → /hospital.html?hospital=:splat 200`), `hospital.html` OG/JSON-LD + `tenant.js` 동적 업데이트
- **legal**: `terms.html:3` 몬스멕타 무상 파트너 키트 약관으로 정렬
- **config**: `wrangler.jsonc` `compat 2025-12-01`/`deprecated type` 제거, `hospital-data.js` 단일 소스 중앙화 + `async fetch` 폴백 + 404 처리
- **ux**: `app.js:74` triage 중복 수정, 공백 보존 normalize, `alert` → `inline role=alert`

---

## 3. 핵심 컨피그 예시

### `config/examples/happy-animal.json`
```json
{
  "hospitalId": "happy-animal",
  "name": "행복동물병원",
  "city": "서울 강남구",
  "address": "서울 강남구 테헤란로123",
  "phone": "02-1234-5678",
  "theme": "teal",
  "specialty": "외과 수술 & 소화기내과",
  "businessHours": "평일 09:30 ~ 18:30 / 토 09:30 ~ 15:00 / 일·공휴일 휴진",
  "monsmectaPartner": false,
  "features": { "triage": true, "summaryPdf": true, "counterPoster": true, "qrPortal": true }
}
```

### `config/hospital.schema.json` (발췌)
- `hospitalId: ^[a-z0-9-]{3,32}$`, `phone: ^0[0-9]{1,2}-[0-9]{3,4}-[0-9]{4}$`, `theme: teal|navy|emerald`, `emonsmectaPartner boolean`

### `public/_headers` (보안)
```
X-Frame-Options: DENY
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; img-src 'self' data:; ...
```

### `public/_redirects`
```
/h/*  /hospital.html?hospital=:splat  200
```

---

## 4. 빌드/배포 명령

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # dist/ 생성 (vite + copy-static.mjs)
npm run preview  # :4173
npx wrangler pages deploy dist --project-name=vet-animal-hospital
# 커스텀 도메인 vet-animal-hospital.net은 Cloudflare Pages > Custom domain 연결
```

- **테넌트 추가 (30초)**: `config/examples/my-hospital.json` 복사 → `hospitalId/name/phone/theme` 수정 → `?hospital=my-hospital` 로 미리보기 → `hospital-config.js` 치환 또는 `fetch('/config/examples/my-hospital.json')` 로드

---

## 5. 법무/라이선스 메모

- AI 트리아지는 **의학적 진단 대체 불가** — 모든 페이지 하단 disclaimer + 모달 + footer 면책 포함
- `privacy.html`/`terms.html` 필수, 보호자 입력은 메모리선 처리 (서버 저장 없음, 로컬 QR)
- 몬스멕타 파트너 키트: 공급 중단 시 소유권 병원에 귀속 (42375f8 reposition 반영)

---

## 6. 보관 정보

- **원본 폴더 전체 유지**: `C:\Users\master\vet_animal_hospital` (node_modules 제외 60+ 파일, `dist` 빌드 포함)
- **GitHub**: `hongsoonil02-maker/vet-animal-hospital` 최신 `239e677` (main, clean)
- **본 문서**: 옵시디언 볼트 `agrolib/Wiki/2026-09-14_Vet_Animal_Hospital_작업_아카이브.md` 및 GitHub `agrolib` Wiki에 이중 커밋 (다음 커밋에서 push)
- **관련 S&J 보관**: `2026-09-14_SnJ_Animal_Hospital_개선_작업.md` 동일 Wiki에 병행 보관 — 두 프로젝트는 봄봄솔루션/몬스멕타/파보겔 생태계로 연계

---

*아카이브 생성일 2026-09-14, 원본 커밋 해시 및 파일 트리 기준 스냅샷. 추가 변경 시 본 문서 갱신 필요.*
