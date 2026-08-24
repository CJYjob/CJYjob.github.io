---
title: "서버 애플리케이션 구조 읽기 - 학습 목차"
date: 2026-08-24
draft: false
description: "JVM 기반 서버 애플리케이션의 런타임, 영속성, 캐시, 콘텐츠 전달, 계층 구조를 일반적인 예제로 학습한 기록"
categories: ["security", "development"]
tags: ["backend", "architecture", "jvm", "cache"]
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

## 일반적인 요청 흐름

`클라이언트 → 백엔드 애플리케이션 → Controller → Service → Repository → DB`

대용량 정적 콘텐츠를 제공하는 시스템에서는 API 서버와 별도로 CDN 같은 콘텐츠 전달 계층을 둘 수 있다. Redis 같은 캐시 계층은 반드시 필요한 구성 요소가 아니라 실제 부하와 요구사항에 따라 선택적으로 추가한다.

## 진행 상태

미완결 학습 로그다. 현재는 각 구성 요소의 역할과 데이터 흐름을 이해하는 단계이며, 이후 실제 테스트베드의 요청 하나를 추적하면서 보안 관점의 검증 포인트와 연결한다.
