---
title: "DVWA (Damn Vulnerable Web Application)"
description: "웹 애플리케이션 취약점 종합 실습 환경"
date: 2024-01-20
categories: ["Lab", "Docker Labs"]
tags: ["DVWA", "XSS", "SQL Injection", "CSRF", "File Upload"]
---

{{< warning >}}
이 실습 환경은 **의도적으로 취약**하게 설계되었습니다.
반드시 로컬 Docker 환경에서만 실행하고, 외부 네트워크에 노출하지 마시기 바랍니다.
{{< /warning >}}

## 개요

DVWA는 PHP/MySQL 기반의 취약한 웹 애플리케이션으로, 다양한 웹 취약점을 실습할 수 있습니다.

## 실습 가능 취약점

{{< mermaid >}}
mindmap
  root((DVWA))
    Injection
      SQL Injection
      SQL Injection Blind
      Command Injection
    XSS
      Reflected XSS
      Stored XSS
      DOM XSS
    기타
      CSRF
      File Inclusion
      File Upload
      Brute Force
      Insecure CAPTCHA
{{< /mermaid >}}

## 환경 정보

| 항목 | 내용 |
|------|------|
| Docker 이미지 | vulnerables/web-dvwa |
| 기본 포트 | 80 |
| 기본 계정 | admin / password |
| 난이도 설정 | Low / Medium / High / Impossible |

## Docker 환경 구성

{{< docker-run image="vulnerables/web-dvwa" port="80" name="dvwa" localport="8080" >}}

## 초기 설정

1. 브라우저에서 `http://localhost:8080` 접속
2. `Create / Reset Database` 클릭
3. 로그인: `admin` / `password`
4. `DVWA Security` 메뉴에서 난이도 설정

## 실습 시나리오

### 1. SQL Injection (Low)

**목표**: 인증 우회 및 데이터 추출

**테스트 페이로드**:
```sql
' OR '1'='1
' UNION SELECT user, password FROM users--
```

**학습 포인트**:
- Prepared Statement의 중요성
- 입력값 검증의 필요성

### 2. Reflected XSS (Low)

**목표**: 악성 스크립트 실행

**테스트 페이로드**:
```html
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
```

**학습 포인트**:
- Output Encoding
- Content Security Policy

### 3. Command Injection (Low)

**목표**: OS 명령어 실행

**테스트 페이로드**:
```
; cat /etc/passwd
| whoami
```

## 난이도별 방어 기법 분석

| 난이도 | 방어 기법 |
|--------|-----------|
| Low | 방어 없음 |
| Medium | 기본적인 필터링 |
| High | 강화된 필터링 |
| Impossible | 완전한 방어 (참고용) |

## 영상 시연

{{< youtube id="YOUR-VIDEO-ID" title="DVWA SQL Injection 실습" >}}

## 실습 종료
```powershell
# 컨테이너 중지 및 삭제
docker stop dvwa && docker rm dvwa
```

## 참고 자료

- [DVWA 공식 GitHub](https://github.com/digininja/DVWA)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)