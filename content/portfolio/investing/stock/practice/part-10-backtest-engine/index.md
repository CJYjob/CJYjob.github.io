---
title: "투자 실습 ⑩ 백테스트 엔진·검증"
date: 2026-06-09
draft: false
description: "미래참조 차단·실제 ETF 가격·비용/세금·벤치마크·성과지표·임계값 검증을 담은 백테스트 엔진 코드."
categories: ["Investment"]
tags: ["Investment", "ETF"]
---

## 백테스트 엔진 — 손익·비용·검증 (셀 5~8)

[구현 편](/portfolio/investing/stock/practice/part-09-implementation/)이 9단계 절차의 **1·3·4**(데이터 조립·국면 분류·포지션 매핑)였다면, 이 장은 남은 **2(미래참조 차단)·5(비용)·6(손익·벤치마크)·7(성과지표)·8(임계값 검증)** 을 코드로 채운다. 백테스트·과적합의 *개념*은 [투자 기초 ⑥](/portfolio/investing/stock/theory/part-06-derivatives-etf-mechanism/)에서, 위험조정 지표는 [성과 지표 편](/portfolio/investing/stock/practice/part-06-position-and-metrics/)에서 이미 다뤘으므로 여기서는 이 전략에 맞춘 *집행*에 집중한다.

설계의 핵심 두 가지를 코드로 못박는다.

첫째, **미래참조(look-ahead) 차단**이다. 종가에 체결하는 포지션은 그 시점에 *이미 확정된* 정보만 써야 한다. 가격 신호는 전일(t−1) 기준으로 당일(t) 종가에 집행하고(`exec_lag=1`), 수급은 장 마감 후(KRX 기준 15:35·18:00)에 공시되므로 지표 계산 전에 하루 더 지연시킨다(`flow_lag=1`). 셀 4의 라벨은 *같은 날* 데이터로 만든 설명용이라, 손익 검증에서는 이 두 지연을 적용해 다시 라벨링한다.

둘째, **손익은 실제 ETF 가격으로** 계산한다. 인버스는 현물 지수가 아니라 F-지수(선물)를 추종하고 일일 −1배 리밸런싱의 decay가 끼므로, 지수에 −1배를 곱하면 맞지 않는다([메커니즘 편](/portfolio/investing/stock/practice/part-05-etf-futures-cost/)). 신호는 지수로 만들되 손익은 4개 ETF의 실제 가격으로 계산한다.

### 셀 5 — 실제 ETF 일봉 수집 (손익 검증용)

이름으로 종목코드를 자동 탐색한다(주석의 코드는 확인용 기본값). KODEX 200 = 069500, KODEX 인버스 = 114800, KODEX 코스닥150 = 229200, KODEX 코스닥150선물인버스 = 251340.

```python
# ===== 셀 5: 실제 ETF 일봉 수집 (손익 검증용) =====
ETF = {  # 지수 → (정방향, 인버스)
    'kospi200':  ('KODEX 200', 'KODEX 인버스'),                   # 069500 / 114800
    'kosdaq150': ('KODEX 코스닥150', 'KODEX 코스닥150선물인버스'),  # 229200 / 251340
}
name2code = {stock.get_etf_ticker_name(t).replace(' ',''): t
             for t in stock.get_etf_ticker_list(END)}
def resolve(name): return name2code.get(name.replace(' ',''))

def fetch_etf(code, tag):
    df = stock.get_market_ohlcv(START, END, code).rename(
        columns={'시가':'open','고가':'high','저가':'low','종가':'close','거래량':'volume'})
    df.index.name='date'
    df.to_csv(f'{SAVE_DIR}/{tag}.csv', encoding='utf-8-sig')
    print(f'[{tag}] {code} {df.shape} {df.index.min().date()}~{df.index.max().date()}')
    return df['close']

ETF_PX = {}
for idxname,(lname,iname) in ETF.items():
    lc, ic = resolve(lname), resolve(iname)
    print(idxname, '→ 정방향', lname, lc, '/ 인버스', iname, ic)
    ETF_PX[idxname] = (fetch_etf(lc, f'{idxname}_etf_long'),
                       fetch_etf(ic, f'{idxname}_etf_inv'))
```

인버스 ETF는 상장이 늦어(코스닥150선물인버스는 2016년 무렵) 손익 검증 구간이 지수보다 짧다 — 백테스트는 네 가격이 모두 존재하는 공통 구간에서만 돈다.

### 셀 6 — 백테스트 엔진 (미래참조 차단·비용·세금)

비용·세금 모델은 [메커니즘 편](/portfolio/investing/stock/practice/part-05-etf-futures-cost/)의 비대칭을 그대로 반영한다. 거래된 금액에 수수료+슬리피지를 양변으로 물리고, **인버스 다리를 줄일 때(매도) 실현이익에만** 15.4%를 매긴다(정방향은 비과세라 거래비용만). 리밸런싱은 국면이 바뀌거나 어느 다리든 비중 이탈이 밴드(기본 5%)를 넘을 때만 일어난다 — A 모드(추세)에서는 목표가 안정적이라 거의 거래하지 않고, 횡보(B 모드)에서는 출렁임에 따라 밴드를 넘나들며 변동성 수확이 자연히 일어난다.

```python
# ===== 셀 6: 백테스트 엔진 (미래참조 차단·비용·세금·리밸런싱 밴드) =====
import numpy as np, pandas as pd

WMAP = {  # 국면 → (정방향 w_long, 인버스 w_inv);  현금 = 1 - w_long - w_inv
 '강한상승':(0.90,0.00),'약한상승':(0.65,0.00),
 '횡보_상단':(0.45,0.55),'횡보_중단':(0.50,0.50),'횡보_하단':(0.55,0.45),
 '약한하락':(0.00,0.65),'강한하락':(0.00,0.90),'중립전이':(0.35,0.35),'-':(0.00,0.00)}

def backtest(px_long, px_inv, regime, commission=0.00015, slippage=0.0005,
             tax=0.154, exec_lag=1, rebal_band=0.05, init_capital=1.0):
    idx=regime.index
    pl=px_long.reindex(idx).ffill().values.astype(float)
    pi=px_inv.reindex(idx).ffill().values.astype(float)
    reg=regime.values
    # look-ahead 차단②: 목표비중을 1일 지연 집행(전일 신호 → 당일 종가 체결)
    wl=pd.Series([WMAP.get(r,(0,0))[0] for r in reg],index=idx).shift(exec_lag).fillna(0).values
    wi=pd.Series([WMAP.get(r,(0,0))[1] for r in reg],index=idx).shift(exec_lag).fillna(0).values
    cash=init_capital; ul=ui=basis=0.0; cr=commission+slippage
    eq=np.empty(len(idx)); turn=np.zeros(len(idx)); last=(None,None)
    for t in range(len(idx)):
        if np.isnan(pl[t]) or np.isnan(pi[t]):
            eq[t]=cash+ul*(0 if np.isnan(pl[t]) else pl[t])+ui*(0 if np.isnan(pi[t]) else pi[t]); continue
        equity=cash+ul*pl[t]+ui*pi[t]
        cl=ul*pl[t]/equity if equity>0 else 0; ci=ui*pi[t]/equity if equity>0 else 0
        if (wl[t],wi[t])!=last or max(abs(cl-wl[t]),abs(ci-wi[t]))>rebal_band:
            tl,ti=equity*wl[t],equity*wi[t]; cl_,ci_=ul*pl[t],ui*pi[t]
            traded=abs(tl-cl_)+abs(ti-ci_)
            dl=tl-cl_; ul+=dl/pl[t]; cash-=dl              # 정방향(비과세)
            di=ti-ci_
            if di>0:                                       # 인버스 매수 → 평단 갱신
                add=di/pi[t]; basis=(basis*ui+di)/(ui+add) if (ui+add)>0 else 0.0
                ui+=add; cash-=di
            elif di<0:                                     # 인버스 매도 → 실현이익 과세
                sell=-di/pi[t]; realized=sell*(pi[t]-basis); ui-=sell; cash+=-di
                if realized>0: cash-=realized*tax
            cash-=traded*cr; turn[t]=traded/equity if equity>0 else 0; last=(wl[t],wi[t])
        eq[t]=cash+ul*pl[t]+ui*pi[t]
    return pd.Series(eq,index=idx), pd.Series(turn,index=idx)

def metrics(equity, turn=None, rf=0.0, ppy=252):
    eq=equity.dropna(); ret=eq.pct_change().dropna(); n=len(eq)
    if n<2 or eq.iloc[0]<=0:
        return dict(CAGR=np.nan,MDD=np.nan,Vol=np.nan,Sharpe=np.nan,Sortino=np.nan,Calmar=np.nan,Turnover=np.nan)
    yrs=n/ppy; cagr=(eq.iloc[-1]/eq.iloc[0])**(1/yrs)-1; dd=(eq/eq.cummax()-1).min()
    vol=ret.std()*np.sqrt(ppy); sharpe=((ret.mean()*ppy)-rf)/vol if vol>0 else np.nan
    dn=ret[ret<0].std()*np.sqrt(ppy); sortino=((ret.mean()*ppy)-rf)/dn if dn>0 else np.nan
    return dict(CAGR=cagr,MDD=dd,Vol=vol,Sharpe=sharpe,Sortino=sortino,
                Calmar=cagr/abs(dd) if dd<0 else np.nan,
                Turnover=(turn.sum()/yrs) if turn is not None else np.nan)

# 셀 4 라벨은 '같은 날' 기준(설명용). 손익 검증은 미래참조-안전 라벨로 다시 만든다.
def relabel_safe(index_name, params):
    raw=pd.read_csv(f'{SAVE_DIR}/{index_name}_combined.csv', index_col='date', parse_dates=True)
    return label(add_indicators(raw, flow_lag=1, **params))['regime']   # 셀 4의 함수 재사용
```

### 셀 7 — 지수별 실행 + 벤치마크 비교

신호는 지수로 만든 라벨, 손익은 ETF 가격. 단순보유(정방향)·정적 50:50·전액 현금과 나란히 둔다. [성과 지표 편](/portfolio/investing/stock/practice/part-06-position-and-metrics/)에서 강조했듯 수익률 한 줄이 아니라 MDD·샤프 같은 위험조정 지표를 함께 본다.

```python
# ===== 셀 7: 지수별 백테스트 실행 + 벤치마크 비교 =====
PARAMS={'kospi200':dict(ma_s=20,ma_l=60,adx_n=14),
        'kosdaq150':dict(ma_s=10,ma_l=40,adx_n=10)}
def fmt(m): return (f"CAGR {m['CAGR']*100:6.2f}% | MDD {m['MDD']*100:7.2f}% | "
                    f"Vol {m['Vol']*100:5.2f}% | Sharpe {m['Sharpe']:4.2f} | "
                    f"Calmar {m['Calmar']:4.2f} | 회전 {m['Turnover']:4.1f}x/yr")
for name in ['kospi200','kosdaq150']:
    reg=relabel_safe(name, PARAMS[name])
    pl,pi=ETF_PX[name]
    common=reg.index.intersection(pl.dropna().index).intersection(pi.dropna().index)
    reg=reg.loc[common]
    eq,turn=backtest(pl,pi,reg)
    bh=(pl.reindex(common).ffill()/pl.reindex(common).ffill().iloc[0])      # 단순보유(정방향)
    e55,_=backtest(pl,pi,pd.Series('횡보_중단',index=common))                # 정적 50:50
    print(f"\n[{name}] {common.min().date()}~{common.max().date()} ({len(common)}일)")
    print(f"  전략      : {fmt(metrics(eq,turn))}")
    print(f"  단순보유  : {fmt(metrics(bh))}")
    print(f"  정적50:50 : {fmt(metrics(e55))}")
    eq.to_csv(f'{SAVE_DIR}/{name}_equity.csv', encoding='utf-8-sig')
```

> **엔진 동작 검증(합성 데이터).** 아래는 실데이터 결과가 *아니라*, 추세·횡보가 섞이도록 만든 *합성* 가격으로 엔진이 의도대로 도는지 확인한 것이다. 방향 예측력이 없는 난수 데이터라 수익은 평범하지만, 전략이 **단순보유 대비 MDD·변동성을 크게 낮추는** 모습(양방향 전략이 노리는 바로 그 지표)이 그대로 나타난다. 실제 운용 판단은 반드시 실데이터·충분한 검증 뒤에 한다.

```
[CASE-A · 추세형 가정]  전략      CAGR  0.48% | MDD -34.96% | Vol  8.45% | Sharpe 0.10 | 회전 19.8x/yr
                        단순보유  CAGR -5.27% | MDD -61.23% | Vol 17.42% | Sharpe -0.22
                        정적50:50 CAGR -0.51% | MDD  -5.73% | Vol  0.79%
[CASE-B · 박스형 가정]  전략      CAGR  4.74% | MDD -23.66% | Vol  9.32% | Sharpe 0.54 | 회전 31.6x/yr
                        단순보유  CAGR  8.13% | MDD -57.62% | Vol 17.08% | Sharpe 0.54
                        정적50:50 CAGR  0.49% | MDD  -1.63% | Vol  0.78%
```

### 셀 8 — 임계값 민감도 + 학습/검증 분할 (8단계)

임계값은 *한 점 최댓값*이 아니라 *고원(plateau)* 에서 고른다. 앞 60%를 학습, 뒤 40%를 검증으로 나눠 같은 임계값이 양쪽에서 고르게 견디는지 본다.

```python
# ===== 셀 8: ADX 임계값 민감도 + 학습/검증 분할(과적합 점검) =====
def sharpe_for(reg, pl, pi):
    c=reg.index.intersection(pl.dropna().index).intersection(pi.dropna().index)
    eq,_=backtest(pl,pi,reg.loc[c]); return metrics(eq)['Sharpe']
name='kospi200'; pl,pi=ETF_PX[name]
raw=pd.read_csv(f'{SAVE_DIR}/{name}_combined.csv', index_col='date', parse_dates=True)
split=raw.index[int(len(raw)*0.6)]
print(f"분할 기준일: {split.date()} (앞=학습 / 뒤=검증)")
print(f"{'강상승ADX':>9}{'강하락ADX':>10}{'학습Sharpe':>12}{'검증Sharpe':>12}")
for up in (28,30,32):
    for dn in (23,25,27):
        d=add_indicators(raw, flow_lag=1, **PARAMS[name])
        reg=label(d, adx_strong_up=up, adx_strong_dn=dn)['regime']
        tr=reg[reg.index<split]; te=reg[reg.index>=split]
        print(f"{up:>9}{dn:>10}{sharpe_for(tr,pl,pi):>12.2f}{sharpe_for(te,pl,pi):>12.2f}")
print("→ 학습·검증 둘 다 안정적으로 양호한 구간을 고른다(한 점 최댓값이면 과적합).")
```

> **검증 출력(합성 데이터).** 8단계의 함정이 그대로 드러난다 — 학습 구간 Sharpe는 +0.4대인데 검증 구간은 −0.4대다. 학습에서 최고였던 임계값이 검증에서 최악일 수 있다는 뜻으로, *과거에 맞춘 값은 미래를 보장하지 않는다*는 것을 눈으로 보여준다.

```
분할 기준일: 2020-12-25 (앞=학습 / 뒤=검증)
 강상승ADX 강하락ADX  학습Sharpe  검증Sharpe
      28       23        0.43       -0.39
      30       25        0.43       -0.40
      32       23        0.41       -0.36
```

### 남은 단계

- **9단계(지수별 별도)** 는 `PARAMS`로 이미 분리되어 있다. 다음은 학습/검증으로 KOSPI200·KOSDAQ150 임계값 표를 각각 *데이터로* 확정하는 일이다.
- **정교화:** 비차익 수급 분리([수급 편](/portfolio/investing/stock/practice/part-04-supply-demand/)), 베이시스·차익잔고·만기 플래그([메커니즘 편](/portfolio/investing/stock/practice/part-05-etf-futures-cost/))를 국면 전이 *조기경보* 로 얹는다 — 단, 규칙이 늘면 과적합 위험도 늘므로 "최소 작동 모델 → 확장" 순서를 지킨다.
- **자동매매([자동매매 편](/portfolio/investing/stock/practice/part-11-automation/))로 연결:** 동일한 신호 계산을 매일 돌려 종가 무렵 목표비중대로 주문하면 된다. 일 1회 종가·비중 리밸런싱이라 키움 REST API로 충분하다.
