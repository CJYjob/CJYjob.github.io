---
title: "서버 애플리케이션 구조 읽기 - 학습 목차"
date: 2026-08-24
draft: false
description: "JVM 기반 서버 애플리케이션의 런타임, 영속성, 캐시, 계층 구조, 요청 인증, 데이터 모델과 API 처리 흐름을 일반적인 예제로 학습한 기록"
categories: ["security", "development"]
tags: ["backend", "architecture", "jvm", "cache", "authentication"]
---

## 학습 목적

서버 애플리케이션의 기술 설계를 읽을 때 특정 서비스나 조직의 구성을 재현하지 않고, 일반적인 백엔드 구조 안에서 각 기술의 역할과 보안 경계를 이해한다.

## 전체 목차

1. [JVM 언어·JDK와 런타임](../java-jvm-runtime-01/)
2. [영속성, JPA와 트랜잭션](../persistence-jpa-transaction-01/)
3. [DNS 이름과 소스 저장소 용어 구분](../domain-repository-naming-01/)
4. [Redis 캐시와 DB 직접 조회](../redis-cache-01/)
5. [CDN·콘텐츠 패키징·비트레이트](../content-delivery-audio-01/)
6. [패키지와 애플리케이션 계층](../package-layering-01/)
7. [Spring, MVC, 객체 연결과 DI](../spring-mvc-di-01/)
8. [HMAC 요청 인증과 Replay 방어](../hmac-request-authentication-01/)
9. [관계형 데이터 모델 읽기](../relational-data-model-01/)
10. [HTTP API 명세와 요청 처리 흐름](../http-api-flow-01/)
11. [기능 요구사항을 SQL 필터로 변환하기](../relational-filter-query-01/)
12. [서명 URL과 콘텐츠 전달 경계](../signed-resource-delivery-01/)
13. [단위·통합 테스트와 의존성 대체](../application-testing-01/)
14. [모바일 API 취약점 점검 준비](../mobile-api-assessment-preparation-01/)

## 일반적인 요청 흐름

`클라이언트 → 백엔드 애플리케이션 → Controller → Service → Repository → DB`

대용량 정적 콘텐츠를 제공하는 시스템에서는 API 서버와 별도로 CDN 같은 콘텐츠 전달 계층을 둘 수 있다. Redis 같은 캐시 계층은 반드시 필요한 구성 요소가 아니라 실제 부하와 요구사항에 따라 선택적으로 추가한다.

요청 인증이 필요한 시스템에서는 Controller에 도달하기 전이나 요청 처리 초기에 서명, 시간 조건, 일회성 값 등의 검증을 수행할 수 있다. 이 인증 계층과 최종 사용자의 로그인·권한 검사는 목적이 다를 수 있으므로 별도로 구분해 읽는다.

데이터 모델과 API 명세를 함께 읽으면 저장 구조가 외부 응답 객체로 어떻게 변환되는지, 관계형 데이터의 연결이 조회 조건으로 어떻게 사용되는지 추적할 수 있다. 기능 요구사항을 SQL로 읽을 때는 문법부터 보지 않고 `기능 조건 → 후보 행 제한 → 관계 연결 → 그룹화 → 그룹 조건 검사 → 결과 선택` 순서로 변환 과정을 추적한다.

## 진행 상태

미완결 학습 로그다. 서버 애플리케이션의 구성 요소와 데이터 흐름, 요청 인증, 관계형 데이터 모델, API 처리, 조건부 조회, 외부 콘텐츠 전달, 테스트 전략까지 설계 문서를 읽는 기본 프레임을 확장했다. 이어서 실제 점검에 들어가기 전 대상 환경·앱 자산·인증 자격정보·권한 차이·프록시 가능 여부를 확인하는 사전 준비 절차를 정리했다. 다음 단계는 허가된 점검 환경과 대상 자산을 확정한 뒤 정상 요청 기준선을 확보하는 것이다.
