---
title: "DNS 이름과 소스 저장소 용어 구분"
date: 2026-08-24
draft: false
description: "DNS 계층의 이름과 개발 문서에서 사용하는 repository 용어가 서로 다른 개념임을 정리한 학습 로그"
categories: ["security", "development"]
tags: ["dns", "repository", "git"]
---

[전체 목차로 돌아가기](../overview-01/)

## 핵심 구분

DNS의 도메인 이름과 소스 코드 repository 이름은 서로 다른 계층의 개념이다.

일반적인 DNS 예시인 `api.example.test`에서 `api`는 하위 라벨이고, 개발 문서의 `repo`는 문맥에 따라 Git 등의 소스 코드 저장소(repository)를 뜻할 수 있다.

두 이름이 우연히 또는 네이밍 규칙에 따라 비슷할 수 있지만, 이름이 같다는 사실만으로 기술적인 연결 관계가 생기지는 않는다. 실제 연결은 배포 파이프라인, DNS, 인프라 설정 등 별도 구성으로 만들어진다.

## 보안 관점

서비스 이름, 저장소 이름, 환경 이름에 지나치게 예측 가능한 규칙을 공통 적용하면 외부에서 자산 구조를 추정하는 단서가 될 수 있다. DNS 관리 권한과 소스 저장소 권한도 별도 보안 경계로 관리한다.
