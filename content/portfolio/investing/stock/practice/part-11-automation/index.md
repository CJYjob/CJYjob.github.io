---
title: "투자 실습 ⑪ 자동매매와 운용 원칙"
date: 2026-06-09
draft: false
description: "데이터→신호→주문→기록 자동매매 흐름과 키움 REST API 실행."
categories: ["Investment"]
tags: ["Investment", "ETF"]
---

## 자동매매 실행 (키움)

(자동화의 흐름 — 데이터→신호→주문→기록→모니터링 — 은 [투자 기초 ⑥](/portfolio/investing/stock/theory/part-06-derivatives-etf-mechanism/)에서 다뤘다. 여기서는 실행 수단만.)

- **키움 REST API(2025 출시):** 웹 기반, Windows/Mac/Linux 지원, 미리 설정한 기준 도달 시 자동 매매·리밸런싱 구현 가능. (구형 Open API+는 윈도우 전용 OCX.)
- **사용 조건:** 키움 증권계좌 → 홈페이지에서 API 사용 신청 → 앱키(App Key)·시크릿(App Secret) 발급 → 토큰으로 호출(IP 화이트리스트 적용). 자동매매는 거래소 규정상 *알고리즘 계좌 등록*이 따를 수 있음. *모의투자* 환경으로 실거래 전 검증. API 자체는 무료, 매매 위탁수수료는 통상 적용.
- 우리 전략(일 1회 종가·비중 리밸런싱)은 일봉 신호 계산 → 종가 무렵 비중 맞춰 주문이라 REST API로 충분히 자동화 가능. *모의투자 → 실거래* 순서로.
