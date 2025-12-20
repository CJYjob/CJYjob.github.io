---
title: "OWASP WebGoat"
description: "웹 보안 학습 플랫폼"
date: 2024-01-22
categories: ["Lab", "Docker Labs"]
tags: ["WebGoat", "OWASP", "Learning"]
---

{{< warning >}}
이 실습 환경은 **의도적으로 취약**하게 설계되었습니다.
반드시 로컬 Docker 환경에서만 실행하시기 바랍니다.
{{< /warning >}}

## 개요

WebGoat는 OWASP에서 제공하는 웹 보안 학습 플랫폼으로, 각 취약점에 대한 상세한 설명과 실습을 제공합니다.

## 특징

- 단계별 학습 가이드
- 취약점별 상세 설명
- 자동 진행률 저장
- WebWolf 통합 (공격 시뮬레이션)

## 환경 정보

| 항목 | 내용 |
|------|------|
| Docker 이미지 | webgoat/webgoat |
| WebGoat 포트 | 8080 |
| WebWolf 포트 | 9090 |

## Docker 환경 구성
```powershell
# WebGoat + WebWolf 실행
docker run -d --name webgoat -p 8080:8080 -p 9090:9090 webgoat/webgoat

# 브라우저 접속
# WebGoat: http://localhost:8080/WebGoat
# WebWolf: http://localhost:9090/WebWolf
```

## 학습 경로

{{< mermaid >}}
graph LR
    A[Introduction] --> B[General]
    B --> C[Injection]
    C --> D[Broken Auth]
    D --> E[XSS]
    E --> F[Access Control]
    F --> G[Cryptography]
{{< /mermaid >}}

## 시작하기

1. `http://localhost:8080/WebGoat` 접속
2. `Register new user` 로 계정 생성
3. 좌측 메뉴에서 학습 주제 선택
4. 각 레슨의 설명을 읽고 실습 진행

## 실습 종료
```powershell
docker stop webgoat && docker rm webgoat
```

## 참고 자료

- [WebGoat 공식 GitHub](https://github.com/WebGoat/WebGoat)
- [OWASP WebGoat](https://owasp.org/www-project-webgoat/)