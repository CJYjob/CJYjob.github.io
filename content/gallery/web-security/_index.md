---
title: "웹 보안 (Web Security)"
description: "웹 애플리케이션 보안의 핵심 개념"
date: 2024-01-15
categories: ["Gallery", "Web Security"]
tags: ["OWASP", "XSS", "SQL Injection"]
weight: 10
---

## 개요

웹 애플리케이션 보안은 정보보안의 핵심 영역입니다.

## 마인드맵

{{< mermaid >}}
mindmap
  root((Web Security))
    Injection
      SQL Injection
      Command Injection
      LDAP Injection
    XSS
      Stored XSS
      Reflected XSS
      DOM-based XSS
    Authentication
      Broken Auth
      Session Management
    Access Control
      IDOR
      Privilege Escalation
{{< /mermaid >}}

## OWASP Top 10

### 1. Injection

SQL, NoSQL, OS 명령어 등이 인터프리터에 신뢰할 수 없는 데이터로 전송될 때 발생합니다.

### 2. Cross-Site Scripting (XSS)

악성 스크립트가 웹 페이지에 삽입되어 사용자 브라우저에서 실행됩니다.

## 실습 링크

- [🧪 DVWA 실습](/lab/docker-labs/dvwa/)
- [🧪 OWASP Juice Shop 실습](/lab/docker-labs/juice-shop/)