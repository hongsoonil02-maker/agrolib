# 🔒 Immutability Raw Zone (/Raw)

> **⚠️ CAUTION: Immutable Data Area**  
> 본 디렉토리는 16개 에이전트의 토너먼트 과정에서 발생한 원본 로그, 백테스트 결과 Raw Data, 시장 수집 데이터 및 임직원이 제공한 원본 문서가 저장되는 **불변 데이터 구역**입니다. (Vault: Agrolib)

---

## 📌 규칙 (Immutability Rules)
1. **수정 및 삭제 금지**: 안그래(Orchestrator), 16개 에이전트, 그리고 임직원 모두 본 디렉토리 내부의 원본 데이터를 직접 수정하거나 삭제할 수 없습니다.
2. **추가 전용 (Append-Only)**: 새로운 토너먼트 세션 로그나 원본 백테스트 수치가 발생하면 타임스탬프 기반 파일명으로 신규 파일만 추가 전용으로 작성됩니다.
3. **5-Filter 가공**: 본 디렉토리의 데이터는 Agent 14 (Wiki Architect)에 의해 5-Filter System 검증을 거친 후 요약/재구성되어 `/Wiki` 구역으로 퍼블리싱됩니다.

---

## 📁 Subdirectories
- `/Raw/tournament_logs/` : 에이전트 간 토너먼트 시뮬레이션 원본 로그
- `/Raw/backtest_reports/` : 백테스트 & 몬테카를로 파라미터 시뮬레이션 Raw Data
- `/Raw/market_data/` : 업비트, OKX, KIS, 나스닥 원본 시세 및 오더북 데이터
- `/Raw/documents/` : 임직원 제공 원본 지침서 및 관련 자료
