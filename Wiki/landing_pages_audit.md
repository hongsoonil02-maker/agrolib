# 📋 4대 동물약품 랜딩페이지 통합 오디트 & 전사 개선 보고서 (landing_pages_audit.md)

- **작성 일자**: 2026-07-26
- **주관 에이전트**: Master Enterprise Orchestrator (안그래 - Agent 16)
- **참여 군단**: Agent 02 (UI/UX), Agent 07 (Performance), Agent 08 (Code & SEO Auditor), Agent 15 (Content & Conversion Ingestor)
- **대상 프로젝트**: `rotagal-landing`, `vetacol-landing`, `monsmecta-landing`, `parvogel_landing`

---

## 🏢 프로젝트별 개선 및 통합 내역 Summary

| 프로젝트명 | 대표 제품 | 핵심 타겟 | 주요 통합 개선 기능 | SEO & 성능 조치 |
|---|---|---|---|---|
| **`rotagal-landing`** | 로타갈 (Rotagal) | 한우/젖소 번식우 농가 | 어미소 분만전 1회 접종 적기 계산기 (Vaccine Calculator), 모바일 스티키 CTA | JSON-LD Product Schema 전화/구매 연결 보완, 미사용 자원 정리 |
| **`vetacol-landing`** | 베타콜 (Vetacol) | 송아지 사육 농가, 대동물병원 | 출생 직후 3시간 초유 면역 골든타임 타이머 (GoldenTime Timer), 스티키 CTA | 100MB+ 주소록/DB 파일 `.gitignore` 격리, theme-color 최적화 |
| **`monsmecta-landing`** | 몬스멕타 (Monsmecta) | 전국 수의사 원장, 동물병원 | 수의사 전용 무료 샘플/독점 공급 신청 모달 (VetSample Modal), 자문단 카러셀 | `og:image` 상대 경로 -> Absolute URL 정상화, 스크립트 빌드 정리 |
| **`parvogel_landing`** | 파보겔 (Parvogel) | 축산농가 (소·돼지·염소·양·말) | 87KB `App.jsx` 5대 모듈 리팩토링, 축종별 맞춤 효능 탭 (Animal Selector), 음성 후기 위젯 | Pretendard 폰트 최적화, Canonical 및 OpenGraph 절대 경로 교정 |

---

## 🔒 5-Filter System 검증 결과

1. **Filter 1 (재사용성)**: 모바일 반응형 Sticky Bottom CTA 컴포넌트 및 Vaccine Calculator, Sample Modal 등 4개 랜딩 공통 재사용 모듈 구축.
2. **Filter 2 (가독성)**: 복잡한 87KB 파보겔 싱글 코드를 독립된 React 컴포넌트로 구조화하여 코드 읽기 편의성 대폭 증대.
3. **Filter 3 (근거 명확성)**: 각 제품별 임상 데이터, 수의사 자문 멘트 및 제품 스펙 수치 유지 및 시각적 부각.
4. **Filter 4 (결론 요약성)**: 농가 및 수의사의 구매 전환을 유도하는 3대 핵심 액션(전화상담/샘플신청/온라인구매)을 모바일 화면에 고정.
5. **Filter 5 (불변성 검증)**: 원본 데이터 및 제품 효능 정보 100% 보존.

---
*본 보고서는 ORCA IDE 16-Agent Army Directive에 따라 자동으로 관리되는 중앙 볼트 문서입니다.*
