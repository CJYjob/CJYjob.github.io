---
title: "투자 실습 ⑫ 모의·실전 운용과 복기"
date: 2026-06-09
draft: false
description: "모의투자에서 실전으로 넘어갈 때의 기록 방법과 복기 루프, 실전 매매 로그 연결을 정리한다."
categories: ["Investment"]
tags: ["Investment", "ETF"]
---

> 학습 정리 노트 — 매수·매도 권유가 아니다.

## 이 편의 위치

설계([백테스트 설계 편](/portfolio/investing/stock/strategy/part-08-backtest-design/))·검증 코드([구현 편](/portfolio/investing/stock/practice/part-09-implementation/)·[엔진 편](/portfolio/investing/stock/practice/part-10-backtest-engine/))·[자동매매 편](/portfolio/investing/stock/practice/part-11-automation/)까지 마친 전략을 실제 계좌에서 돌리고 기록하는 단계다. 목표는 단기 수익이 아니라, 검증된 구간에서만 참여하고 모든 판단을 기록해 복기하는 습관을 만드는 것이다.

## 모의 → 실전 순서

```text
모의투자로 규칙 집행을 검증
→ 소액 실전으로 전환
→ 매매마다 기록
→ 정기 복기
→ 규칙 보정
→ 재검증(백테스트/모의)
```

규칙을 손실 직후 즉흥적으로 바꾸지 않는다. 규칙 수정은 충분한 표본, 반복된 동일 문제, 과정 오류 확인, 백테스트·실전 차이의 설명 가능성, 수정 후 재검증 가능성을 만족할 때만 한다([리스크와 예외 조건 편](/portfolio/investing/stock/strategy/part-07-risk-and-exceptions/) 참조).

## 진입 전 최소 기록

아래 항목 중 하나라도 비어 있으면 매매를 보류한다.

```text
1. 현재 국면 판단(지수별)
2. 선택한 ETF 방향(정방향/인버스/현금)
3. 진입 이유
4. 비중 결정 이유
5. 종료 조건
6. 예외 조건 해당 여부
```

## 매매 후 기록

```text
체결가 · 체결 수량 · 체결 후 비중 · 예상/실제 비용 · 결과(손익) · 미체결/오류 사유
```

## 복기 루프

복기는 손익을 평가하는 자리가 아니라 과정을 점검하는 자리다.

```text
국면 판단이 규칙대로였나
→ 진입/종료가 기록된 조건을 따랐나
→ 예외 조건을 지켰나
→ 비용·회전율이 설명되나
→ 다음 규칙 보정이 필요한가
```

## 기록은 어디에 두나

완결된 학습은 이 시리즈(Portfolio)에 두고, 진행 중인 원시 매매·복기 기록은 Log에 누적한다. 실제 일자별 기록은 **[ETF 실전 매매 기록 로그](/log/etf-live-trading/)** 에 쌓는다.
