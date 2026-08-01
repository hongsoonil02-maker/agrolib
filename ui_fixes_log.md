# 랜딩페이지 UI 및 번역 수정 로그 (2026-07-27)

- **작업 내용**: 
  1. 수량 선택 부분의 번역 키 오류(`clinical.chart_monsmecta`)를 `order.product_name`으로 교체하여 정상적으로 "몬스멕타"로 출력되도록 수정.
  2. 하단 고정 알림 박스(`StickyBottomCTA`)의 색상을 파란색/남색 계열에서 전체 테마에 맞는 딥그린/옐로우/에메랄드 색상으로 변경.
  3. 하단 고정 박스가 푸터 글자를 가리는 현상을 수정하기 위해 `Footer` 컴포넌트 하단 여백(`pb-24 md:pb-32`) 대폭 추가.
- **수정 파일**:
  - `src/components/OrderForm.jsx`
  - `src/components/StickyBottomCTA.jsx`
  - `src/components/Footer.jsx`
- **GitHub 반영**: `git commit -m "Fix UI: translation key for quantity & update StickyBottomCTA colors"` 후 `git push` 완료
