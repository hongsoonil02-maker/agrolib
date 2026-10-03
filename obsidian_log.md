# Obsidian Log — 2026-10-02

## 업비트 듀얼 퀀트 엔진 구축 및 200일 백테스트 최적화 적용

### 요약
- KIS 한국주식 및 OKX 퀀트 엔진 로직을 업비트(Upbit) 현물로 완벽 복제 이식.
- 메이저 트렌드 봇(`upbit_trend_trader`) + 알트 벤처 스나이퍼 봇(`upbit_venture_trader`) 듀얼 엔진 구조 구축.
- 자금 변동(20만 원 → 155만 원)에 맞춘 포지션 사이징(메이저 25%, 벤처 15%) 및 캡 리밸런싱.
- 200일 백테스트 그리드 서치를 통해 1위 파라미터 도출: 돈키언 10일, ATR 3.0x, 손절 10%, RSI 50~75 필터 (수익률 +19.06%, MDD -3.87%, 승률 61.9%, 손익비 3.63) 실가동 반영 완료.
- 상세 문서: [[2026-10-02_업비트_듀얼엔진_구축_및_200일_백테스트_최적화_적용]]

---

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

- [2026-09-18 19:06:00] 파보겔(Parvogel) SEO 타겟 확장: 반려조류(앵무새), 소동물(햄스터 웻테일), 특수동물(도롱뇽, 파충류) 키워드 및 안내문구 추가 배포 완료 (parvogel.kr 및 agrokorea.net).

- [2026-09-18 19:30:35] 3대 사이트(한국아그로 agrokorea.net, 파보겔 parvogel.kr, 몬스멕타 monsmecta.kr) 전 축종 및 모든 반려동물·특수동물(조류·햄스터·도롱뇽·양서파충류) 상세 UI 탭 및 안내문구 전면 보강 배포 완료.

- [2026-09-18 19:53:59] **파보겔(parvogel.kr) 메인 카피 및 세션 순서 CRO 최적화**: 히어로 메인 카피를 전 동물 포용형("다시 생생하게 기운 차려 품으로 안깁니다", "강아지·고양이는 물론 앵무새·소동물·송아지까지")으로 개선하고, 핵심 동물 선택기(AnimalSelector) 및 앵무새 후기(GomiPoopStory)를 첫 화면 직하단으로 상향 배치하여 라이브 배포 완료.

- [2026-09-18 20:23:45] **파보겔(parvogel.kr) 메인 카피 및 세션 순서 CRO 최적화**: 히어로 메인 카피를 전 동물 포용형("다시 생생하게 기운 차려 품으로 안깁니다", "강아지·고양이는 물론 앵무새·소동물·송아지까지")으로 개선하고, 핵심 동물 선택기(AnimalSelector) 및 앵무새 후기(GomiPoopStory)를 첫 화면 직하단으로 상향 배치하여 라이브 배포 완료.

- **2026-09-20 14:12** | [S-NACF 사료첨가제 제안 실무 제작 완료] (주)삼원팜텍 단독 제조·판매원 기준 공식 제안서 Word 문서(.docx), 30장 프레젠테이션 덱(.pptx), 3분 43초 풀 나레이션 1080p 제안 영상(.mp4) 제작 및 C:\Users\master\S-project_files에 납품 완료.
[2026-09-20 14:35:58] S-NACF 한일사료 임가공 맞춤형 고농축 사료첨가제 제안 3대 산출물(PPTX 30장 덱, 1080p MP4 홍보영상, DOCX 제안서) 생동감 극대화 전면 고도화 완료. 21개 다이내믹 켄번스 샷+배경음악(BGM)+동기화 자막 탑재 영상(40.8MB) 및 실물 사진·표·3D 마스코트가 완벽 결합된 30슬라이드 덱(9.7MB) 납품 완료.
[2026-09-20 14:43:18] GitHub 원격 저장소(vet-animal-hospital)에 S-NACF 맞춤형 고농축 사료첨가제 제안 3대 산출물(커밋: 734590a) 푸시 완료. (Word 제안서, PPTX 30장 덱, 1080p MP4 풀모션 영상 및 에셋 소스코드 총 65개 파일 반영)
### [2026-09-20 14:58:33] S-Project: 100% 서울우유 낙농 특화 개편 및 돼지/한우/축협 전역 삭제
- 전역(C:\Users\master\S-project 마스터 문서, 코드베이스, Word 문서, PPTX 30장 덱, MP4 영상)에서 한우·비육우 및 돼지(양돈, 자돈, 비육돈, 모돈, PED) 관련 내용 및 에셋 완전 삭제 완료.
- 수요처를 '서울우유 (서울우유협동조합)'로 통일하고 착유우 산유량 방어, 체세포수 1등급 달성, 송아지 설사 80% 저감 등 100% 낙농 전문 처방으로 3대 산출물 최신본 동기화 완료.


- **[2026-09-20 15:14:55]** [S-Project] PPTX 30장 슬라이드 전역 레이아웃 개선 완료: 박스 내부 텍스트(11~17pt), 헤더 서브타이틀(13pt Bold), 핵심 키워드 볼드 하이라이트 및 카드 상하 여백 최적화로 공간 균형감 대폭 개선.

- **[2026-09-20 15:40:42]** [S-Project] 슬라이드(30장 덱) 및 홍보영상(MP4) 전역 개선 완료: 서울우유 브랜드 정체성에 맞춘 맑고 깨끗한 순백색(Pure Milk White) 및 시그니처 바이오 그린(#008B47) 테마 전면 적용, 다크 네이비 배경 제거, 카드 상단 그린 액센트 리본, 불릿 항목 한글 내어쓰기(Hanging Indent) 및 좌우 여백/줄맞춤 전면 최적화 완료.

- [2026-09-20 16:04:01] S-Project: 슬라이드 및 홍보영상 전역에서 젖소-돼지 마스코트 사진을 우유 마시는 아이(child drinking milk) 사진으로 전면 대체하고, 비디오 배경을 순백색 및 서울우유 그린(#008B47)으로 최적화 완료.

## [2026-09-21 19:11:51] 몬스멕타 네이버 검색 유입 대응 게이트웨이 및 수의사 비공개 락 구현
- 몬스멕타 검색자 대상 동물병원 내원 유치 및 동일 나노 포뮬러 파보겔(쿠팡/스토어) 즉시 구매 전환 게이트웨이(/monsmecta) 구축 완료.
- 수의사 전용 비공개 영역(공급 단가, 발주 시스템, 임상 프로토콜 락) 및 기존 홈페이지용 독립형 팝업 소스(monsmecta-popup-embed.html) 패키지 배포.


## [2026-09-21 19:21:23] 몬스멕타(monsmecta) 및 파보겔(parvogel) GitHub 배포 푸시 완료
- monsmecta 레포지토리(https://github.com/hongsoonil02-maker/monsmecta): 수의사 전용 비공개 락, 일반인 안내 팝업 및 파보겔 전환 배너 푸시 완료(커밋: b122290). GitHub Actions 배포 트리거.
- parvogel 레포지토리(https://github.com/hongsoonil02-maker/parvogel): 몬스멕타 게이트웨이(/monsmecta) 및 SEO 검색 연동 푸시 완료(커밋: 57cec3f).


## [2026-09-21 19:29:20] 몬스멕타 공급가 완전 비공개 락 긴급 조치 완료
- monsmecta(https://github.com/hongsoonil02-maker/monsmecta): 몬스멕타 헤파맥스, 레날디톡스 등 전 라인업 공급가 및 발주폼 단가 노출 완전 차단.
- '🔒 수의사 전용 비공개 (사업자 인증 후 적용)' 락 적용 완료 (커밋: cc497cc) 및 즉시 GitHub Actions 배포 푸시.


- [2026-09-22 10:01] GCP quant-nasdaq-only 원격 연결 불가 원인 진단 완료 및 SSH 접속 가이드 제공.

- [2026-09-22 10:07] SSH config 진단 완료: nasdaq/quant-nasdaq-only/coinbot 정상 접속 확인, oracle-new (144.24.65.250) 타임아웃 원인(인스턴스 전원/IP변경/보안목록) 분석.

- [2026-09-22 10:08] 오라클 서버 제외 확인. GCP (nasdaq, coinbot) 원격 SSH 접속 체계 최종 세팅 완료.

- [2026-09-22 10:20] Antigravity IDE Remote-SSH 연결 오류('SSH server closed unexpectedly') 진단 및 해결: 원격 서버(e2-micro) 부팅 지연 대비 extension.js 내 시작 대기 루프 시간(7.5초->60초) 확장 패치 및 원격 lock 정리 완료.

<<<<<<< HEAD
### [2026-09-22 19:26:04] ?뚮낫寃?異붿꽍 吏???좊Ъ(100ml) ?쒗겕由?肄붾뱶 ?몄쬆 ?좎껌 ?쒖뒪??援ъ텞
- ?ㅼ씠踰?寃?????덊럹?댁? ?좎엯 吏???쒖젙 ?뚮낫寃?100ml 1蹂?臾대즺 ?좊Ъ 紐⑤떖(ChuseokGiftModal) 媛쒕컻.
- ?쒗겕由?肄붾뱶('?щ쭪??00' ?? 寃利? 以묐났 ?좎껌 諛⑹?, ?ㅼ떆媛??쒖젙 ?섎웾 移댁슫??援ы쁽.
- ?곷떒 諛곕꼫, ?ㅻ뜑/紐⑤컮???ㅻ퉬寃뚯씠??踰꾪듉, ?섎떒 ?뚮줈????踰꾪듉 諛?Google Apps Script ?곕룞 ?꾨즺.
=======
## [2026-09-22] OKX 자동매매 Breakeven 스탑 수술, JEV Supreme 확립 및 PnL 원장 정밀 감사

### 요약
- 비트코인 상승장 속 손실 원인 규명: Breakeven Stop에 레버리지 ROE 오적용(-0.025% 미세 하락에도 조기 털림) 수술
- `spot_pnl_pct`(레버리지 제외 순수 가격 변동률) 분리 도입 및 ATR Stop 배수 2.5 → 3.5 확대
- JEV Supreme 아키텍처 확립: JEV AI가 매크로 레짐 및 ADX chop 게이트를 바이패스하고 최우선 1번 판단권 행사
- Health Circuit Breaker 해제 및 과거 손실 제외 베이스라인 갱신
- PnL 원장 감사: 이전 보고서의 +$9,496은 OKX 선물 스왑 계약 단위(ctVal=0.01) 미반영으로 인한 100배 과대계상 착시(실제 7일 순손익 -$228.67 USDT로 계좌 우하향과 100% 일치) 규명
- 불필요 캐시/PID/로그 정리 및 봇 3종 정상 가동 (현재 계좌 $10,687 USDT)
- 상세 문서: [[2026-09-22_OKX_자동매매_Breakeven스탑수술_및_PnL원장정밀감사]]

>>>>>>> cec133f2cb48393087c9d12c0e1f91290bf8b5be

### [2026-09-22 19:26:39] ?뚮낫寃?異붿꽍 吏???좊Ъ(100ml) ?쒗겕由?肄붾뱶 ?몄쬆 ?좎껌 ?쒖뒪??援ъ텞
- ?ㅼ씠踰?寃?????덊럹?댁? ?좎엯 吏???쒖젙 ?뚮낫寃?100ml 1蹂?臾대즺 ?좊Ъ 紐⑤떖(ChuseokGiftModal) 媛쒕컻.
- ?쒗겕由?肄붾뱶('?щ쭪??00' ?? 寃利? 以묐났 ?좎껌 諛⑹?, ?ㅼ떆媛??쒖젙 ?섎웾 移댁슫??援ы쁽.
- ?곷떒 諛곕꼫, ?ㅻ뜑/紐⑤컮???ㅻ퉬寃뚯씠??踰꾪듉, ?섎떒 ?뚮줈????踰꾪듉 諛?Google Apps Script ?곕룞 ?꾨즺.

### [2026-09-22 19:31:42] ?뚮낫寃?源껎뿀釉??몄떆 ?꾨즺 (Commit: 376d3a1)
- 異붿꽍 ?쒓???吏???쒖젙 100ml ?좊Ъ 紐⑤떖 諛??쒗겕由?珥덈?肄붾뱶 ?몄쬆 ?쒖뒪?쒖쓣 GitHub master 釉뚮옖移섏뿉 ?깃났?곸쑝濡?而ㅻ컠 諛??몄떆 ?꾨즺.

### [2026-09-22 19:44:16] ?뚮낫寃?諛?紐ъ뒪硫뺥? ?ㅻ뜑 ?곹샇 ?몄텧 ?곷떒諛??쒓굅 諛??명꽣 議곗떖?ㅻ윭??諛곗튂 ?꾨즺
- ?뚮낫寃?parvogel.kr) ?곷떒?먯꽌 寃???'?섏쓽??泥섎갑 ?꾩슜 紐ъ뒪硫뺥?' ?곷떒諛붾? ?쒓굅?섏뿬 釉뚮옖???뺤껜??諛?怨좉컼 ?쇱꽑 諛⑹?.
- 紐ъ뒪硫뺥?(monsmecta.kr) ?곷떒?먯꽌 '?뚮낫寃?荑좏뙜/?ㅻ쭏?몄뒪?좎뼱)' ?곷떒諛붾? ?쒓굅?섏뿬 ?섏쓽???꾩슜 ?꾩긽 沅뚯쐞 蹂댄샇.
- ?묒궗 紐⑤몢 ?섎떒 ?명꽣(Footer)??議곗슜?섍퀬 ?뺤쨷???⑤?由?留곹겕濡??щ같移??꾨즺. (parvogel: ac7d429 / monsmecta: b394a26)

### [2026-09-22 19:48:55] ?뚮낫寃?諛?紐ъ뒪硫뺥? ?명꽣?먯꽌???곹샇 留곹겕 ?꾩쟾 ??젣 諛?100% ?낅┰ 梨꾨꼸???꾨즺
- ?뚮낫寃?parvogel.kr)怨?紐ъ뒪硫뺥?(monsmecta.kr) 媛꾩쓽 ?명꽣 ?곹샇 留곹겕瑜??꾩쟾???쒓굅.
- ?섏쓽???꾩슜 ?꾩긽 ?쒖옱(紐ъ뒪硫뺥?)???꾨Ц?깃낵 泥섎갑 沅뚯쐞瑜??⑥쟾??蹂댄샇?섍퀬, 諛섎젮??????뚮낫寃?梨꾨꼸??100% ?낅┰ 遺꾨━.
- ?묒궗 Git 而ㅻ컠 諛??몄떆 ?꾨즺 (parvogel: 9de714e / monsmecta: bd595df)

### [2026-09-22 20:11:36] ?뚮낫寃?異붿꽍 吏??留덉???諛?釉뚮옖??遺꾨━ ?묒뾽 留덈Т由?- 異붿꽍 吏???쒖젙 ?뚮낫寃?100ml ?좊Ъ ?좎껌 紐⑤떖(ChuseokGiftModal) 諛??쒗겕由?珥덈?肄붾뱶 寃利??쒖뒪??援ы쁽 ?꾨즺.
- ?뚮낫寃?諛?紐ъ뒪硫뺥? ?ㅻ뜑/?명꽣 ?곹샇 留곹겕 ?꾩쟾 ?뺣━(100% ?낅┰ 梨꾨꼸?? 諛?GitHub ?몄떆 ?꾨즺.
- 諛쒖넚??異붿꽍 ?덈? 硫붿떆吏 移댄뵾??3醫??뺣퉬 ?꾨즺 (??쒕떂 ?대? ?쇱쓽 ?湲?.

### [2026-09-24 07:00:42] OKX 선물 자동매매 시스템 심층 아키텍처 및 런타임 코드 리뷰 완료
- OKX 선물 자동매매(coinbot_live/quant_system)의 4개 전략 엔진, 오케스트레이터, Webhook 실행 엔진(bot_c_okx_swap), 리스크 관리자 코드 전수 감사 완료.
- max_price_state 누락, market_info 미정의 NameError, PID Lock 부재로 인한 중복 주문, DCA 카운터 증가 결함 등 4대 크리티컬 버그 도출 및 개선 로드맵 수립.
### [2026-09-24 07:12:53] OKX 실서버(coinbot) 24시간 실거래 성과 및 JEV Supreme 가동 현황 재리뷰 완료
- GCP 실서버(136.111.207.137) SSH 직접 연결 및 실계좌 조회 완료.
- 계좌 자산(Equity) 10,687.36 USDT(09-22) -> 11,008.21 USDT(09-24)로 +320.85 USDT(+3.0%) 순증가 확인.
- JEV Supreme AI 정상 가동(400~500ms 레이턴시, 61개 LOB 피드, 0.55 미만 횡보장 컷 차단) 및 Breakeven Stop 수술 후 SEI/UNI/ZHIPU 익절 보존 확인.
## [2026-09-24 07:22:36] Google Cloud Nasdaq 서버 알파카 자동매매 시스템 실시간 리뷰
- Google Cloud nasdaq 서버(34.24.136.72)의 Bun Jev 사이드카 및 alpaca_jev_trader.py 가동 상태 점검.
- 알파카 가상계좌 자산(,689.81, 5개 보유 포지션) 및 25건 실체결 매매 통계 분석 완료, 양방향 ETF(TQQQ/SQQQ) 동시 보유 문제 및 브라켓 GTC 개선점 도출.


## [2026-09-24 07:27:43] Google Cloud Nasdaq 알파카 자동매매 v2.1 긴급 개선 및 배포 완료
- **개선 배포 완료**: alpaca_jev_trader.py v2.1 구글 nasdaq 서버 배포 및 데몬 재가동(PID: 2315163).
- **주요 개선 항목**:
  1. 롱/인버스 레버리지 ETF 상호 배제(Mutual Exclusion) 및 매크로 추세 반전 시 역방향 자동 청산(Regime Shift Unwind) 구현.
  2. 최대 포지션 4개 엄격 제한(미체결 주문 포함 get_active_count 카운트).
  3. 손절 후 30분 쿨다운 락아웃(Post-Loss Lockout)으로 고점 뇌동 재진입 방지.
  4. 브라켓 주문 time_in_force를 GTC로 변경하여 오버나잇 스탑로스 소멸 차단.
  5. 장 개장 시 충돌 포지션 자동 조율(Reconciliation) 루틴 탑재.



## [2026-09-24 07:33:10] 파보겔 추석 지인 선물 알리고(Aligo) LMS 문자안 개정
- 낯선 수신자 및 오랜 지인을 위한 정중한 사전 사과/양해 인사 및 명절 안부 문구 보강.
- KISA 정보통신망법 제50조 준수: (광고) 명칭, 발신인 식별, 080 무료수신거부 번호 규격 반영.


## [2026-09-24 07:57:26] 알리고 지인 주소록 분석 및 고인(윤호중, 홍인선) 연락처 영구 삭제
- 알리고 지인 주소록 정밀 분석: 총 4,312건 중 순수 010 정상 휴대폰 번호 3,724건 산출 완료.
- 별세하신 지인 故 윤호중(2건), 故 홍인선(1건) 주소록에서 안전 삭제 및 영구 제외 리스트 등록 완료.


## [2026-09-24 08:02:31] 알리고 잔여포인트 및 발송가능건수 분석
- 알리고 포인트 58,477.6P 중 기존 8,477.6P 제외 시 정확히 50,000P 충전된 내역 분석.
- 3,724명 LMS 발송을 위한 필요 포인트(약 9.5만P) 및 결제 확인 가이드 제시.


## [2026-09-24 08:07:34] (주)알리는사람들 10만원 입금 건 정밀 진단
- 부가세(VAT 10%) 미포함 100,000원 입금으로 55,000원(5만P)만 부분충전되고 45,000원 예치금 계류 상태 규명.
- 알리고 고객센터(02-511-4560) 및 추가 10,000원 입금/포인트 전환 해결 가이드 도출.


## [2026-09-24 08:12:25] 추석 지인 선물(3,724명) 14:00 예약 발송 세팅 완료
- 고인 3건 제외 순수 010 지인 3,724명 대상 업로드용 엑셀/CSV 생성 완료 (하이픈 010 보존 규격).
- 알리고 14:00 예약 발송 스크립트(reserve_chuseok_dispatch.py) 구축 및 IP 등록 가이드 제공.


## [2026-09-24 08:18:42] 알리고 추석 선물(3,724명) 바탕화면 업로드 엑셀 배치 완료
- 바탕화면에 [알리고_추석지인선물_3724명_대량발송_업로드용.xlsx] 즉시 업로드 파일 배치.
- 알리고 대량발송 14:00 예약 및 080 자동삽입 발송 가이드 완료.


## [2026-09-24 08:20:22] 파보겔 추석 지인 선물(3,724명) 알리고 공식 API 14:00 예약 발송 성공 완료
- 故 윤호중 님, 故 홍인선 님 제외 정제된 010 지인 3,724명 전원 오늘 오후 2시(14:00) 예약 등록 완료 (성공 3,724건 / 실패 0건).
- 알리고 msg_id (1460253070 외 7개 배치) 발급 및 잔여 LMS 4,354건 안전 보존 확인.

## [2026-09-27 17:03:57] 紐ъ뒪硫뺥?(monsmecta.kr) & ?뚮낫寃?ParvoGel) ?뱀궗?댄듃 ?뺣? 媛쒗렪 湲고쉷???묒닔 諛??ㅽ뻾 以鍮?- B2B ?섏쓽???쒕뵫: ??媛??좎옣 異?Gut-Liver-Kidney Axis) 3? 泥섎갑 ?쇱씤?? ?섎끂 ?뺤쟾湲??몃옪 MOA, S&J ?숇Ъ蹂묒썝 ?꾩긽 利앸? 諛섏쁺 湲고쉷.
- B2C ?뚮낫寃??곸꽭: ?먯꽍 ?섎끂 ?ㅽ?吏, 15遺??꾩궛 ?꾩땐留? 媛??좎옣 ???遺??0% 移댄뵾?쇱씠??諛?3?④퀎 ?ㅽ넗由щ씪???뺤젙.
- ?꾨줈?앺듃 ??[MONSMECTA_PARVOGEL_RENEWAL_PLAN.md] 湲고쉷 臾몄꽌 ?뺤떇 諛고룷 ?꾨즺.
## [2026-09-27 17:08:03] 紐ъ뒪硫뺥?(B2B) & ?뚮낫寃?B2C) ?뺣? 媛쒗렪 湲고쉷??肄붾뱶 援ы쁽 諛?諛고룷 鍮뚮뱶 ?꾨즺
- MonsmectaGateway.jsx: ??媛??좎옣 異?Gut-Liver-Kidney) 3? 泥섎갑 ?쇱씤?? 3? ?섎끂 MOA 紐⑤뱢, S&J ?숇Ъ蹂묒썝 ?고빀 ?ㅼ쟾 ?꾩긽 利앸?(?섏븸 0mL ?⑤룆 ?ъ뿬) 而댄룷?뚰듃 ?묒옱 ?꾨즺.
- Landing.jsx: ?몃? ?꾩궛 援ы넗/?덈? 怨듦컧 ?섏씤?ъ씤?? 3?④퀎 ?섎끂 ?ㅽ?吏 ?≪뀡(15遺??꾩땐/20遺??ы쉷/Flush 諛곗텧), 4? ?뚮퉬???덉떖 媛移??먯꽍 ?ㅽ?吏, 媛??좎옣 遺??0%) ?곕룞 ?꾨즺.
- npm run build 寃利??깃났 (dist 鍮뚮뱶 踰덈뱾留??꾨즺).
## [2026-09-27 17:13:16] 紐ъ뒪硫뺥?(monsmecta) 諛??뚮낫寃?parvogel) GitHub ?숈떆 而ㅻ컠쨌?몄떆 ?꾨즺
- 紐ъ뒪硫뺥? 由ы룷 (hongsoonil02-maker/monsmecta): 3? 泥섎갑 ?쇱씤?? 3? MOA, S&J ?묎툒 ?꾩긽 耳?댁뒪 諛섏쁺 ??main 釉뚮옖移??몄떆 ?꾨즺 (commit: 0026e94).
- ?뚮낫寃?由ы룷 (hongsoonil02-maker/parvogel): B2C ?섎끂 ?ㅽ?吏 3?④퀎 ?ㅽ넗由щ씪??諛?MonsmectaGateway ?뺣? 媛쒗렪蹂?master 釉뚮옖移??몄떆 ?꾨즺 (commit: cfb0b68).
## [2026-09-27 17:21:33] 紐ъ뒪硫뺥? ?쒓렇?덉쿂 ??洹몃┛ ???듭씪 諛??먯옣???꾩슜 ?곸뿭 ??B2C 諛곕꼫 ?뺣━ ?꾨즺
- ?ㅼ븻留ㅻ꼫: 紐ъ뒪硫뺥? 怨좎쑀??吏숈? ?뱀깋(#003828, #00513b, ?먮찓?꾨뱶/泥?줉 ???쇰줈 3? ?쇱씤?? 3? MOA, S&J ?묎툒 ?꾩긽 耳?댁뒪, 鍮꾧났媛??곸뿭 ?꾨㈃ 由щ뵒?먯씤 ?꾨즺.
- B2B 吏꾨즺沅?蹂댄샇: ?섏쓽??鍮꾧났媛??곸뿭 ?섎떒???몄텧?섎뜕 ?쇰컲??荑좏뙜/?ㅻ쭏?몄뒪?좎뼱 援щℓ 諛곕꼫 ?꾨꼍 ?쒓굅(?먯옣???꾩슜 諛쒖＜/臾대즺?섑뵆 李쎄뎄??吏묒쨷).
- monsmecta.kr (main) 諛?parvogel.kr (master) ??由ы룷吏?좊━???숈떆 鍮뚮뱶 寃利?諛?源껎뿀釉??몄떆 ?꾨즺.
## [2026-09-27 17:24:28] ?뱀젙 ?쒗뭹紐?'LIQI' ?꾨㈃ ??젣 諛??쇰컲 ?숈닠紐?'紐щえ由대줈?섏씠?? ?뺤젙 諛고룷 ?꾨즺
- LIQI ?섎끂 紐щえ由대줈?섏씠??-> 怨좎닚???섎끂 紐щえ由대줈?섏씠??/ ?섎끂 紐щえ由대줈?섏씠?몃줈 ?꾨㈃ 移섑솚.
- LIQI Nano Trap -> ?뺤쟾湲곗쟻 ?먯꽦 ?ы쉷 (?섎끂 紐щえ由대줈?섏씠???몃옪)?쇰줈 紐낆묶 蹂寃?
- monsmecta(main, commit: 218567c) 諛?parvogel(master, commit: 15be3d3) ???먭꺽 ??μ냼???꾨꼍 ?숆린???몄떆 ?꾨즺.
## [2026-09-27 17:29:31] monsmecta.kr ?ㅼ젣 ?쒖꽦 而댄룷?뚰듃(VetRestrictedSection.jsx) ?κ렇由??듭씪 諛??뚮퉬??諛곕꼫 ?곴뎄 ?쒓굅 ?꾨즺
- monsmecta_landing 由ы룷吏?좊━??src/components/VetRestrictedSection.jsx ??吏숈? ?뱀깋(#00281d, #002016, ?먮찓?꾨뱶) 由щ뵒?먯씤 ?곸슜.
- ?먯옣??鍮꾧났媛????섎떒???⑥븘?덈뜕 [?뚯쨷???꾩씠瑜??꾪븳 媛???곷퉬??蹂댁“?쒓? ?꾩슂?섏떊媛??] 荑좏뙜/?ㅻ쭏?몄뒪?좎뼱 B2C 諛곕꼫瑜??꾩쟾????젣.
- monsmecta(main, commit: 29f5883) ?뺤긽 鍮뚮뱶 寃利?諛?源껎뿀釉??몄떆 ?꾨즺.
## [2026-09-27 18:41:19] monsmecta.kr ?ㅼ젣 ?쒖꽦 而댄룷?뚰듃(VetRestrictedSection.jsx) ?κ렇由??듭씪 諛??뚮퉬??諛곕꼫 ?곴뎄 ?쒓굅 ?꾨즺
- monsmecta_landing 由ы룷吏?좊━??src/components/VetRestrictedSection.jsx ??吏숈? ?뱀깋(#00281d, #002016, ?먮찓?꾨뱶) 由щ뵒?먯씤 ?곸슜.
- ?먯옣??鍮꾧났媛????섎떒???⑥븘?덈뜕 [?뚯쨷???꾩씠瑜??꾪븳 媛???곷퉬??蹂댁“?쒓? ?꾩슂?섏떊媛??] 荑좏뙜/?ㅻ쭏?몄뒪?좎뼱 B2C 諛곕꼫瑜??꾩쟾????젣.
- monsmecta(main, commit: 29f5883) ?뺤긽 鍮뚮뱶 寃利?諛?源껎뿀釉??몄떆 ?꾨즺.
## [2026-09-27 18:55:06] monsmecta.kr ?ㅼ젣 ?쒖꽦 而댄룷?뚰듃(VetRestrictedSection.jsx) ?κ렇由??듭씪 諛??뚮퉬??諛곕꼫 ?곴뎄 ?쒓굅 ?꾨즺
- monsmecta_landing 由ы룷吏?좊━??src/components/VetRestrictedSection.jsx ??吏숈? ?뱀깋(#00281d, #002016, ?먮찓?꾨뱶) 由щ뵒?먯씤 ?곸슜.
- ?먯옣??鍮꾧났媛????섎떒???⑥븘?덈뜕 [?뚯쨷???꾩씠瑜??꾪븳 媛???곷퉬??蹂댁“?쒓? ?꾩슂?섏떊媛??] 荑좏뙜/?ㅻ쭏?몄뒪?좎뼱 B2C 諛곕꼫瑜??꾩쟾????젣.
- monsmecta(main, commit: 29f5883) ?뺤긽 鍮뚮뱶 寃利?諛?源껎뿀釉??몄떆 ?꾨즺.
## [2026-09-27 19:01:17] monsmecta.kr ?ㅼ젣 ?쒖꽦 而댄룷?뚰듃(VetRestrictedSection.jsx) ?κ렇由??듭씪 諛??뚮퉬??諛곕꼫 ?곴뎄 ?쒓굅 ?꾨즺
- monsmecta_landing 由ы룷吏?좊━??src/components/VetRestrictedSection.jsx ??吏숈? ?뱀깋(#00281d, #002016, ?먮찓?꾨뱶) 由щ뵒?먯씤 ?곸슜.
- ?먯옣??鍮꾧났媛????섎떒???⑥븘?덈뜕 [?뚯쨷???꾩씠瑜??꾪븳 媛???곷퉬??蹂댁“?쒓? ?꾩슂?섏떊媛??] 荑좏뙜/?ㅻ쭏?몄뒪?좎뼱 B2C 諛곕꼫瑜??꾩쟾????젣.
- monsmecta(main, commit: 29f5883) ?뺤긽 鍮뚮뱶 寃利?諛?源껎뿀釉??몄떆 ?꾨즺.
## [2026-09-27 19:27:12] monsmecta.kr ?ㅼ젣 ?쒖꽦 而댄룷?뚰듃(VetRestrictedSection.jsx) ?κ렇由??듭씪 諛??뚮퉬??諛곕꼫 ?곴뎄 ?쒓굅 ?꾨즺
- monsmecta_landing 由ы룷吏?좊━??src/components/VetRestrictedSection.jsx ??吏숈? ?뱀깋(#00281d, #002016, ?먮찓?꾨뱶) 由щ뵒?먯씤 ?곸슜.
- ?먯옣??鍮꾧났媛????섎떒???⑥븘?덈뜕 [?뚯쨷???꾩씠瑜??꾪븳 媛???곷퉬??蹂댁“?쒓? ?꾩슂?섏떊媛??] 荑좏뙜/?ㅻ쭏?몄뒪?좎뼱 B2C 諛곕꼫瑜??꾩쟾????젣.
- monsmecta(main, commit: 29f5883) ?뺤긽 鍮뚮뱶 寃利?諛?源껎뿀釉??몄떆 ?꾨즺.
## [2026-09-27 19:52:53] monsmecta.kr ?ㅼ젣 ?쒖꽦 而댄룷?뚰듃(VetRestrictedSection.jsx) ?κ렇由??듭씪 諛??뚮퉬??諛곕꼫 ?곴뎄 ?쒓굅 ?꾨즺
- monsmecta_landing 由ы룷吏?좊━??src/components/VetRestrictedSection.jsx ??吏숈? ?뱀깋(#00281d, #002016, ?먮찓?꾨뱶) 由щ뵒?먯씤 ?곸슜.
- ?먯옣??鍮꾧났媛????섎떒???⑥븘?덈뜕 [?뚯쨷???꾩씠瑜??꾪븳 媛???곷퉬??蹂댁“?쒓? ?꾩슂?섏떊媛??] 荑좏뙜/?ㅻ쭏?몄뒪?좎뼱 B2C 諛곕꼫瑜??꾩쟾????젣.
- monsmecta(main, commit: 29f5883) ?뺤긽 鍮뚮뱶 寃利?諛?源껎뿀釉??몄떆 ?꾨즺.
## [2026-09-27 19:59:06] monsmecta.kr ?ㅼ젣 ?쒖꽦 而댄룷?뚰듃(VetRestrictedSection.jsx) ?κ렇由??듭씪 諛??뚮퉬??諛곕꼫 ?곴뎄 ?쒓굅 ?꾨즺
- monsmecta_landing 由ы룷吏?좊━??src/components/VetRestrictedSection.jsx ??吏숈? ?뱀깋(#00281d, #002016, ?먮찓?꾨뱶) 由щ뵒?먯씤 ?곸슜.
- ?먯옣??鍮꾧났媛????섎떒???⑥븘?덈뜕 [?뚯쨷???꾩씠瑜??꾪븳 媛???곷퉬??蹂댁“?쒓? ?꾩슂?섏떊媛??] 荑좏뙜/?ㅻ쭏?몄뒪?좎뼱 B2C 諛곕꼫瑜??꾩쟾????젣.
- monsmecta(main, commit: 29f5883) ?뺤긽 鍮뚮뱶 寃利?諛?源껎뿀釉??몄떆 ?꾨즺.
## [2026-09-27 20:06:05] monsmecta.kr ?ㅼ젣 ?쒖꽦 而댄룷?뚰듃(VetRestrictedSection.jsx) ?κ렇由??듭씪 諛??뚮퉬??諛곕꼫 ?곴뎄 ?쒓굅 ?꾨즺
- monsmecta_landing 由ы룷吏?좊━??src/components/VetRestrictedSection.jsx ??吏숈? ?뱀깋(#00281d, #002016, ?먮찓?꾨뱶) 由щ뵒?먯씤 ?곸슜.
- ?먯옣??鍮꾧났媛????섎떒???⑥븘?덈뜕 [?뚯쨷???꾩씠瑜??꾪븳 媛???곷퉬??蹂댁“?쒓? ?꾩슂?섏떊媛??] 荑좏뙜/?ㅻ쭏?몄뒪?좎뼱 B2C 諛곕꼫瑜??꾩쟾????젣.
- monsmecta(main, commit: 29f5883) ?뺤긽 鍮뚮뱶 寃利?諛?源껎뿀釉??몄떆 ?꾨즺.
## [2026-09-27 20:10:03] monsmecta.kr ?ㅼ젣 ?쒖꽦 而댄룷?뚰듃(VetRestrictedSection.jsx) ?κ렇由??듭씪 諛??뚮퉬??諛곕꼫 ?곴뎄 ?쒓굅 ?꾨즺
- monsmecta_landing 由ы룷吏?좊━??src/components/VetRestrictedSection.jsx ??吏숈? ?뱀깋(#00281d, #002016, ?먮찓?꾨뱶) 由щ뵒?먯씤 ?곸슜.
- ?먯옣??鍮꾧났媛????섎떒???⑥븘?덈뜕 [?뚯쨷???꾩씠瑜??꾪븳 媛???곷퉬??蹂댁“?쒓? ?꾩슂?섏떊媛??] 荑좏뙜/?ㅻ쭏?몄뒪?좎뼱 B2C 諛곕꼫瑜??꾩쟾????젣.
- monsmecta(main, commit: 29f5883) ?뺤긽 鍮뚮뱶 寃利?諛?源껎뿀釉??몄떆 ?꾨즺.
## [2026-09-27 20:15:52] monsmecta.kr ?ㅼ젣 ?쒖꽦 而댄룷?뚰듃(VetRestrictedSection.jsx) ?κ렇由??듭씪 諛??뚮퉬??諛곕꼫 ?곴뎄 ?쒓굅 ?꾨즺
- monsmecta_landing 由ы룷吏?좊━??src/components/VetRestrictedSection.jsx ??吏숈? ?뱀깋(#00281d, #002016, ?먮찓?꾨뱶) 由щ뵒?먯씤 ?곸슜.
- ?먯옣??鍮꾧났媛????섎떒???⑥븘?덈뜕 [?뚯쨷???꾩씠瑜??꾪븳 媛???곷퉬??蹂댁“?쒓? ?꾩슂?섏떊媛??] 荑좏뙜/?ㅻ쭏?몄뒪?좎뼱 B2C 諛곕꼫瑜??꾩쟾????젣.
- monsmecta(main, commit: 29f5883) ?뺤긽 鍮뚮뱶 寃利?諛?源껎뿀釉??몄떆 ?꾨즺.
- **2026-09-27 20:36:02**: 회사 홍대표 직통(이미지/문자) 115번 우포켄넬(서유석 대표) 신규 샘플 주문 DB 전체 동기화, 구글 시트 웹앱 API 실시간 등록(success), 우체국택배 115건 접수용 엑셀 및 맞춤형 A4 알림판(HTML/PDF/PNG) 생성 완료

## [2026-09-28 15:15:10] 우체국택배 추석 지인 선물 28건(한정희 님 추가) 대량발송 엑셀 생성 완료
- 어제 27건 파일에 오늘 추가 접수된 1건(한정희 님)을 통합하여 28건 우체국택배 신규양식(xls/xlsx) 파일 재생성 및 다운로드 폴더 저장 완료.

## [2026-09-28 07:40] OKX 서브계정 BTC/ETH 페어 트레이딩 + DCA 스캘핑 봇 신규 구축 및 1,000 USDT 실전 가동

### 요약
1. **서브계정 전용 봇 구축 (`quant_system_20x`)**:
   - OKX V5 USDT 선물 기반 BTC/ETH 상대강도(스프레드) 볼린저 밴드 Z-Score 평균회귀 봇 완성.
   - 레버리지 백테스트(10x~100x) 검증 결과 최적의 **30배(30x)** 격리 마진 확정.
   - 1분봉 롤링 30분 윈도우 스캘핑 + 가용 시드의 15%($150) 동적 증거금 투입 모델 적용.
2. **실전 가동 및 첫 진입 성과**:
   - 1,000 USDT 이체 확인 후 가동(`PID: 1144572`).
   - 가동 즉시 Z=-2.71 괴리 감지되어 **BTC 롱(5.0계약) / ETH 숏(17.0계약)** 동시 체결 완료.
   - 진입 직후 마진 대비 **+2.15% (+3.22 USDT)** 수익권 순항 중.
3. **안전 장치**:
   - 1-Leg 비대칭 체결 위험 차단(Legging 롤백), 볼린저 중앙선 복귀 시 조기 익절, 최대 2회 분할 매수(DCA), -1.5% 하드 손절 탑재.
4. **상세 문서**: `agrolib/2026-09-28_OKX_BTC_ETH_페어트레이딩_DCA봇_신규구축_및_실전가동.md`

## [2026-09-28 19:00:40] 우체국택배 공식 17열 템플릿(template_befrecev_parcel_new) 규격 반영 완료
- 우체국 대량접수 오류 원인 규명: 13열 임의 양식에서 우체국 공식 17열 템플릿 복제 방식으로 스크립트 전면 개편.
- 28건 데이터가 주입된 공식 XLS 및 XLSX 파일 재발행 완료.

## [2026-09-28 19:03:58] 우체국택배 9열 내용품코드 필수값 반영 및 엑셀 재발행 완료
- ePOST 검증 오류 해결: 9열 내용품코드에 공식 필수 코드값(농/수/축산물(일반)) 28건 전 행 일괄 반영.
- template_befrecev_parcel_new (4).xls 및 관련 양식 파일 즉시 업데이트 완료.

## [2026-09-28 19:08:11] 우체국택배 28건 주소 띄어쓰기 및 필수 상세주소 정밀 교정 완료
- ePOST 주소 파서 검증 대응: 우지영 님(해송로30번길 19 -> 인천광역시 연수구 해송로30번길 19, 상세주소: 송도동 웰카운티3단지)을 비롯한 28건 전원 기본주소 및 필수 상세주소 완벽 정제.

- **2026-09-29 07:16:26**: [추석지인선물] 우지영 상세주소 보완(해송로30번길 19, 웰카운티3단지 308동 202호) - 구글 시트 웹앱 API 실시간 등록 및 우체국택배 28건 접수용 XLS/XLSX/로컬캐시 갱신 완료

- [2026-09-29 09:48:39] [parvogel_landing] 추석 지인 선물 프로모션 정리 완료: UI/UX 상단 공지 탑바, 네비게이션 헤더 및 모바일 메뉴 버튼, 우측 하단 플로팅 버튼, 팝업 모달 및 URL 쿼리 파라미터 연동을 제거하고 모든 관련 자산·데이터·스크립트를 archive/chuseok_gift_2026 및 zip으로 통합 백업 및 아카이빙 처리함.

- [2026-09-29 09:52:17] [parvogel_landing] 추석 선물 이벤트 정리 작업 깃허브 커밋 및 푸시 완료 (commit: 0db3835, branch: master). GitHub Actions 페이지 자동 배포 트리거됨.

- [2026-09-29 09:59:08] [parvogel_landing] 모바일 헤더 및 드롭다운 메뉴 주문/상담 신청 CTA 시인성 버그 수정: Tailwind primary-850 미등록으로 인한 투명 배경 및 흰색 글씨 가림 현상 해결, 주문·상담 신청 및 1병 무료체험 버튼 복원 및 깃허브 푸시 완료 (commit: aad458f).

- [2026-09-29 10:13:03] [parvogel_landing] 펫샵 및 브리더 10월 환절기 알리고 LMS 예약 발송 완료: 1단계(오늘 9/29 14:00 VIP 116개소 도매 재발주 115건 성공), 2단계(내일 9/30 14:00 미신청 1,349개소 2차 무료체험 1,349건 전량 성공 등록).

[2026-09-30 16:57:27] Removed real farm names (공주 구암농장, 충주 루미가든) from UI, blog posts, translations, and all related data files in parvogel_landing due to sensitive feedback.

[2026-09-30] Added export_all feature to Google Apps Script, downloaded current sample requests (including 10 new SMS requests), cleaned/deduplicated data (175 unique), and rebuilt batch-print.html for label printing.

[2026-09-30] Added ������ (Adorable) and ȫ���� to the sheet. Rebuilt batch-print.html for 176 unique targets.

[2026-09-30] Created Post Office Excel upload file (��ü��_�ù�������_����.xlsx) from the 176 unique targets.

[2026-09-30] Re-created Post Office Excel upload file (��ü��_�ù�������_144������_����.xlsx) to only include 33 new orders starting from seq #144.

[2026-09-30] [USER PREFERENCE UPDATED] ��ü�� �ù� �뷮 ������ ���� ������ �׻� �۾� �� ���ε� ���Ǹ� ���� `c:\Users\master\Downloads\` (�ٿ�ε� ����) ��ο� �ٷ� ����ǵ��� ���̽� ��ũ��Ʈ ���� �Ϸ�.

[2026-09-30] Fixed Post Office bulk upload format to use the official 17-column template (template_befrecev_parcel_new.xls).

[2026-09-30] Fixed missing detail address (���ּ�) issue by falling back to shop name or '������' to prevent epost validation errors.

[2026-09-30] Fixed post office 150 byte length limit on delivery request notes by safely truncating long notes to 45 characters.
- **2026-10-01 06:59**: ���� �۽� ��ũ��Ʈ(google_apps_script.gs) �� �˸��� �μ� ������(batch-print.html)���� ��ȣ���� ������� ��� ����(������/����ڸ�)�� ��µǵ��� �⺻�� �ѹ�(����) �Ϸ�.
- **2026-10-01 07:03**: �ֽ� ���� ��Ʈ �����͸� ����ȭ(fetch_and_save_raw.py ����) �� �ߺ� ���� ����(run_clean_dedup.py)�� �˸��� �μ� ��ũ��Ʈ(sync_batch_print_full.py)�� ������Ͽ� 177��° ��û�ڸ� ���������� ������Ʈ �Ϸ���.

- 2026-10-01: Fixed fetch_and_save_raw.py to properly fetch hospitalName and fallback to name. Fixed batch-print.html fallback logic issue. 강아지나라 correctly displays as 상호명.

- [2026-10-01 14:43:38] [parvogel_landing] 무료샘플 신청 구글 시트 데이터 전수 점검 및 9/30~10/1 2차 알리고 캠페인 이후 신규 신청 내역(15건) 정밀 분석 완료.

- [2026-10-01 14:53:02] [parvogel_landing] 중복 건(강아지나라, 유선환) 정리 확인 및 인접 농장(정읍애견사랑 원태경), 청통농장 도병천 A4 알림판 및 우체국 택배 명단(총 183개소) 반영 완료.

- **[2026-10-01 16:36:49]**: 파보겔 신규 주문 처 [멍벤져스(박정한), 010-2208-9245, 인천 남동구 간석동 234-4 트라움 108호] 구글 시트 및 발송 마스터 DB(184건) 추가, 맞춤 A4 알림판(HTML/PDF/PNG) 제작, 우체국택배 접수 엑셀 갱신 완료.

### [2026-10-01 22:23:00] Naver Blog Auto-Publishing Engine Integration Complete
- Playwright 기반 네이버 스마트에디터 ONE 자동 포스팅 엔진 연동 및 실배포 테스트 완료 (발행 URL: https://blog.naver.com/soonilhong/224428731358).
- 영구 로그인 세션 및 쿠키 보존 체계 구축, 바탕화면 즉시 실행 배치 파일 제공 및 마케팅 공장 파이프라인 결합 완료.

### [2026-10-01 22:46:22] Naver Blog Title, Intro, and Categories Restructured
- 블로그 메인명을 (주)한국아그로 수의학연구소로 개편하고, 소개글에 로타갈, 베타콜, 젬스밀크(어린동물 분유), 파보겔 등 4대 핵심 라인업 전문성 반영 완료.
- 낙서장 카테고리를 파보겔 (강아지 장염·설사)로 리뉴얼 및 젬스밀크, 산업동물, 수의사 칼럼 메뉴 체계 구축 완료.

### [2026-10-01 22:50:30] Sample Order #185 (오라애견) Added from Google Sheet
- 구글 시트 최하단 접수건인 오라애견(정미애 대표님, 010-2737-3032, 경기 파주) 신규 샘플 신청 등록 완료.
- clean_87_orders.json, 배송 명단, 우체국 택배 엑셀(117~185번 69건) 및 batch-print.html 일괄 갱신 완료.

### [2026-10-01 22:53:06] 69 Orders Split: B2B Business (40) vs Friends (29)
- 69건 대상 정밀 분석 결과 지인/추석선물 29건과 순수 B2B 사업자 40건으로 분리.
- 우체국 택배 엑셀 접수파일 각각 분리 생성 완료.

### [2026-10-01 22:54:39] Order Reclassification: Hong Jeong-ui to Breeder (B2B: 41, Friends: 28)
- #180 홍정의 대표님을 전문 브리더(B2B)로 정보 갱신 및 재분류 완료.
- 최종 분리: 순수 B2B 사업자 41건 / 추석 달맞이100 지인 선물 28건으로 우체국 접수 엑셀 갱신 완료.


## [2026-10-02 11:29:58] Parvogel Marketing Batch Path Fix
- Fixed working directory path in Desktop batch file to correctly target parvogel_landing.
- Verified marketing scripts status.


## [2026-10-02 11:34:35] Parvogel Marketing Pipeline Bugfixes
- Fixed FFmpeg Windows drawtext font path colon escaping in video_maker.py.
- Successfully verified 9:16 Shorts rendering and batch file echo encoding.


## [2026-10-02 11:50:42] Parvogel Marketing Duplicate Blocker & Retry Logic
- Resolved duplicate run block when Naver Blog failed on initial run.
- Added smart per-channel skip logic to avoid duplicate social posts while retrying failed channels.
- Fixed batch echo parsing for Coupang keyword.


## [2026-10-02 12:21:38] Added Sample Recipient & Generated A4 Notice Board (K타운 윤익수)
- Added applicant 'K타운 윤익수' (010-8248-1048, 경산시 와촌면 상암길37길 124) to sampleRecipients.json (#117), orders_cleaned.json (#186), cleaned_batch_input.tsv, and batch-print.html.
- Created dedicated custom A4 notice board `parvogel-notice-ktown.html` ready for print.


## [2026-10-02 12:38:37] K타운 (윤익수 / 010-8248-1048) 샘플 신청자 구글 시트 전송 완료 및 전체 알림판 일괄 인쇄기(batch-print.html 186번), 맞춤 알림판 생성 완료

- [2026-10-03 17:25:51] 구글 시트 파보겔 무료 샘플 신규 신청 건 확인 (강아지대공원 이완구 대표 010-2828-9779, 양주시 옥정동로7다길 62).

- [2026-10-03 17:28:58] 파보겔 무료 샘플 187번 (강아지대공원 이완구 대표) 정제명단 추가 및 맞춤 A4 알림판(HTML, PDF, PNG), 일괄인쇄(batch-print 187건), 신규 71건 우체국택배 접수 엑셀 자동 생성 완료.

- [2026-10-03 18:03:24] 네이버·구글 1위 노출 최적화: index.html 및 SEO.jsx에 몬스멕타/파보겔 타겟 키워드 전진 배치, Schema.org 구조화 데이터(Product/Brand/Organization/FAQ) 정적 하드코딩 삽입 및 sitemap.xml 갱신, 프로덕션 빌드 완료.

- [2026-10-03 18:36:54] 네이버 블로그 스마트블록 상위 점유 자동 포스팅 엔진(login_and_publish_blog.py) 연동 및 브라우저 세션 락 해제 완료.
