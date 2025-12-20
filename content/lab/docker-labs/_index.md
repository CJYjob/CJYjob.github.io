---
title: "🐳 Docker Labs"
description: "Docker Hub 기반 취약점 실습 환경"
---

Docker Hub의 공식 취약점 실습 이미지를 활용한 실험 공간입니다.

## 사전 요구사항

- Docker Desktop 설치 및 실행
- 최소 4GB RAM 권장

## 사용 가능한 실습 환경

| 환경 | 설명 | 난이도 |
|------|------|--------|
| [DVWA](/lab/docker-labs/dvwa/) | 웹 취약점 종합 실습 | ⭐⭐☆☆☆ |
| [Juice Shop](/lab/docker-labs/juice-shop/) | OWASP Top 10 실습 | ⭐⭐⭐☆☆ |
| [WebGoat](/lab/docker-labs/webgoat/) | 웹 보안 학습 플랫폼 | ⭐⭐☆☆☆ |

## 공통 Docker 명령어
```powershell
# 실행 중인 컨테이너 확인
docker ps

# 모든 컨테이너 확인
docker ps -a

# 컨테이너 로그 확인
docker logs [container-name]

# 컨테이너 중지 및 삭제
docker stop [container-name]
docker rm [container-name]

# 사용하지 않는 이미지 정리
docker image prune
```