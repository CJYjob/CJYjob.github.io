---
title: "투자 실습"
date: 2026-06-09
draft: false
description: "투자 전략을 pykrx 데이터로 직접 구현하고 백테스트·검증·자동화·실전 기록까지 한 단계씩 따라가는 핸즈온 트랙."
categories: ["Portfolio", "Investment"]
tags: ["Investment", "ETF", "System Trading", "Backtest"]
weight: 20
ShowToc: true
TocOpen: true
cascade:
  - weight: 10
    summary: "pykrx 데이터 수집과 국면 라벨링 구현 코드."
    target: { path: "{/portfolio/investing/stock/practice/part-09-implementation,/portfolio/investing/stock/practice/part-09-implementation/**}" }
  - weight: 20
    summary: "미래참조 차단·비용/세금·검증을 담은 백테스트 엔진 코드."
    target: { path: "{/portfolio/investing/stock/practice/part-10-backtest-engine,/portfolio/investing/stock/practice/part-10-backtest-engine/**}" }
  - weight: 30
    summary: "데이터→신호→주문→기록 자동매매 구조와 운용 원칙."
    target: { path: "{/portfolio/investing/stock/practice/part-11-automation,/portfolio/investing/stock/practice/part-11-automation/**}" }
  - weight: 40
    summary: "모의·실전 매매와 복기 기록(/log 연결)."
    target: { path: "{/portfolio/investing/stock/practice/part-12-live-and-review,/portfolio/investing/stock/practice/part-12-live-and-review/**}" }
---

## 개요

[투자 전략](/portfolio/investing/stock/strategy/part-01-foundation-and-edge/)에서 설계한 규칙을 실제 코드로 옮겨, 데이터 수집부터 백테스트·검증·자동화·실전 기록까지 한 단계씩 직접 만들어 본다.

`데이터·라벨링 → 백테스트 엔진 → 자동매매 → 모의·실전 기록`
