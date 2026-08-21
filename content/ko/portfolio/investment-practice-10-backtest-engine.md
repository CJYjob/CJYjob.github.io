---
title: "투자 실습 ⑩ 백테스트 엔진 — 미래참조 차단·실제 ETF 손익"
date: 2026-06-09
draft: false
description: "전일 신호·수급 지연으로 미래참조를 차단하고, 실제 ETF 가격·비용·세금을 반영해 전략 손익을 검증하는 백테스트 엔진."
categories:
  - "Investment"
series:
  - "Investment Practice"
tags:
  - "Investment"
  - "ETF"
weight: 100
aliases:
  - /portfolio/investing/stock/practice/part-10-backtest-engine/
---

## 백테스트 엔진 — 미래참조 차단과 실제 ETF 손익

[구현 편](/ko/portfolio/investment-practice-09-implementation/)에서 지수·수급 데이터를 모으고 국면을 라벨링했다. 이번에는 그 라벨을 실제 ETF 가격에 연결해 손익을 계산한다.

핵심은 세 가지다.

1. **미래참조를 막는다.** 오늘 종가로 만든 신호를 오늘 종가 체결에 쓰지 않는다.
2. **실제 ETF 가격을 쓴다.** 지수 수익률을 그대로 전략 수익률로 간주하지 않는다.
3. **비용과 세금을 넣는다.** 회전율이 높은 전략일수록 이 차이가 커진다.

### 미래참조 차단

수급 데이터는 장 마감 후 확정되므로 당일 종가 매매에는 사용할 수 없다. 따라서 [구현 편](/ko/portfolio/investment-practice-09-implementation/)의 `add_indicators()`에서 `flow_lag=1`을 적용한다. 그리고 국면·포지션 신호 자체도 한 거래일 뒤로 민다.

```python
# 수급을 하루 지연시켜 지표 계산
signal_df = label(add_indicators(combined_df, **params, flow_lag=1))

# 오늘 계산된 포지션은 다음 거래일부터 사용
signal_df['position_exec'] = signal_df['position'].shift(1)
signal_df['regime_exec'] = signal_df['regime'].shift(1)
```

이렇게 하면 t일 종가까지 확정된 정보가 t+1일 거래에 반영된다.

### 실제 ETF 가격 수집

손익은 KOSPI200·KOSDAQ150 지수가 아니라 실제 정방향·인버스 ETF 가격으로 계산한다. 그래야 추적오차, 인버스의 일간 재설정, 변동성 손실, 베이시스와 운용비용이 가격에 반영된다.

```python
from pykrx import stock

ETF = {
    'kospi_long':  '069500',  # KODEX 200
    'kospi_inv':   '114800',  # KODEX 인버스
    'kosdaq_long': '229200',  # KODEX 코스닥150
    'kosdaq_inv':  '251340',  # KODEX 코스닥150선물인버스
}

def fetch_etf(ticker, start, end):
    d = stock.get_market_ohlcv_by_date(start, end, ticker)
    d = d.rename(columns={'종가':'close'})
    return d[['close']]
```

ETF 상장일이 서로 다르므로 네 상품이 모두 존재하는 **공통 가격 구간**만 사용한다. 공통 구간 밖에서 지수 라벨이 존재하더라도 손익 검증에는 넣지 않는다.

### 포지션을 숫자 비중으로 변환

[성과 지표 편](/ko/portfolio/investment-strategy-06-position-and-metrics/)에서 정한 포지션을 정방향·인버스·현금 비중으로 바꾼다.

```python
WEIGHTS = {
    '정90/현금10':       (0.90, 0.00, 0.10),
    '정65/현금35':       (0.65, 0.00, 0.35),
    '정45/인버스55':     (0.45, 0.55, 0.00),
    '정50/인버스50':     (0.50, 0.50, 0.00),
    '정55/인버스45':     (0.55, 0.45, 0.00),
    '인버스65/현금35':   (0.00, 0.65, 0.35),
    '인버스90/현금10':   (0.00, 0.90, 0.10),
    '정35/인버스35/현금30': (0.35, 0.35, 0.30),
}
```

### 일별 손익

ETF의 일별 수익률을 구하고, 전일에 확정된 실행 비중을 곱한다.

```python
long_ret = long_price['close'].pct_change()
inv_ret  = inv_price['close'].pct_change()

w = signal_df['position_exec'].map(WEIGHTS)
w_long = w.map(lambda x: x[0] if isinstance(x, tuple) else 0.0)
w_inv  = w.map(lambda x: x[1] if isinstance(x, tuple) else 0.0)
w_cash = w.map(lambda x: x[2] if isinstance(x, tuple) else 1.0)

# 현금수익률은 우선 0으로 두고 필요하면 단기금리로 대체
strategy_gross = w_long * long_ret + w_inv * inv_ret
```

### 거래비용·세금

비용은 비중 변화량을 기준으로 잡는다. 오늘 목표 비중과 어제 목표 비중의 차이가 실제 매매량이다.

```python
turnover = (
    w_long.diff().abs().fillna(0)
    + w_inv.diff().abs().fillna(0)
)

BROKER_FEE = 0.00005     # 예시값
SLIPPAGE   = 0.00010     # 예시값

trade_cost = turnover * (BROKER_FEE + SLIPPAGE)
strategy_net = strategy_gross - trade_cost
```

세금은 ETF 유형과 계좌에 따라 달라질 수 있으므로 별도 함수로 분리한다. 국내 주식형 ETF와 인버스·파생형 ETF의 과세 구조가 다르므로 하나의 고정 세율로 뭉개지 않는다.

```python
def tax_cost(position_before, position_after, price_ret, config):
    # 실제 적용 전 최신 세법·상품 유형을 확인해 config로 주입
    return 0.0
```

백테스트 코드에 세법을 하드코딩하지 않는 이유는 제도가 바뀔 수 있기 때문이다.

### 리밸런싱 밴드

목표 비중이 조금 바뀔 때마다 매매하면 비용이 커진다. 따라서 실제 전략에서는 목표와 현재 비중의 차이가 일정 수준 이상일 때만 리밸런싱하는 밴드를 둘 수 있다.

```python
REBALANCE_BAND = 0.05

def need_rebalance(current_w, target_w, band=REBALANCE_BAND):
    return max(abs(current_w[i] - target_w[i]) for i in range(3)) >= band
```

밴드가 너무 작으면 회전율이 높아지고, 너무 크면 목표 포지션을 제대로 따라가지 못한다. 따라서 밴드도 학습 구간에서 한 점 최적값을 찾기보다 넓은 범위에서 성과가 유지되는지를 본다.

### 비교 기준

전략 성과는 단독 숫자가 아니라 비교군과 함께 본다.

- 정방향 ETF 단순 보유
- 정방향·인버스 정적 50:50
- 전액 현금
- 국면 기반 동적 전략

```python
bench_long = long_ret
bench_5050 = 0.5 * long_ret + 0.5 * inv_ret
bench_cash = pd.Series(0.0, index=long_ret.index)
```

### 성과 지표

최종 비교는 CAGR·MDD·변동성·샤프·소르티노·칼마·회전율을 함께 본다.

```python
import numpy as np

def performance(r, periods=252):
    r = r.dropna()
    equity = (1 + r).cumprod()
    years = len(r) / periods
    cagr = equity.iloc[-1] ** (1 / years) - 1 if years > 0 else np.nan
    peak = equity.cummax()
    dd = equity / peak - 1
    mdd = dd.min()
    vol = r.std(ddof=0) * np.sqrt(periods)
    sharpe = (r.mean() * periods) / vol if vol > 0 else np.nan
    downside = r[r < 0].std(ddof=0) * np.sqrt(periods)
    sortino = (r.mean() * periods) / downside if downside > 0 else np.nan
    calmar = cagr / abs(mdd) if mdd < 0 else np.nan
    return {
        'CAGR': cagr,
        'MDD': mdd,
        'Volatility': vol,
        'Sharpe': sharpe,
        'Sortino': sortino,
        'Calmar': calmar,
    }
```

### 학습/검증 분리

임계값은 전체 기간을 보고 고르지 않는다. 먼저 학습 구간에서 후보를 비교하고, 선택한 규칙을 손대지 않은 검증 구간에 적용한다.

```python
train = result.loc[:'2021-12-31']
test  = result.loc['2022-01-01':]
```

한 숫자에서만 최고 성과가 나는 임계값보다, 주변 값을 조금 바꿔도 성과가 유지되는 **고원형(plateau)** 구간을 우선한다. KOSPI와 KOSDAQ은 구조가 다르므로 파라미터 표도 따로 관리한다.

### 검증 순서

최종 엔진은 다음 순서로 돌린다.

1. 지수·수급 원자료 조립
2. 수급을 1일 지연
3. 지표 계산·국면 라벨링
4. 국면 신호를 다시 1일 지연해 실행 포지션 생성
5. 실제 ETF 가격의 공통 거래 구간과 결합
6. 포지션별 일별 손익 계산
7. 비중 변화에 따른 비용·세금 반영
8. 비교군과 CAGR·MDD·샤프·회전율 비교
9. 학습/검증 분리와 파라미터 강건성 확인

이 단계까지 통과해야 "과거에 좋아 보이는 규칙"이 아니라, 실제 상품 구조와 정보 시점을 고려한 전략 후보가 된다.
