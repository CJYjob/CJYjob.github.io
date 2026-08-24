---
title: "패키지와 애플리케이션 계층"
date: 2026-08-24
draft: false
description: "Controller, Service, Repository, Entity, DTO, Config의 역할과 데이터 흐름을 일반적인 예제로 정리한 학습 로그"
categories: ["security", "development"]
tags: ["controller", "service", "repository", "entity", "dto", "backend"]
---

[전체 목차로 돌아가기](../overview-01/)

## 패키지

Java/JVM 프로젝트에서 패키지는 코드의 논리적 네임스페이스다. 실제 프로젝트에서는 패키지 이름에 맞춘 디렉터리 구조를 사용하는 경우가 많지만 OS의 디렉터리 자체와 언어 차원의 패키지는 개념적으로 구분한다.

일반적인 역할 분리 예시는 다음과 같다.

```text
app/
├── controller/
├── service/
├── repository/
├── dto/
├── entity/
└── config/
```

## 가상 콘텐츠 조회 예시

사용자가 `GET /contents/123`처럼 특정 콘텐츠를 조회한다고 가정한다.

### Controller

HTTP 요청을 받는 진입점이다. URL, HTTP method, 요청 데이터를 애플리케이션의 메서드와 연결하고 Service에 처리를 요청한다.

### Service

업무 규칙을 처리한다. 조회 가능 여부, 상태 확인, 여러 데이터 조합 같은 비즈니스 판단을 수행할 수 있다.

### Repository

DB 조회와 저장 같은 데이터 접근을 추상화한다. Service가 필요한 영속 데이터를 가져오도록 데이터 접근 계층과 연결된다.

### Entity

JPA의 Entity는 단순한 `DB 행을 담는 DTO`가 아니라 **영속성 컨텍스트에서 식별성과 생명주기를 관리받는 도메인/영속 객체**다. 일반적으로 DB 테이블과 매핑되므로 처음에는 `DB에 저장되는 데이터 구조를 애플리케이션 객체로 표현한다`고 이해할 수 있지만, 핵심은 JPA가 이 객체의 상태를 추적하고 DB의 영속 상태와 연결한다는 데 있다.

예를 들어 JPA가 조회한 Entity의 특정 필드가 트랜잭션 안에서 변경되면, 관리 상태인 Entity의 변경을 감지해 적절한 시점에 UPDATE를 생성할 수 있다. 이를 변경 감지(dirty checking)라고 한다. 따라서 Entity는 단순 복사 데이터가 아니라 ORM이 관리하는 객체가 될 수 있다.

### DTO

DTO(Data Transfer Object)는 **데이터를 특정 경계 사이에서 전달하기 위한 객체**다. Entity와 마찬가지로 코드상 객체라는 점은 같지만 목적과 생명주기가 다르다.

예를 들어 Entity가 `id`, `title`, `internalStatus`, `createdAt`을 가지고 있지만 외부 응답에는 `id`, `title`만 필요하다면 필요한 값을 DTO에 복사해 반환할 수 있다.

`Entity → 필요한 값 선택/변환 → Response DTO → 외부 응답`

그러나 DTO가 항상 Entity의 일부 필드만 복사한 객체인 것은 아니다. 여러 Entity의 값을 합치거나 계산 결과를 넣거나, 반대로 외부 요청값을 받아 Service에 전달하는 Request DTO도 있다. 즉 DTO의 본질은 **Entity 축약본**이 아니라 **경계에 맞는 데이터 전달 모델**이다.

### Config

보안, 직렬화, 외부 연동, 객체 생성과 연결 등 애플리케이션의 동작 방식을 설정하는 코드가 위치할 수 있다.

## 전체 흐름

```text
사용자 요청
  ↓
Controller
  ↓
Service
  ↓
Repository
  ↓
DB
  ↓
Entity
  ↓
Service에서 필요한 데이터 구성
  ↓
DTO
  ↓
Controller의 HTTP 응답
```

Config는 이 흐름 옆에서 애플리케이션의 공통 동작과 구성 방식을 설정한다.

## 공격자 관점

- Controller의 입력이 어디까지 전달되는가
- Service의 권한 검사를 우회할 내부 경로가 있는가
- Repository 쿼리에 사용자 입력이 안전하게 전달되는가
- Entity의 내부 필드가 외부 응답으로 노출되는가

## 방어자 관점

- 인증·인가 책임 위치 명확화
- 입력 검증과 업무 규칙 검증 구분
- 외부 경계에 맞는 DTO 사용
- 안전한 데이터 접근 방식
- 계층 간 의존 방향 관리
