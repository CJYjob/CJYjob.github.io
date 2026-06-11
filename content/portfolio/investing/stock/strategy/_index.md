---
title: "투자 전략"
date: 2026-06-09
draft: false
description: "코스피200·코스닥150 양방향 ETF 전략의 설계: 수익 원천, 국면 분류, 지표 선택, 수급 활용, 상품 구조 반영, 포지션, 리스크, 백테스트 설계."
categories: ["Portfolio", "Investment"]
tags: ["Investment", "ETF", "Strategy"]
weight: 15
ShowToc: true
TocOpen: true
cascade:
  - weight: 10
    summary: "양방향 보유의 실체와 수익 원천(방향 A / 변동성 수확 B)."
    target: { path: "{/portfolio/investing/stock/strategy/part-01-foundation-and-edge,/portfolio/investing/stock/strategy/part-01-foundation-and-edge/**}" }
  - weight: 20
    summary: "추세·횡보 1차 축과 5단계 국면, KOSPI·KOSDAQ 차이, 하락 비대칭."
    target: { path: "{/portfolio/investing/stock/strategy/part-02-market-regimes,/portfolio/investing/stock/strategy/part-02-market-regimes/**}" }
  - weight: 30
    summary: "국면 판별에 쓸 지표 4개(SMA·ADX·BB %B·수급 z)와 선택 이유."
    target: { path: "{/portfolio/investing/stock/strategy/part-03-regime-indicators,/portfolio/investing/stock/strategy/part-03-regime-indicators/**}" }
  - weight: 40
    summary: "수급을 방향 신호로 쓰는 법(금액 z 우선·비차익만·만기 주 신뢰도·KOSDAQ 보조)."
    target: { path: "{/portfolio/investing/stock/strategy/part-04-supply-demand,/portfolio/investing/stock/strategy/part-04-supply-demand/**}" }
  - weight: 50
    summary: "ETF·선물·세금 구조를 전략에 반영(인버스는 실제 ETF 가격으로, 세금 비대칭 운영)."
    target: { path: "{/portfolio/investing/stock/strategy/part-05-etf-futures-cost,/portfolio/investing/stock/strategy/part-05-etf-futures-cost/**}" }
  - weight: 60
    summary: "국면별 포지션 비중과 변동성 수확, MDD·샤프 중심 평가."
    target: { path: "{/portfolio/investing/stock/strategy/part-06-position-and-metrics,/portfolio/investing/stock/strategy/part-06-position-and-metrics/**}" }
  - weight: 70
    summary: "진입 전 거르는 리스크·예외 조건과 인버스 사용 원칙."
    target: { path: "{/portfolio/investing/stock/strategy/part-07-risk-and-exceptions,/portfolio/investing/stock/strategy/part-07-risk-and-exceptions/**}" }
  - weight: 80
    summary: "미래참조 차단·비용·과적합 방지를 포함한 백테스트 9단계 설계."
    target: { path: "{/portfolio/investing/stock/strategy/part-08-backtest-design,/portfolio/investing/stock/strategy/part-08-backtest-design/**}" }
---

## 개요

[투자 이론](/portfolio/investing/stock/theory/)의 토대 위에서, 코스피200·코스닥150 정방향/인버스 ETF로 운용할 전략을 설계한다. 이 트랙은 "왜·무엇"(설계)이고, 실제 코드 구현·검증은 [투자 실습](/portfolio/investing/stock/practice/part-09-implementation/)에서 다룬다. 지표·상품·수급의 *정의와 원리*는 모두 이론 트랙에 있고, 여기서는 그것을 *어떻게 활용할지*만 정한다.

`수익 원천 → 국면 분류 → 지표 선택 → 수급 활용 → 상품 구조 반영 → 포지션·성과 → 리스크 → 백테스트 설계`

## 핵심 요약

- 양방향을 겹쳐 드는 헤지 자체는 비용이다. 수익은 방향(A) 또는 변동성 수확(B)에서 나온다.
- 전환은 곧 추세인지 횡보인지를 판별하는 일이다. 추세장은 현금 + 주력 한 방향(A), 횡보장은 양방향 + 리밸런싱(B).
- 판별에 쓰는 4지표는 SMA 배열 · ADX · BB %B · 수급 z-점수다. 모멘텀·비차익·베이시스는 나중에 필요한 만큼만 더한다(과적합 경계).
- 인버스는 과세·선물지수 추종·변동성 손실 때문에 회전을 최소화하고, 백테스트는 실제 ETF 가격으로 한다.
- 국면 분포·임계값은 가정하지 말고 백테스트로 정하며, KOSPI·KOSDAQ을 따로 본다.
- 검증되지 않은 방향 판단에 레버리지를 더하면 가장 빠르게 깨진다. 모의투자·백테스트로 "동전 던지기보다 나은지"를 먼저 증명한다.
