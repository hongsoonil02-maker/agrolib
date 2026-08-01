# ORCA - Antigravity - OmniRoute 연동 및 토큰 무제한 세팅 가이드

## 1. 개요
이 문서는 ORCA 오케스트레이터와 Antigravity IDE(내부 Kilo Code)를 옴니라우트(OmniRoute)를 통해 연결하여, 에이전트 간의 컨텍스트(토큰) 과부하 문제를 해결하고 무제한에 가까운 토큰 라우팅 환경을 구축하는 방법을 영구적으로 기록합니다.

## 2. Kilo Code (Antigravity 내부) 설정
Antigravity IDE 내에서 옴니라우트를 메인 엔드포인트로 사용하도록 Kilo Code를 설정해야 합니다.

1. **옴니라우트 실행 확인:** 
   - 터미널에서 `omniroute` 명령어로 서버 가동 확인 (`http://localhost:20128` 접속)
2. **Kilo Code 공급자 설정:**
   - Kilo Code 패널 -> ⚙️ 설정(Settings) -> **공급자(Providers)**
   - **OpenAI Compatible** (또는 OpenAI) 항목에 연결
3. **설정값 입력:**
   - **Base URL:** `http://localhost:20128/v1` (반드시 `/v1` 포함)
   - **API Key:** 옴니라우트 대시보드에서 발급받은 키
   - **모델 (Model ID):** `auto` 또는 `auto/coding` 입력
4. **문제 해결 (Troubleshooting):**
   - 만약 "응답이 예기치 않게 종료되었으며..." 에러가 발생하면, 컨텍스트 과부하이거나 `auto` 모델이 코딩용(긴 텍스트)을 감당하지 못하는 상태일 수 있음. 
   - 이 경우 모델 ID를 **`auto/coding`**으로 변경하여 해결함.

## 3. ORCA 오케스트레이터 설정
ORCA가 안티그래비티를 메인 두뇌로 인식하게 만들어야, 위에서 세팅한 옴니라우트 통신망을 자동으로 활용할 수 있습니다.

1. **ORCA 에이전트 탭 이동:**
   - ORCA 좌측 메뉴 -> **에이전트 (Agents)**
2. **기본 Agent 선택:**
   - 여러 에이전트 버튼 중 **`Antigravity`** (A 모양 로고)를 찾아 클릭(선택 상태로 변경)
3. **결과:**
   - ORCA에 별도로 Base URL을 입력할 필요 없이, Antigravity를 대장으로 선택함으로써 내부적으로 연동된 옴니라우트망을 그대로 활용함.
   - 우측 하단 상태 표시줄에 Antigravity와 Gemini 아이콘이 활성화된 것을 통해 연결 상태를 실시간 확인 가능.

## 4. 아키텍처 요약
- **ORCA (오케스트레이터)** -> 지시 및 작업 분배
- **Antigravity (메인 에이전트)** -> ORCA의 명령을 수신하여 실행
- **OmniRoute (게이트웨이)** -> Kilo Code를 거쳐 전달된 프롬프트를 쿼터가 넉넉한 최적의 모델(auto/coding 등)로 라우팅 (단일 모델 과부하 방지 및 토큰 압축 엔진 활용)
