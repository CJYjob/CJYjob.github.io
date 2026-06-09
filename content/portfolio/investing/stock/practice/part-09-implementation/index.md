---
title: "투자 실습 ⑨ 구현 — 데이터 수집·국면 라벨링"
date: 2026-06-09
draft: false
description: "pykrx로 KOSPI200·KOSDAQ150 지수·수급을 수집하고 SMA·ADX·%B·수급 z-score로 국면을 라벨링하는 코드."
categories: ["Investment"]
tags: ["Investment", "ETF"]
---

## 구현 — 데이터 수집과 국면 라벨링 (pykrx · 코랩)

여기까지가 설계라면, 아래는 9단계 절차 중 **1(데이터 조립)·3(국면 분류)·4(포지션 매핑)** 를 실제로 돌린 코드다. 환경은 구글 코랩, 데이터는 pykrx(무료·권한 불필요), 저장은 구글 드라이브. 신호 검증용 지수는 2010년~현재 구간으로 모으고, 손익 검증(실제 ETF 가격)은 다음 단계로 둔다.

> ⚠️ pykrx 버전에 따라 투자자 수급 함수명·컬럼이 다를 수 있다. **셀 2**로 컬럼을 먼저 확인하고 **셀 3의 CONFIG**(외국인·기관 순매수 컬럼명)를 맞춘다.

실행 순서: 셀 1(지수 수집) → 셀 2(수급 함수 탐색) → 셀 3(수급 결합) → 셀 4(국면 라벨링).

### 셀 1 — 설치·드라이브 마운트·지수 일봉 수집

코스피200은 지수코드 `1028`로 바로 받고, 코스닥150은 시장 지수 목록에서 이름으로 코드를 자동 탐색한다(현재 `2203`).

```python
# ===== 셀 1: 설치 · 드라이브 마운트 · 지수 일봉 수집 =====
!pip install pykrx --quiet
from google.colab import drive
drive.mount('/content/drive')

import os
from datetime import datetime
import pandas as pd
from pykrx import stock

SAVE_DIR = '/content/drive/MyDrive/Colab Notebooks/stock_2026_blog/etf_strategy'
os.makedirs(SAVE_DIR, exist_ok=True)
START = "20100101"
END   = datetime.today().strftime("%Y%m%d")

def fetch_index(ticker, name):
    df = stock.get_index_ohlcv(START, END, ticker)
    df = df.rename(columns={'시가':'open','고가':'high','저가':'low','종가':'close','거래량':'volume'})
    df.index.name = 'date'
    df.to_csv(f'{SAVE_DIR}/{name}_index.csv', encoding='utf-8-sig')
    print(f'[{name}] {df.shape}  {df.index.min().date()} ~ {df.index.max().date()}')
    return df

kospi200 = fetch_index('1028', 'kospi200')

# 코스닥150 지수코드 자동 탐색
kq150 = None
for t in stock.get_index_ticker_list(END, market='KOSDAQ'):
    if stock.get_index_ticker_name(t).replace(' ', '') == '코스닥150':
        kq150 = t; break
print('코스닥150 ticker =', kq150)
kosdaq150 = fetch_index(kq150, 'kosdaq150')
```

출력:

```
[kospi200] (4041, 7)  2010-01-04 ~ 2026-06-04
코스닥150 ticker = 2203
[kosdaq150] (4041, 7)  2010-01-04 ~ 2026-06-04
```

> pykrx 자체는 로그인이 필요 없다. 다만 일부 환경에서 KRX 인증이 필요하면 코랩 Secrets에 `KRX_ID`/`KRX_PW`를 저장해 환경변수로 주입할 수 있다(선택).
>
> ```python
> import os
> from google.colab import userdata
> os.environ['KRX_ID'] = userdata.get('KRX_ID')
> os.environ['KRX_PW'] = userdata.get('KRX_PW')
> ```

### 셀 2 — 투자자 수급 함수 탐색 (pykrx 버전 차이 대비)

`dir(stock)`에서 수급 관련 함수를 추려 보고, 후보 함수를 최근 구간만 시험 호출해 컬럼 구조를 확인한다.

```python
# ===== 셀 2: 투자자 수급 함수 탐색 (pykrx 버전 차이 대비) =====
print('관련 함수:', [f for f in dir(stock) if any(k in f.lower() for k in ('investor','trading','net_purchase'))])

# 후보 함수를 최근 구간만 시험 호출해 컬럼 구조를 확인 (KOSPI 전체 시장)
try:
    sample = stock.get_market_trading_value_by_date("20260101", END, "KOSPI")
    print('\n[get_market_trading_value_by_date] 컬럼:', list(sample.columns))
    print(sample.tail(3))
except Exception as e:
    print('이 함수가 없거나 시그니처가 달라요 → 위 함수 목록에서 골라 교체:', e)
```

출력:

```
관련 함수: ['get_etf_trading_volume_and_value', 'get_market_net_purchases_of_equities', 'get_market_net_purchases_of_equities_by_ticker', 'get_market_trading_value_and_volume_by_ticker', 'get_market_trading_value_by_date', 'get_market_trading_value_by_investor', 'get_market_trading_volume_by_date', 'get_market_trading_volume_by_investor', 'get_shorting_investor_value_by_date', 'get_shorting_investor_volume_by_date']

[get_market_trading_value_by_date] 컬럼: ['기관합계', '기타법인', '개인', '외국인합계', '전체']
                     기관합계          기타법인             개인          외국인합계  전체
날짜
2026-06-01  2442734402012   -7045956425   386231493075 -2821919938662   0
2026-06-02   -54581539354    4361786494  6353747500232 -6303527747372   0
2026-06-04  1525451417948  127314148549  5013493246131 -6666258812628   0
```

컬럼명(`외국인합계`, `기관합계`)을 확인했으니 셀 3의 CONFIG에 그대로 넣는다.

### 셀 3 — 투자자 수급 수집 + 결합 CSV 생성

지수 일봉에 외국인+기관 순매수 금액을 합쳐 `flow` 한 컬럼으로 붙인다. 이 단계 결과가 라벨링의 입력이다.

```python
# ===== 셀 3: 투자자 수급 수집 + 결합 CSV 생성 =====
# 셀 2 출력에서 확인한 '외국인 순매수금액' / '기관 순매수금액' 컬럼명을 아래에 맞추세요.
FOREIGN_COL = '외국인합계'   # ← 외국인(순매수 금액) 컬럼명으로 수정
INSTIT_COL  = '기관합계'     # ← 기관(순매수 금액) 컬럼명으로 수정
# ※ 함수가 '순매수'가 아니라 '거래대금(매수/매도)'을 준다면, 순매수 컬럼을 주는 함수로 교체하거나
#    (매수금액 - 매도금액)으로 직접 계산하세요.

def fetch_flow_value(market):
    return stock.get_market_trading_value_by_date(START, END, market)

def build_combined(index_name, market):
    idx = pd.read_csv(f'{SAVE_DIR}/{index_name}_index.csv', index_col='date', parse_dates=True)
    val = fetch_flow_value(market)
    val.index = pd.to_datetime(val.index); val.index.name = 'date'
    flow = (val[FOREIGN_COL] + val[INSTIT_COL]).rename('flow')   # 외국인+기관 순매수 금액
    out = idx.join(flow, how='left')
    out['flow'] = out['flow'].fillna(0)
    out.to_csv(f'{SAVE_DIR}/{index_name}_combined.csv', encoding='utf-8-sig')
    print(f'[{index_name}] combined {out.shape}')
    return out

c_kospi  = build_combined('kospi200', 'KOSPI')
c_kosdaq = build_combined('kosdaq150', 'KOSDAQ')
```

출력:

```
[kospi200] combined (4041, 8)
[kosdaq150] combined (4041, 8)
```

### 셀 4 — 지표 계산 + 국면 라벨링 (5단계 → 횡보 3분할 → 7단계)

[지표 편](/portfolio/investing/stock/practice/part-03-regime-indicators/)의 4지표(SMA 배열·ADX·BB %B·수급 z-점수)를 계산하고, [국면 분류 편](/portfolio/investing/stock/practice/part-02-market-regimes/)의 규칙대로 라벨을 붙인다. ADX 임계값은 **하락 비대칭**(강한상승 ≥30 vs 강한하락 ≥25)을 반영하고, 횡보는 %B로 상단/중단/하단 3분할해 7단계로 확장한다. 파라미터는 KOSPI 20/60·ADX14, KOSDAQ 10/40·ADX10의 *예시*이며 8단계 최적화에서 보정한다. `add_indicators`에는 `flow_lag` 인자를 두었는데, 여기(셀 4·설명용 라벨)서는 기본 0이고 [엔진 편](/portfolio/investing/stock/practice/part-10-backtest-engine/) 백테스트에서 1로 켜서 미래참조를 차단한다.

```python
# ===== 셀 4: 지표 계산 + 국면 라벨링 (5단계, 횡보 3분할 → 7단계) =====
import numpy as np, pandas as pd

def wilder(x, n):
    x = np.asarray(x, float); s = np.full(len(x), np.nan)
    valid = np.where(~np.isnan(x))[0]
    if len(valid) < n: return s
    f = valid[0] + n - 1
    s[f] = np.nansum(x[valid[0]:f+1])
    for i in range(f+1, len(x)):
        s[i] = s[i-1] - s[i-1]/n + (x[i] if not np.isnan(x[i]) else 0)
    return s

def add_indicators(df, ma_s=20, ma_l=60, adx_n=14, bb_n=20, bb_k=2.0, flow_win=60, flow_lag=0):
    d = df.copy()
    # look-ahead 차단①: 수급은 종가 후 공시 → 지표 계산 전에 flow_lag일 지연(백테스트에서 1로 사용)
    if 'flow' in d.columns and flow_lag > 0:
        d['flow'] = d['flow'].shift(flow_lag)
    c,h,l = d['close'].values, d['high'].values, d['low'].values; N=len(d)
    d['sma_s']=d['close'].rolling(ma_s).mean(); d['sma_l']=d['close'].rolling(ma_l).mean()
    std=d['close'].rolling(bb_n).std(ddof=0); mid=d['close'].rolling(bb_n).mean()
    up,dn=mid+bb_k*std, mid-bb_k*std
    d['pctB']=(d['close']-dn)/(up-dn); d['bw']=(up-dn)/mid*100
    TR=np.full(N,np.nan); pDM=np.zeros(N); mDM=np.zeros(N)
    for i in range(1,N):
        TR[i]=max(h[i]-l[i],abs(h[i]-c[i-1]),abs(l[i]-c[i-1]))
        um,dm=h[i]-h[i-1], l[i-1]-l[i]
        pDM[i]=um if(um>dm and um>0) else 0; mDM[i]=dm if(dm>um and dm>0) else 0
    atr=wilder(TR,adx_n); spDM=wilder(pDM,adx_n); smDM=wilder(mDM,adx_n)
    with np.errstate(invalid='ignore',divide='ignore'):
        pDI=100*spDM/atr; mDI=100*smDM/atr; DX=100*np.abs(pDI-mDI)/(pDI+mDI)
    ADX=np.full(N,np.nan); fi=np.where(~np.isnan(DX))[0]
    if len(fi)>=adx_n:
        s0=fi[0]+adx_n-1; ADX[s0]=np.nanmean(DX[fi[0]:s0+1])
        for i in range(s0+1,N):
            if not np.isnan(DX[i]): ADX[i]=(ADX[i-1]*(adx_n-1)+DX[i])/adx_n
    d['adx']=ADX
    cum5=d['flow'].rolling(5).sum()
    d['flow_z']=(cum5-cum5.rolling(flow_win).mean())/cum5.rolling(flow_win).std(ddof=0)
    return d

def label(d, adx_trend=20, adx_strong_up=30, adx_strong_dn=25):
    regs=[]; poss=[]
    for _,r in d.iterrows():
        if np.isnan(r['sma_l']) or np.isnan(r['adx']) or np.isnan(r['pctB']):
            regs.append('-'); poss.append('-'); continue
        aup=r['close']>r['sma_s']>r['sma_l']; adn=r['close']<r['sma_s']<r['sma_l']; a=r['adx']
        if a<adx_trend: reg='횡보'
        elif aup and a>=adx_strong_up: reg='강한상승'
        elif aup and a>=adx_trend: reg='약한상승'
        elif adn and a>=adx_strong_dn: reg='강한하락'
        elif adn and a>=adx_trend: reg='약한하락'
        else: reg='중립전이'
        if reg=='횡보':
            sub='상단' if r['pctB']>=0.7 else('하단' if r['pctB']<=0.3 else '중단'); reg=f'횡보_{sub}'
        pos={'강한상승':'정90/현금10','약한상승':'정65/현금35','횡보_상단':'정45/인버스55',
             '횡보_중단':'정50/인버스50','횡보_하단':'정55/인버스45','약한하락':'인버스65/현금35',
             '강한하락':'인버스90/현금10','중립전이':'정35/인버스35/현금30'}[reg]
        regs.append(reg); poss.append(pos)
    d=d.copy(); d['regime']=regs; d['position']=poss; return d

# KOSPI 20/60·ADX14 / KOSDAQ 10/40·ADX10 (예시 파라미터 — 백테스트로 보정)
PARAMS={'kospi200':dict(ma_s=20,ma_l=60,adx_n=14),
        'kosdaq150':dict(ma_s=10,ma_l=40,adx_n=10)}

for name in ['kospi200','kosdaq150']:
    df=pd.read_csv(f'{SAVE_DIR}/{name}_combined.csv', index_col='date', parse_dates=True)
    d=label(add_indicators(df, **PARAMS[name]))
    d.to_csv(f'{SAVE_DIR}/{name}_labeled.csv', encoding='utf-8-sig')
    print(f'\n[{name}] 국면 분포'); print(d['regime'].value_counts().to_string())
```

출력(국면 분포):

```
[kospi200] 국면 분포
regime
중립전이     786
횡보_상단    620
횡보_중단    606
약한상승     500
강한하락     469
강한상승     407
횡보_하단    404
약한하락     190
-         59

[kosdaq150] 국면 분포
regime
-        1378
중립전이      831
강한하락      489
강한상승      318
약한상승      301
횡보_중단     287
횡보_상단     239
횡보_하단     109
약한하락       89
```

각 지표가 자리 잡으려면 워밍업 구간이 필요하므로 초반은 `-`(미산출)로 빠진다. KOSDAQ150의 `-`가 KOSPI보다 훨씬 많은 것은 이 산출 구간 차이에서 비롯된 것으로, *국면 비율을 비교하려면* 공통의 유효 구간으로 잘라 다시 세야 한다([국면 분류 편](/portfolio/investing/stock/practice/part-02-market-regimes/) "분포는 가정 말고 측정"의 실제 적용).

### 라벨링 다음 단계

이 코드는 9단계 중 1·3·4까지다. 남은 2·5~8단계를 [엔진 편](/portfolio/investing/stock/practice/part-10-backtest-engine/)에서 코드로 잇는다. 핵심은 다음과 같다.

- **2단계(미래참조 차단):** 지금은 같은 날 데이터로 라벨을 만들지만, 실거래·정직한 백테스트에서는 신호를 *전일(t−1)* 로 미뤄야 한다. 특히 수급 확정값은 장 마감 후(15:35·18:00)에 나오므로 **종가 매매 시점엔 그날 `flow`를 쓸 수 없다** → `flow`는 반드시 하루 이상 지연시켜 사용.
- **5~7단계:** 비용(수수료·스프레드·세금)과 B 모드 리밸런싱 규칙을 넣어 손익을 시뮬레이션하고, 단순 보유·정적 50:50·전액 현금과 비교한 뒤 [성과 지표 편](/portfolio/investing/stock/practice/part-06-position-and-metrics/) 지표로 평가.
- **8~9단계:** 학습/검증 분할로 임계값을 *고원형*으로 고르고, KOSPI·KOSDAQ 임계값 표를 따로 만든다. 손익 검증은 지수가 아니라 *실제 4개 ETF 가격*으로(인버스 decay·베이시스 반영).
