---
title: "OWASP Juice Shop"
description: "OWASP Top 10 취약점 실습 플랫폼"
date: 2024-01-21
categories: ["Lab", "Docker Labs"]
tags: ["OWASP", "Juice Shop", "CTF"]
---

{{< warning >}}
이 실습 환경은 **의도적으로 취약**하게 설계되었습니다.
반드시 로컬 Docker 환경에서만 실행하시기 바랍니다.
{{< /warning >}}

## 개요

OWASP Juice Shop은 현대적인 웹 애플리케이션의 보안 취약점을 실습할 수 있는 플랫폼입니다.
Node.js 기반으로 구축되어 있으며, CTF(Capture The Flag) 형식의 챌린지를 제공합니다.

## 특징

- OWASP Top 10 전체 취약점 포함
- 100개 이상의 해킹 챌린지
- 점수 및 진행률 추적
- 힌트 시스템

## 환경 정보

| 항목 | 내용 |
|------|------|
| Docker 이미지 | bkimminich/juice-shop |
| 기본 포트 | 3000 |
| 기술 스택 | Node.js, Angular |

## Docker 환경 구성

{{< docker-run image="bkimminich/juice-shop" port="3000" name="juice-shop" localport="3000" >}}

## 챌린지 카테고리

{{< mermaid >}}
mindmap
  root((Juice Shop))
    Injection
      SQL Injection
      NoSQL Injection
    Broken Auth
      Password Strength
      Forgotten Password
    XSS
      DOM XSS
      Reflected XSS
    Security Misconfig
      Error Handling
      Deprecated Interface
    Sensitive Data
      Confidential Document
      Exposed Metrics
{{< /mermaid >}}

## 시작하기

1. `http://localhost:3000` 접속
2. 우측 상단 `Account` → `Register` 로 계정 생성
3. 좌측 사이드바 `Score Board` 에서 챌린지 확인
4. 난이도별(⭐~⭐⭐⭐⭐⭐⭐) 챌린지 도전

## 초급 챌린지 예시

### Challenge: Score Board (⭐)

**목표**: 숨겨진 스코어보드 페이지 찾기

**힌트**: 개발자 도구에서 JavaScript 파일 분석

### Challenge: Admin Section (⭐⭐)

**목표**: 관리자 페이지 접근

**힌트**: 라우팅 정보 분석

## 실습 종료
```powershell
docker stop juice-shop && docker rm juice-shop
```

## 참고 자료

- [Juice Shop 공식 문서](https://pwning.owasp-juice.shop/)
- [Juice Shop GitHub](https://github.com/juice-shop/juice-shop)