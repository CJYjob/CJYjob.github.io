---
title: "투자 전략"
date: 2026-06-09
draft: false
description: "코스피200·코스닥150 양방향 ETF 전략의 설계: 수익 원천, 국면 분류, 판별 지표, 수급, 상품 메커니즘, 포지션, 리스크, 백테스트 설계."
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
    summary: "국면 판별 지표 6분류와 선택한 4개(SMA·ADX·BB %B·수급 z-score)."
    target: { path: "{/portfolio/investing/stock/strategy/part-03-regime-indicators,/portfolio/investing/stock/strategy/part-03-regime-indicators/**}" }
  - weight: 40
    summary: "외국인·기관 수급 읽기와 정규화(시총 대비·z-점수)."
    target: { path: "{/portfolio/investing/stock/strategy/part-04-supply-demand,/portfolio/investing/stock/strategy/part-04-supply-demand/**}" }
  - weight: 50
    summary: "ETF 가격 메커니즘, 선물·베이시스·콘탱고, 비용과 세금 비대칭."
    target: { path: "{/portfolio/investing/stock/strategy/part-05-etf-futures-cost,/portfolio/investing/stock/strategy/part-05-etf-futures-cost/**}" }
  - weight: 60
    summary: "국면별 포지션 비중과 위험조정 성과 지표."
    target: { path: "{/portfolio/investing/stock/strategy/part-06-position-and-metrics,/portfolio/investing/stock/strategy/part-06-position-and-metrics/**}" }
  - weight: 70
    summary: "진입 전 거르는 리스크·예외 조건과 인버스 사용 원칙."
    target: { path: "{/portfolio/investing/stock/strategy/part-07-risk-and-exceptions,/portfolio/investing/stock/strategy/part-07-risk-and-exceptions/**}" }
  - weight: 80
    summary: "미래참조 차단·비용·과적합 방지를 포함한 백테스트 9단계 설계."
    target: { path: "{/portfolio/investing/stock/strategy/part-08-backtest-design,/portfolio/investing/stock/strategy/part-08-backtest-design/**}" }
  - weight: 90
    summary: "ETF·지표·선물 용어 풀이(어원 포함)."
    target: { path: "{/portfolio/investing/stock/strategy/appendix-glossary,/portfolio/investing/stock/strategy/appendix-glossary/**}" }
  - weight: 100
    summary: "전략 전체를 한 장으로 줄인 핵심 요약."
    target: { path: "{/portfolio/investing/stock/strategy/appendix-summary,/portfolio/investing/stock/strategy/appendix-summary/**}" }
---

## 개요

[투자 이론](/portfolio/investing/stock/theory/part-01-market-structure/)의 토대 위에서, 코스피200·코스닥150 정방향/인버스 ETF로 운용할 전략을 설계한다. 이 트랙은 "왜·무엇"(설계)이고, 실제 코드 구현·검증은 [투자 실습](/portfolio/investing/stock/practice/part-09-implementation/)에서 다룬다.

`수익 원천 → 국면 분류 → 판별 지표 → 수급 → 상품 메커니즘 → 포지션·성과 → 리스크 → 백테스트 설계`
