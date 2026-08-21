---
title: "투자 전략 ⑧ 백테스트 설계"
date: 2026-06-09
draft: false
description: "미래참조 차단, 비용·세금 반영, 벤치마크 비교, 과적합 방지를 포함한 백테스트 9단계 절차를 정리한다."
categories:
  - "Investment"
series:
  - "Investment Strategy"
tags:
  - "Investment"
  - "ETF"
  - "Backtest"
weight: 80
aliases:
  - /portfolio/investing/stock/strategy/part-08-backtest-design/
---

## 백테스트 설계

(백테스트·과최적화의 *개념*은 [투자 기초 ⑥](/ko/portfolio/investment-theory-06-derivatives-etf-mechanism/)에서 다뤘다. 여기서는 이 전략에 맞춘 *절차*에 집중한다.)

- **데이터 출처:** **pykrx**(무료; 지수 OHLC[코스피200 = 코드 1028], 투자자별 거래실적을 금액·주식수로) / 키움 REST API / KRX 정보데이터시스템. 수급 *확정* 데이터는 KRX 기준 15:35·18:00에 나오므로 **종가 매매 시 그날 수급은 아직 없다**(미래참조 함정의 핵심).
- **9단계 절차:**
  1. 데이터 조립(일봉 OHLC + 외국인·기관 순매수; 다양한 국면을 담게 길게).
  2. **미래참조(look-ahead) 차단** — 신호는 *전일(t−1)* 확정 데이터로, 집행은 *당일(t) 종가*. (그날 데이터를 그날 신호에 쓰면 결과가 거짓으로 좋아짐.)
  3. 국면 분류(4지표 + 잠정 임계값으로 매일 5단계 라벨).
  4. 포지션 매핑(라벨 → 정방향/인버스/현금 비중).
  5. 비용 반영(수수료 + 스프레드/슬리피지 + 세금; B 모드 리밸런싱 비용이 결과를 좌우하니 필수).
  6. 손익 시뮬 + 벤치마크 비교(단순 보유 KODEX 200 / 정적 50:50 / 전액 현금).
  7. 성과지표([성과 지표 편](/ko/portfolio/investment-strategy-06-position-and-metrics/)).
  8. 임계값 최적화 + 과적합 방지(학습/검증 기간 분할, *살짝 다른 값에서도 통하는 고원형* 임계값 선택).
  9. 지수별 별도(KOSPI200·KOSDAQ150 각각 → 임계값 표 2벌).
- **백테스트 대상(확정안 ⓒ):** *지수*로 신호 견고성 검증 → *실제 4개 ETF 가격*으로 손익 검증(공통 상장 ~10년치, 현실적 비용·decay 반영). 인버스 다리는 반드시 실제 ETF 가격으로.
