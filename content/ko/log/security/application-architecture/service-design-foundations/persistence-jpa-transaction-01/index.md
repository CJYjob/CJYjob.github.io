---
title: "영속성, JPA와 트랜잭션"
date: 2026-08-24
draft: false
description: "영속성, JPA 계층과 읽기 중심 트랜잭션 선언의 의미를 정리한 학습 로그"
categories: ["security", "development"]
tags: ["persistence", "jpa", "transaction", "database"]
---

[전체 목차로 돌아가기](../overview-01/)

## 영속성

영속성(Persistence)은 프로세스가 종료된 뒤에도 필요한 데이터가 남아 다시 사용될 수 있는 성질과 그 처리 영역을 말한다. 메모리에만 존재하는 객체와 DB 등에 저장된 데이터를 구분하는 핵심 개념이다.

## JPA

JPA는 Java Persistence API의 약자이며 JVM 애플리케이션에서 객체와 관계형 데이터베이스 사이의 영속성 처리를 위한 표준 명세다. JPA 자체가 하나의 DB 제품은 아니며 실제 동작은 JPA 구현체가 담당한다.

Spring Data JPA 같은 데이터 접근 계층은 JPA를 활용해 repository 추상화와 쿼리 작성 편의 기능을 제공한다. 최종적으로는 DB가 이해하는 SQL과 트랜잭션으로 이어진다.

`Service → Repository → 데이터 접근 계층/JPA 구현체 → DB 드라이버 → DB`

## 읽기 중심 트랜잭션

`@Transactional(readOnly=true)`와 같은 선언은 읽기 중심 트랜잭션이라는 의도를 프레임워크에 전달하는 메타데이터다. 구현과 환경에 따라 flush나 변경 감지 등의 동작 최적화에 활용될 수 있다.

이를 데이터 변경을 절대적으로 막는 보안 장치로 이해하면 안 된다. 실제 보장은 DB, 드라이버, 트랜잭션 매니저와 설정에 따라 달라질 수 있다.

## 공격자 관점

- 사용자 입력이 동적 쿼리까지 전달되는 경로
- 과도한 데이터 노출
- 트랜잭션 경계 오류로 인한 정합성 문제

## 방어자 관점

- 안전한 파라미터 바인딩
- DTO와 영속 모델의 책임 분리
- DB 계정 최소 권한
- 읽기와 쓰기의 트랜잭션 경계 명확화
