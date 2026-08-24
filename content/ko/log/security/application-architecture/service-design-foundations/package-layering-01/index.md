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

## 가상 리소스 조회 예시

사용자가 `GET /resources/123`처럼 특정 리소스를 조회한다고 가정한다.

### Controller

HTTP 요청을 받는 진입점이다. URL, HTTP method, 요청 데이터를 애플리케이션의 메서드와 연결하고 Service에 처리를 요청한다.

### Service

업무 규칙을 처리한다. 조회 가능 여부, 상태 확인, 여러 데이터 조합 같은 비즈니스 판단을 수행할 수 있다.

### Repository

DB 조회와 저장 같은 데이터 접근을 추상화한다. Service가 필요한 영속 데이터를 가져오도록 데이터 접근 계층과 연결된다.

### Entity

JPA의 Entity는 단순한 데이터 복사 객체가 아니라 **영속성 컨텍스트에서 식별성과 생명주기를 관리받는 영속 객체**다.

입문 단계에서는 `DB에 저장되는 데이터 구조를 애플리케이션 객체로 표현한다`고 이해할 수 있지만, 더 정확한 핵심은 JPA가 관리 상태의 Entity와 DB의 영속 상태를 연결한다는 데 있다.

예를 들어 JPA가 조회한 Entity의 특정 필드가 트랜잭션 안에서 변경되면, 관리 상태인 Entity의 변화를 추적해 적절한 시점에 UPDATE를 생성할 수 있다. 이를 변경 감지(dirty checking)라고 한다.

따라서 다음처럼 이해한다.

`DB의 영속 데이터 ↔ JPA 영속성 컨텍스트 ↔ 관리되는 Entity 객체`

Entity는 DB 자체의 기능이 아니라 애플리케이션/JPA 쪽 개념이다. 서비스가 객체 상태와 DB 상태의 연결을 직접 일일이 구현하는 대신 JPA가 이 관계와 생명주기를 관리하도록 할 수 있다.

실제 SQL이 DB에 전달되는 시점과 트랜잭션이 최종 확정되는 시점은 별개의 개념이며, 이후 `flush`와 `commit`을 학습할 때 연결한다.

### DTO

DTO(Data Transfer Object)는 **데이터를 특정 경계 사이에서 전달하기 위한 객체**다. Entity와 마찬가지로 코드상 객체라는 점은 같지만 목적과 생명주기가 다르다.

외부 응답에 필요한 값만 Entity에서 선택해 Response DTO를 만들 수 있다.

`Entity → 필요한 값 선택/변환 → Response DTO → 외부 응답`

하지만 DTO가 항상 Entity의 축약본인 것은 아니다. 여러 Entity의 값을 합치거나 계산 결과를 담을 수도 있고, 외부 요청값을 받아 Service로 전달하는 Request DTO도 있다.

DTO의 핵심은 `네트워크를 반드시 탄다`가 아니라 **어떤 경계 사이에서 필요한 데이터를 전달한다**는 것이다. 그 경계는 외부 클라이언트와 Controller 사이일 수도 있고, 애플리케이션 내부 계층 사이일 수도 있다.

따라서 다음처럼 구분한다.

- Entity: 영속성 세계와 연결되는 관리 대상 객체
- DTO: 경계 사이 데이터 전달을 위한 객체

### Config

보안, 직렬화, 외부 연동, 객체 생성과 연결 등 애플리케이션의 동작 방식을 설정하는 코드가 위치할 수 있다.

## 전체 흐름

```text
외부 요청
  ↓
Request DTO
  ↓
Controller
  ↓
Service
  ↓
Repository
  ↓
DB ↔ Entity
  ↓
Service에서 필요한 데이터 구성
  ↓
Response DTO
  ↓
외부 응답
```

Config는 이 흐름 옆에서 애플리케이션의 공통 동작과 구성 방식을 설정한다.

## 공격자 관점

- Controller의 입력이 어디까지 전달되는가
- Service의 권한 검사를 우회할 내부 경로가 있는가
- Repository 쿼리에 사용자 입력이 안전하게 전달되는가
- Entity의 내부 필드가 외부 응답으로 노출되는가
- 요청 DTO의 값이 검증 없이 Entity의 민감 필드에 반영되는가

## 방어자 관점

- 인증·인가 책임 위치 명확화
- 입력 검증과 업무 규칙 검증 구분
- 외부 경계에 맞는 DTO 사용
- Entity와 외부 입력 모델의 역할 분리
- 안전한 데이터 접근 방식
- 계층 간 의존 방향 관리
