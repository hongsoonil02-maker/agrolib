# 수익 극대화 & 손실 최소화 및 포트폴리오 리밸런싱 계획

최근 1주일간 벤처(알트코인)에서 압도적인 수익이 발생한 데이터를 바탕으로, **수익은 크게(Let Profits Run)**, **손실은 짧게(Cut Losses Short)** 가져가고 **자본 배분을 최적화(Portfolio Weighting)**하기 위한 기술적 구현 계획입니다.

## User Review Required
> [!WARNING]
> 현재 모든 봇(Major/Venture)이 동일한 비율로 자본을 배분받고 있습니다. 이번 패치로 벤처에 자본을 더 많이 밀어주고 메이저는 비중을 축소하게 됩니다. 이 방향이 맞는지 확인 부탁드립니다.

## Proposed Changes

### 1. 자본 배분 가중치 적용 (Portfolio Weighting)
기존 로직은 전체 자산을 15개 포지션으로 단순히 1/N 균등 분할하고 있었습니다. 이제 전략별로 **`PORTFOLIO_WEIGHT`** 가중치를 도입합니다.

#### [MODIFY] [strategy_common.py](file:///home/hongsoonil02/quant_system/strategy_common.py)
- `BaseStrategyBrain` 클래스에 `PORTFOLIO_WEIGHT = 1.0` 속성을 추가합니다.
- 목표 마진 계산 시 `(total_equity / MAX_OPEN_POSITIONS) * PORTFOLIO_WEIGHT`를 적용합니다.

#### [MODIFY] [okx_venture_strategy.py](file:///home/hongsoonil02/quant_system/okx_venture_strategy.py)
- `PORTFOLIO_WEIGHT = 1.5` 적용: 수익을 견인하는 알트/밈 코인에 **자본을 1.5배 가중 배분**합니다.

#### [MODIFY] [okx_major_strategy.py](file:///home/hongsoonil02/quant_system/okx_major_strategy.py)
- `PORTFOLIO_WEIGHT = 0.5` 적용: 방어적 성격의 메이저 코인에는 **자본을 절반(0.5배)으로 축소 배분**합니다.

---

### 2. 손실 최소화 (Cut Losses Short) - 타이트한 스탑로스
Venture 코인은 수익도 높지만 BZ(블루젤)처럼 급격하게 무너지는 꼬리 위험(Tail Risk)이 존재합니다.

#### [MODIFY] [strategy_common.py](file:///home/hongsoonil02/quant_system/strategy_common.py) & 서브클래스
- 기존 일괄 `-30%(-0.30)` 였던 하드 스탑로스(`HARD_STOP_LOSS_PCT`)를 전략별로 오버라이드할 수 있도록 변경합니다.
- **Venture (알트)**: 변동성을 제어하기 위해 **`-15%(-0.15)`**로 매우 타이트하게 조입니다.
- **Major (메이저)**: 변동성이 적어 휩쏘가 잦으므로 기존 **`-30%(-0.30)`**를 유지합니다.

---

### 3. 수익 극대화 (Let Profits Run) - 불타기(Pyramiding) 강화
트렌드가 한 번 터질 때(예: OKB +4만 달러 수익), 수익을 극대화하기 위해 승자 포지션에 대한 불타기 비중을 높입니다.

#### [MODIFY] [strategy_common.py](file:///home/hongsoonil02/quant_system/strategy_common.py) & 서브클래스
- `PYRAMID_RATIO` 속성을 도입합니다. (기본값 0.35)
- **Venture (알트)**: `PYRAMID_RATIO = 0.50` 으로 상향 조정합니다. 즉, 추세를 타고 +40% 이상 수익권 진입 시, **기존보다 훨씬 공격적인 물량(50%)**으로 추세 추종 불타기를 감행합니다.
- **Major (메이저)**: 기존 `0.35` 비율 유지.

## Verification Plan

### Manual Verification
- 봇 재구동(`systemctl restart`) 후 로그를 모니터링하여 가중치가 제대로 곱해진 채로 사이징(`target_margin`)이 계산되는지 확인합니다.
