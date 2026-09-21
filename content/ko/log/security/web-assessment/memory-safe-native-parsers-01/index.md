---
title: "메모리 안전 언어와 네이티브 파서의 신뢰 경계"
date: 2026-09-21
draft: false
description: "파일 파서 관점에서 수동 메모리 관리, GC, Rust의 소유권 모델과 unsafe·FFI 경계를 구분해 메모리 안전성을 이해한 학습 기록"
categories: ["security"]
tags: ["memory-safety", "rust", "parser", "ffi", "secure-development"]
---

## 목차

1. 학습 목표
2. 메모리 관리 모델의 차이
3. Rust 소유권과 빌림
4. 메모리 안전과 성능을 혼동하지 않기
5. unsafe와 FFI가 만드는 새 경계
6. 파서 점검에 적용하기
7. 공격자·방어자 관점

## 1. 학습 목표

파일 parser의 구현 언어를 보고 "안전하다/위험하다"고 즉시 판정하지 않고, **언어가 제거하는 버그 종류와 여전히 남는 신뢰 경계**를 구분한다.

## 2. 메모리 관리 모델의 차이

C/C++처럼 수동 메모리 관리가 가능한 언어에서는 잘못된 lifetime 관리, 범위를 벗어난 접근, 해제 후 사용 같은 메모리 안전 문제가 발생할 수 있다.

GC(Garbage Collection)를 사용하는 언어는 객체 수명을 런타임이 관리하므로 수동 해제에서 생기는 일부 오류를 크게 줄인다. 하지만 "GC 언어이므로 모든 메모리 오류가 원천적으로 없다"고 일반화해서는 안 된다. 네이티브 확장, unsafe 기능, 런타임 자체의 결함, 논리적 자원 고갈 같은 문제는 별개다.

## 3. Rust 소유권과 빌림

Rust는 일반적인 safe code에서 ownership과 borrowing 규칙을 컴파일 시점에 검사한다.

핵심 모델은 다음과 같다.

- 값에는 소유권이 있다.
- 참조는 원본보다 오래 살아남을 수 없다.
- 같은 데이터에 대한 mutable aliasing을 제한한다.
- lifetime 규칙을 만족하지 못하면 컴파일이 거부된다.

이 규칙은 use-after-free나 data race 같은 중요한 버그 계열을 줄이는 데 강점이 있다.

다만 "Rust = buffer overflow가 어떤 경우에도 불가능"처럼 이해하면 안 된다. 안전한 Rust의 경계 밖으로 나가거나 외부 네이티브 코드와 연결되는 순간 별도의 검증이 필요하다.

## 4. 메모리 안전과 성능을 혼동하지 않기

GC가 존재한다고 해서 특정 언어가 항상 느린 것도 아니고, GC가 없다고 해서 parser에 항상 더 적합한 것도 아니다. 실제 성능은 구현, runtime, workload, allocation pattern, JIT/AOT 여부 등에 좌우된다.

따라서 보안 학습에서는 "빠르기 때문에 안전한 언어를 쓴다"보다 다음 질문이 더 중요하다.

> 이 parser의 신뢰할 수 없는 바이트가 어느 메모리 안전 경계까지 도달하는가?

## 5. unsafe와 FFI가 만드는 새 경계

Rust의 `unsafe`는 컴파일러가 보장할 수 없는 일부 조건을 개발자가 책임지는 영역이다. FFI(Foreign Function Interface)를 통해 C/C++ decoder나 OS API를 호출하는 경우에도 외부 코드의 메모리 안전성은 Rust 타입 시스템만으로 보장되지 않는다.

```text
untrusted file
  ↓
safe Rust parser
  ↓
unsafe wrapper / FFI
  ↓
native decoder
```

이 구조에서는 "코어가 Rust"라는 사실보다 **unsafe/FFI 경계가 어디에 있고, 외부 decoder가 어떤 입력을 받는가**를 확인한다.

## 6. 파서 점검에 적용하기

구현 언어를 확인했다면 다음 순서로 범위를 좁힌다.

1. 신뢰할 수 없는 입력을 직접 받는 모듈을 찾는다.
2. safe code와 unsafe/FFI 경계를 구분한다.
3. 외부 decoder·parser 의존성과 버전을 식별한다.
4. SBOM이나 의존성 고지로 알려진 취약점 매핑의 정확도를 높인다.
5. 수동 표본 테스트와 fuzzing의 보장 범위를 구분한다.

## 7. 공격자·방어자 관점

공격자는 언어 이름보다 **언어의 안전 보장이 끊기는 지점**을 찾는다. 방어자는 unsafe 범위를 최소화하고, wrapper에서 길이·lifetime·ownership 계약을 명확히 하며, 네이티브 의존성을 지속적으로 관리한다.

관련 학습: [로컬 파일 파싱·렌더링 보안 점검](../desktop-file-preview-security-01/)
