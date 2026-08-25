---
title: "Spring, MVC, 객체 연결과 DI"
date: 2026-08-25
draft: false
description: "Spring Framework와 Spring Boot의 관계, MVC, 인터페이스 구현과 DI를 일반적인 서버 구조로 정리한 학습 로그"
categories: ["security", "development"]
tags: ["spring", "spring-boot", "mvc", "dependency-injection", "backend"]
---

[전체 목차로 돌아가기](../overview-01/)

## Spring Framework와 Spring Boot

Spring Framework는 JVM 기반 애플리케이션에서 객체 생성과 연결, 웹 요청 처리, 트랜잭션, 데이터 접근 연동 등 여러 기반 기능을 제공한다.

Spring Boot는 Spring Framework를 기반으로 애플리케이션을 더 쉽게 구성하고 실행하도록 자동 설정, 의존성 구성, 실행 환경의 기본값 등을 제공하는 별도 프로젝트다. 단순히 `Spring 안에 Boot라는 기능 하나가 들어 있다`기보다 **Spring Framework를 활용하는 애플리케이션의 구성 비용을 줄이는 계층**으로 이해하는 편이 정확하다.

Python과 특정 패키지 배포판의 관계처럼 `언어 + 패키지 묶음`으로 완전히 대응시키기는 어렵다. Spring과 Spring Boot는 모두 애플리케이션 프레임워크 생태계 안에서 역할을 나누기 때문이다.

## MVC

MVC는 Model-View-Controller의 약자로 책임을 분리하는 설계 패턴이다.

- Controller: 외부 요청을 받아 적절한 처리로 연결한다.
- Model: 애플리케이션이 다루는 데이터와 상태를 표현한다.
- View: 사용자에게 보여 줄 표현 결과를 담당한다.

전통적인 서버 렌더링 웹에서는 View가 HTML일 수 있다. 모바일 앱이 REST API를 호출하는 구조에서는 서버가 JSON 같은 데이터를 반환하고 실제 화면은 모바일 앱이 그릴 수 있으므로, 실무 코드를 읽을 때는 `Controller → Service → Repository` 같은 계층 흐름을 함께 보는 것이 유용하다.

Spring은 DBMS 자체를 포함하지 않는다. 대신 트랜잭션과 데이터 접근 기술을 연계할 수 있는 추상화와 통합 기능을 제공하며, 실제 저장과 질의 실행은 외부 DBMS와 드라이버 등이 담당한다.

## 인터페이스, 구현과 Override

인터페이스는 구현체가 제공해야 할 동작의 계약을 정의할 수 있다. 구현 클래스는 그 계약에 맞는 메서드를 실제로 구현한다.

```text
KeyProvider (interface)
  └─ loadKey(id)
       ↑
DatabaseKeyProvider (implementation)
  └─ loadKey(id)의 실제 동작 구현
```

이 과정에서 구현체가 상위 타입에서 정의된 메서드의 실제 동작을 제공할 때 `override`라는 개념이 사용된다.

Overloading은 다른 개념이다. 같은 이름의 메서드를 매개변수의 개수나 타입 조합을 달리하여 여러 형태로 정의하는 것을 말한다.

## DI: Dependency Injection

DI의 핵심은 어떤 객체가 필요한 의존 객체를 내부에서 직접 생성하지 않고 **외부에서 제공받는 것**이다.

```text
Verifier
  └─ KeyProvider가 필요함
       ↑
외부 구성에서 실제 구현체를 연결
```

예를 들어 Verifier가 구체적인 DB 조회 클래스 자체에 묶이지 않고 `KeyProvider`라는 계약에 의존하면, 외부 구성에서 그 계약을 만족하는 구현체를 연결할 수 있다. Spring Container는 등록된 객체의 생성과 관계를 관리하면서 이런 연결을 수행할 수 있다.

이는 객체의 생명주기가 강하게 묶이는 Composition과 다른 축의 개념이다. Composition/Aggregation은 객체 사이의 전체-부분 관계를 설명하는 데 가깝고, DI는 **의존성을 누가 만들고 연결하는가**에 초점을 둔다.

## 보안 관점

### 공격자 관점

- 요청 검증 객체가 어떤 경로에 연결되어 있고 우회 가능한 진입점이 있는가
- 환경별 설정 차이로 보안 구현체가 빠지거나 다른 구현체가 연결될 수 있는가
- 데이터 접근 계층까지 전달되는 사용자 입력이 안전하게 처리되는가

### 방어자 관점

- 인증·인가·입력 검증 책임을 명확한 계층에 둔다.
- 보안 인터페이스의 구현체와 환경별 연결 상태를 검증한다.
- DB 접근 계정과 애플리케이션의 권한을 최소화한다.
- 자동 설정에 의존하더라도 실제 적용된 보안 설정을 확인한다.
