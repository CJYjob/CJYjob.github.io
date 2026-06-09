---
title: "투자 실습 ⑪ 자동매매와 운용 원칙"
date: 2026-06-09
draft: false
description: "데이터→신호→주문→기록 자동매매 흐름과 키움 REST API 실행, 영어 용어·핵심 요약 부록."
categories: ["Investment"]
tags: ["Investment", "ETF"]
---

## 자동매매 실행 (키움)

(자동화의 흐름 — 데이터→신호→주문→기록→모니터링 — 은 [투자 기초 ⑥](/portfolio/investing/stock/theory/part-06-derivatives-etf-mechanism/)에서 다뤘다. 여기서는 실행 수단만.)

- **키움 REST API(2025 출시):** 웹 기반, Windows/Mac/Linux 지원, 미리 설정한 기준 도달 시 자동 매매·리밸런싱 구현 가능. (구형 Open API+는 윈도우 전용 OCX.)
- **사용 조건:** 키움 증권계좌 → 홈페이지에서 API 사용 신청 → 앱키(App Key)·시크릿(App Secret) 발급 → 토큰으로 호출(IP 화이트리스트 적용). 자동매매는 거래소 규정상 *알고리즘 계좌 등록*이 따를 수 있음. *모의투자* 환경으로 실거래 전 검증. API 자체는 무료, 매매 위탁수수료는 통상 적용.
- 우리 전략(일 1회 종가·비중 리밸런싱)은 일봉 신호 계산 → 종가 무렵 비중 맞춰 주문이라 REST API로 충분히 자동화 가능. *모의투자 → 실거래* 순서로.

## 부록 A. 영어 용어 풀이(어원 포함)

| 용어 | 우리말 / 뜻 | 비고 |
|---|---|---|
| ETF (Exchange-Traded Fund) | 상장지수펀드 | 거래소에서 거래되는 펀드 |
| NAV (Net Asset Value) | 순자산가치 | 담은 자산의 1주당 실제 가치 |
| AP (Authorized Participant) | 지정참가회사 | 설정/환매 권한 |
| LP (Liquidity Provider) | 유동성공급자 | 호가창에 매수·매도 호가 제공 |
| SMA / EMA | 단순/지수 이동평균 | EMA는 최근 가중 |
| BB (Bollinger Bands) | 볼린저밴드 | 중심 ±2σ |
| %B | 밴드 내 위치 | (가격−하단)/(상단−하단), B=Bands |
| Bandwidth | 밴드 폭 | 4σ/SMA, 상대 변동성 |
| ADX (Average Directional Index) | 평균방향지수 | 추세 *강도*(방향 무관) |
| ATR (Average True Range) | 평균 실제 변동폭 | ₩ 절대 변동성 |
| MACD (Moving Average Convergence Divergence) | 이동평균 수렴·확산 | 방향+모멘텀 |
| RSI (Relative Strength Index) | 상대강도지수 | 과매수/과매도 |
| ROC (Rate of Change) | 변화율 | N일 수익률 |
| z-score | 표준점수 | 평균에서 표준편차 몇 배 |
| Cost of carry | 보유비용 | 이자 − 배당 |
| Basis | 베이시스 | 선물 − 현물 |
| Contango | 콘탱고 | 선물>현물. 어원: 런던 거래소 결제 *이연 수수료*(이월·보유 비용) |
| Backwardation | 백워데이션 | 선물<현물. 어원: 콘탱고의 반대, 가격이 "뒤로 꺾임" |
| Quadruple Witching | 네 마녀의 날 | 선물·옵션 동시 만기일 |
| Roll-over | 롤오버 | 근월물→차월물 교체 |
| Slippage | 슬리피지 | 의도가-체결가 차이 |
| TER (Total Expense Ratio) | 총보수 | 보유 중 차감되는 연 비용 |
| CAGR / MDD | 연복리수익 / 최대낙폭 | |
| Sharpe / Sortino / Calmar | 위험조정 수익 지표 | |
| Whipsaw | 휩소 | 추세인 줄 알았다 뒤집히는 속임수 |
| Capitulation | 투매 | 공포성 대량 매도(바닥 신호) |

## 부록 B. 핵심 한 줄 요약

- 양방향을 겹쳐 드는 *헤지 자체는 비용*. 수익은 **방향(A)** 또는 **변동성 수확(B)** 에서 나온다.
- **전환 = 추세인지 횡보인지 판별**. 추세장 = 현금 + 주력 한 방향(A), 횡보장 = 양방향 + 리밸런싱(B).
- 판별 4지표: **SMA 배열 · ADX · BB %B · 수급 z-점수**. 모멘텀·차익/비차익·베이시스는 *나중에* 필요한 만큼만 추가(과적합 경계).
- 인버스는 *과세·선물지수 추종·decay* → 회전 최소화, 백테스트는 *실제 ETF 가격*으로.
- 국면 분포·임계값은 *가정 말고 백테스트로*, KOSPI·KOSDAQ 따로.
- **검증되지 않은 방향 판단 + 레버리지 = 가장 빠르게 깨지는 조합.** 모의투자·백테스트로 "동전 던지기보다 나은지" 먼저 증명.
