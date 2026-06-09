---
title: "투자 실습"
date: 2026-06-09
draft: false
description: "투자 이론을 코스피200·코스닥150 정방향/인버스 ETF 전략으로 구현한다. 전략 논리·국면 지표·상품 메커니즘·운용·리스크·백테스트·코드·자동매매·실전 기록까지."
categories: ["Portfolio", "Investment"]
tags: ["Investment", "ETF", "System Trading", "Backtest"]
weight: 20
ShowToc: true
TocOpen: true
cascade:
  - weight: 10
    summary: "양방향 보유의 실체와 수익 원천(방향 A / 변동성 수확 B)."
    target: { path: "{/portfolio/investing/stock/practice/part-01-foundation-and-edge,/portfolio/investing/stock/practice/part-01-foundation-and-edge/**}" }
  - weight: 20
    summary: "추세·횡보 1차 축과 5단계 국면, KOSPI·KOSDAQ 차이, 하락 비대칭."
    target: { path: "{/portfolio/investing/stock/practice/part-02-market-regimes,/portfolio/investing/stock/practice/part-02-market-regimes/**}" }
  - weight: 30
    summary: "국면 판별 지표 6분류와 선택한 4개(SMA·ADX·BB %B·수급 z-score)."
    target: { path: "{/portfolio/investing/stock/practice/part-03-regime-indicators,/portfolio/investing/stock/practice/part-03-regime-indicators/**}" }
  - weight: 40
    summary: "외국인·기관 수급 읽기와 정규화(시총 대비·z-점수)."
    target: { path: "{/portfolio/investing/stock/practice/part-04-supply-demand,/portfolio/investing/stock/practice/part-04-supply-demand/**}" }
  - weight: 50
    summary: "ETF 가격 메커니즘, 선물·베이시스·콘탱고, 비용과 세금 비대칭."
    target: { path: "{/portfolio/investing/stock/practice/part-05-etf-futures-cost,/portfolio/investing/stock/practice/part-05-etf-futures-cost/**}" }
  - weight: 60
    summary: "국면별 포지션 비중과 위험조정 성과 지표."
    target: { path: "{/portfolio/investing/stock/practice/part-06-position-and-metrics,/portfolio/investing/stock/practice/part-06-position-and-metrics/**}" }
  - weight: 70
    summary: "진입 전 거르는 리스크·예외 조건과 인버스 사용 원칙."
    target: { path: "{/portfolio/investing/stock/practice/part-07-risk-and-exceptions,/portfolio/investing/stock/practice/part-07-risk-and-exceptions/**}" }
  - weight: 80
    summary: "미래참조 차단·비용·과적합 방지를 포함한 백테스트 9단계 설계."
    target: { path: "{/portfolio/investing/stock/practice/part-08-backtest-design,/portfolio/investing/stock/practice/part-08-backtest-design/**}" }
  - weight: 90
    summary: "pykrx 데이터 수집과 국면 라벨링 구현 코드."
    target: { path: "{/portfolio/investing/stock/practice/part-09-implementation,/portfolio/investing/stock/practice/part-09-implementation/**}" }
  - weight: 100
    summary: "미래참조 차단·비용/세금·검증을 담은 백테스트 엔진 코드."
    target: { path: "{/portfolio/investing/stock/practice/part-10-backtest-engine,/portfolio/investing/stock/practice/part-10-backtest-engine/**}" }
  - weight: 110
    summary: "데이터→신호→주문→기록 자동매매 구조와 운용 원칙."
    target: { path: "{/portfolio/investing/stock/practice/part-11-automation,/portfolio/investing/stock/practice/part-11-automation/**}" }
  - weight: 120
    summary: "모의·실전 매매와 복기 기록(/log 연결)."
    target: { path: "{/portfolio/investing/stock/practice/part-12-live-and-review,/portfolio/investing/stock/practice/part-12-live-and-review/**}" }
  - weight: 130
    summary: "ETF·지표·선물 용어 풀이(어원 포함)."
    target: { path: "{/portfolio/investing/stock/practice/appendix-glossary,/portfolio/investing/stock/practice/appendix-glossary/**}" }
  - weight: 140
    summary: "전략 전체를 한 장으로 줄인 핵심 요약."
    target: { path: "{/portfolio/investing/stock/practice/appendix-summary,/portfolio/investing/stock/practice/appendix-summary/**}" }
---

## 개요

[투자 이론](/portfolio/investing/stock/theory/part-01-market-structure/)에서 익힌 구조를 KODEX 200·인버스, KODEX 코스닥150·인버스에 적용한 실습 트랙이다.

`전략 논리 → 국면 도구 → 상품 메커니즘 → 운용·리스크 → 백테스트 설계·코드 → 자동매매 → 모의·실전 기록`
