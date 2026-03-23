---
title: "실무 수준의 보안 테스트베드 구축기 — 목표와 단계별 계획"
date: 2026-03-24
draft: false
description: "실무 수준의 하이브리드 업무환경 테스트베드를 단계적으로 구축하는 과정을 기록합니다. 온프레미스와 OCI 클라우드를 연결하는 풀스택 환경을 최소 구성부터 점진적으로 확장합니다."
categories: ["Lab"]
tags: ["테스트베드", "Docker", "pfSense", "보안환경구축", "모의해킹", "Hyper-V", "OCI"]
---

## 왜 이 글을 쓰는가

모의해킹 직무를 시작하면서 가장 필요하다고 느낀 것은 **실제 기업 환경과 유사한 실습 공간**이었다.

CTF 문제 하나, 튜토리얼 하나로 공부하는 것과, 실제로 방화벽·WAF·IDS·AD가 모두 돌아가는 환경을 직접 공격하고 방어해보는 것은 전혀 다른 경험이다. 이 글은 그 환경을 처음부터 만들어가는 과정을 기록한다.

---

## 최종 목표

**온프레미스와 클라우드를 연결한 하이브리드 네트워크 실습 환경**을 구축한다.

구체적으로는 실제 기업 네트워크 구조인 아래 흐름을 가상 환경으로 완전히 재현하는 것이 목표다.

```
인터넷(공격자) → 외부 방화벽 → IPS/IDS → WAF
                                        ↓
                               DMZ (웹서버·메일·VPN)
                                        ↓
                                   내부 방화벽
                                        ↓
                  내부망 (AD·WAS·직원PC) ↔ VPN ↔ OCI 클라우드
                                        ↓
                                 DB 격리 네트워크
```

이 환경에서 공격자(Kali)로 침투 시나리오를 수행하고, 동시에 SIEM(Splunk)에서 그 흔적이 어떻게 기록되는지 관찰할 수 있다.

---

## 구성 확정 사항

### 가상화 방식

| 구성요소 | 방식 | 이유 |
|---|---|---|
| pfSense (방화벽 × 2) | Hyper-V VM | FreeBSD 기반 → Docker 컨테이너 불가 |
| Windows Server 2022 (AD) | Hyper-V VM | Kerberos 등 Windows 커널 기능 필요 |
| 나머지 전체 | Docker 컨테이너 | 애플리케이션 격리로 충분 |

### 클라우드

OCI(Oracle Cloud Infrastructure) Always Free 티어를 사용한다.

- Ampere A1 ARM VM: 4 OCPU / 24GB RAM — **영구 무료**
- Site-to-Site IPSec VPN 50개 연결 — **영구 무료**
- 아웃바운드 데이터 10TB/월 — **영구 무료**

AWS·Azure·GCP의 무료 티어가 12개월 한정인 것과 달리, OCI는 기간 제한이 없다.

### 오픈소스 소프트웨어 목록

| 역할 | 소프트웨어 |
|---|---|
| 방화벽 | pfSense CE 2.7.2 |
| 공격자 PC | kali-rolling (Docker) |
| WAF | nginx 1.26 + ModSecurity 3 |
| IPS/IDS | Suricata 7.0 |
| SIEM | Splunk Free + Wazuh |
| 로드밸런서 | HAProxy 3.0 |
| 웹 서버 | nginx + DVWA + Juice Shop |
| 메일 서버 | Postfix + Dovecot |
| VPN | WireGuard |
| WAS | Apache Tomcat + WebGoat |
| AD | Windows Server 2022 Eval |
| DB | MySQL 8.0 + MSSQL 2022 Express |

---

## 단계별 구축 계획

**서비스 가용성을 유지하면서 구성요소를 하나씩 붙여나가는** 방식으로 접근한다.

### Step 1 — 최소 실습 환경

> 완료 기준: Kali에서 웹 서버 접속

Docker만으로 공격자와 취약한 웹 서버를 연결한다.

```
[Kali 컨테이너] → [nginx + DVWA + Juice Shop]
  net-external        net-dmz
```

### Step 2 — 방화벽 추가

> 완료 기준: pfSense 규칙으로 특정 포트 차단 확인

Hyper-V에 pfSense VM을 설치하고 Docker 네트워크와 연결한다.

```
[Kali] → [pfSense VM] → [웹 서버]
```

Docker 브릿지와 Hyper-V VM 간 연결은 `vEthernet`(Hyper-V 가상 스위치 호스트쪽 NIC)을 공유 지점으로 사용한다.

### Step 3 — 보안 모니터링 추가

> 완료 기준: Splunk에서 공격 로그 확인

```
[Kali] → [pfSense] → [웹 서버]
                          ↓ 로그 전송
                      [Splunk 컨테이너]
```

Splunk Free License는 일일 500MB 제한이 있지만 실습 환경에서는 충분하다.

### Step 4 — WAF + IDS 추가

> 완료 기준: WAF가 SQLi 페이로드 차단 확인

```
[Kali] → [pfSense] → [Suricata IPS] → [nginx+ModSec WAF] → [웹 서버]
```

IPS가 네트워크 레벨 공격을 먼저 걸러내고, WAF가 HTTP 내용 레벨 공격을 분석한다.

Suricata는 `network_mode: host`로 실행해 호스트의 모든 브릿지 트래픽을 캡처한다. `iptables NFQUEUE`를 통해 인라인 IPS로도 동작 가능하다.

### Step 5 — 내부망 확장

> 완료 기준: Kali에서 AD 침투 시나리오 완주

```
[Kali] → [pfSense 1] → [DMZ] → [pfSense 2] → [LAN: WAS + AD + 직원PC]
                                                         ↓
                                                   [DB 격리망]
```

Windows Server 2022 Evaluation을 Hyper-V VM으로 설치한다.

AD 서버는 만료 후 **Hyper-V 스냅샷 롤백**으로 무기한 운용한다. `slmgr -rearm` 명령으로 180일 추가 연장도 가능하다.

### Step 6 — 클라우드 연결

> 완료 기준: OCI VM과 내부망 간 ping 성공

```
[온프레미스 내부망] ←→ [WireGuard VPN] ←→ [OCI Always Free VM]
```

OCI VCN을 구성하고 WireGuard ↔ OCI IPSec Site-to-Site VPN으로 온프레미스와 연결한다. 연결 후 OCI의 WAS 인스턴스가 온프레미스 DB에 접근하는 이중화 구성이 완성된다.

---

## 전체 일정 요약

| Step | 내용 | 소요 시간 |
|---|---|---|
| Step 1 | Docker 최소 실습 환경 |
| Step 2 | pfSense 방화벽 VM 추가 |
| Step 3 | Splunk SIEM 추가 |
| Step 4 | WAF + Suricata IDS/IPS 추가 |
| Step 5 | 내부망 + AD 확장 |
| Step 6 | OCI 클라우드 VPN 연결 |

---

## 앞으로의 기록 방향

각 Step이 완료될 때마다 구성 파일, 발생한 문제와 해결 방법, 실습 시나리오를 이 블로그에 기록한다.

단순한 "설치 가이드"가 아니라, **왜 이 구조인지**, **어디서 막혔고 어떻게 해결했는지**를 중심으로 작성할 예정이다. 같은 목표를 가진 사람에게 실질적인 참고가 되길 바란다.

---

*다음 글: Step 1 — Docker로 최소 실습 환경 구성하기*
