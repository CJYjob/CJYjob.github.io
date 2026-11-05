---
title: "Hugo 블로그 운영 구조와 AI Agent·Harness 기술 기초"
date: 2026-11-05
draft: true
description: "Hugo·GitHub Actions의 정적 사이트 생성 및 배포 구조와 LLM, Agent, Harness, Workflow, SDK, MCP의 개념 및 실제 AI 서비스 설계 원리를 정리한 학습 기록"
categories:
  - development
  - automation
  - ai
series:
  - ai-blog-operations
tags:
  - hugo
  - github-actions
  - github-pages
  - static-site-generation
  - llm
  - ai-agent
  - harness
  - workflow
  - sdk
  - mcp
activities:
  - learning
---

# Hugo 블로그 운영 구조와 AI Agent·Harness 기술 기초

## 1. 학습 개요

### 1.1 학습 목적

기존에 AI의 도움으로 구축한 GitHub Pages 블로그를 직접 이해하고 유지보수할 수 있는 기술 역량을 확보하는 것이 목적입니다.

추가로 AI 모델·Agent·Harness·MCP 등 AI 서비스의 구성요소를 학습하고, 이를 활용하여 블로그 운영 자동화 및 소프트웨어 개발 시스템을 설계할 수 있는 기반을 마련합니다.

이번 기록은 **개념 학습과 기존 시스템 구조 분석**에 해당합니다. AI 운영 서비스의 구현 완료나 성능 검증 결과를 의미하지 않습니다.

### 1.2 학습 범위

1. Hugo와 정적 사이트 생성기의 원리
2. 콘텐츠 저장 구조와 Taxonomy
3. HTML 템플릿과 URL 생성
4. GitHub Actions의 CI/CD 구조 및 한계
5. LLM·Agent·Harness·Workflow·SDK의 관계
6. MCP와 외부 도구 호출 원리
7. ARTEX 및 Norma SDK의 공개 구현
8. Custom GPT에서 Plugin으로의 전환
9. AI 기반 블로그 운영 자동화의 향후 설계 방향

---

## 2. Hugo와 정적 사이트 생성기

### 2.1 Hugo란?

Hugo는 Go 언어로 개발된 정적 사이트 생성기(Static Site Generator, SSG)입니다.

Markdown으로 작성한 콘텐츠와 HTML 템플릿, 설정 파일을 조합하여 실제 웹사이트에 필요한 HTML, CSS, JavaScript 등의 파일을 생성합니다.

정적 사이트 생성기는 방문자 요청이 발생할 때마다 서버에서 페이지를 생성하는 대신, **사이트 빌드 시점에 필요한 페이지를 미리 생성**합니다.

따라서 GitHub Pages처럼 정적 파일을 제공하는 호스팅 서비스와 함께 사용할 수 있습니다.

### 2.2 Hugo를 사용한 이유

현재 블로그는 다음 요구사항을 갖고 있습니다.

- Markdown 기반 콘텐츠 저장
- Git을 통한 변경 이력 관리
- 학습 기록과 완결 산출물의 분리
- Category·Tag·Series를 이용한 분류
- 다국어 확장 가능성
- GitHub Actions 기반 자동 배포

이러한 조건에서 Hugo는 적합한 선택입니다.

다만 최초 구축 당시 Hugo, Jekyll, Astro 등 후보를 비교하고 최종 선정한 의사결정 기록은 확인하지 못했습니다. 따라서 위 내용은 **현재 요구사항을 기준으로 재평가한 판단**입니다.

대표적인 대안으로 Jekyll, Astro, Eleventy, Docusaurus, WordPress 등이 있습니다.

Hugo·Jekyll·Eleventy는 정적 사이트 생성에 초점을 맞추며, Astro는 컴포넌트 기반 웹 개발에 유리합니다. WordPress는 콘텐츠 편집과 관리 기능을 제공하는 CMS에 해당합니다.

현재 블로그를 리팩터링하기 위해 Hugo 자체를 교체할 기술적 필요성은 확인되지 않았습니다.

---

## 3. 현재 블로그 기술 스택

확인한 주요 기술 구성은 다음과 같습니다.

| 기술 | 역할 |
|---|---|
| GitHub Repository | 원본 콘텐츠·설정·코드 저장 |
| Hugo Extended | 정적 사이트 생성 |
| PaperMod | Hugo 테마 |
| GitHub Actions | 빌드·테스트·배포 자동화 |
| GitHub Pages | 정적 웹사이트 호스팅 |
| Markdown | 본문 콘텐츠 형식 |
| YAML | 사이트·Workflow·게시글 메타데이터 설정 |
| Python | 데이터 처리 및 자동화 |
| Mermaid.js | 다이어그램 렌더링 |

### 3.1 저장소 구조

```text
repository/
├── .github/
│   └── workflows/
├── archetypes/
├── config/
├── content/
│   └── ko/
│       ├── log/
│       ├── portfolio/
│       ├── categories/
│       └── series/
├── data/
├── docs/
├── layouts/
│   ├── partials/
│   └── shortcodes/
├── scripts/
├── static/
├── themes/
│   └── PaperMod/
└── hugo.yaml
```

각 디렉터리는 다음과 같은 책임을 가집니다.

- `content`: 웹사이트에 게시할 콘텐츠 원본을 보관합니다.
- `layouts`: 화면 렌더링에 사용하는 사용자 정의 템플릿을 보관합니다.
- `themes`: 기본 테마를 보관합니다.
- `data`: 구조화된 데이터를 저장합니다.
- `static`: 이미지·아이콘 등 정적 리소스를 보관합니다.
- `scripts`: 자동화 프로그램을 보관합니다.
- `docs`: 운영·설계 관련 문서를 보관합니다.
- `.github/workflows`: GitHub Actions 자동화 설정을 보관합니다.

### 3.2 콘텐츠와 산출물의 구분

현재 블로그는 크게 Log와 Portfolio로 구분합니다.

**Log**는 학습·연구·개발 등 진행 과정의 이력을 누적하는 공간입니다.

**Portfolio**는 일정한 활동이 완료되어 외부에 설명할 수 있는 산출물로 정리한 결과를 게시하는 공간입니다.

Log의 내용이 완성되면 원본을 삭제하거나 이동하기보다는 별도의 Portfolio 페이지로 정리하고, 필요하면 원래 Log를 참조하도록 연결합니다.

이를 통해 활동의 진행 과정과 최종 결과를 모두 보존할 수 있습니다.

---

## 4. Markdown과 Front matter

### 4.1 Markdown

Markdown은 간단한 문법으로 제목, 본문, 표, 코드 등을 작성할 수 있는 문서 형식입니다.

Hugo는 Markdown을 해석하여 HTML 콘텐츠로 렌더링합니다.

### 4.2 Front matter

Front matter는 게시글 앞부분에서 메타데이터를 정의하는 영역입니다.

```yaml
---
title: "게시글 제목"
date: 2026-11-05
draft: false

categories:
  - security
  - automation

series:
  - security-automation

tags:
  - python
  - linux

activities:
  - learning
---
```

주요 필드는 다음과 같습니다.

| 필드 | 의미 |
|---|---|
| `title` | 게시글 제목 |
| `date` | 작성일 |
| `description` | 게시글 요약 |
| `draft` | 초안 여부 |
| `categories` | 콘텐츠 분야 |
| `series` | 연속된 주제·프로젝트 |
| `tags` | 세부 기술·키워드 |
| `activities` | 활동 유형 |
| `aliases` | 이전 URL을 위한 별칭 |
| `weight` | 페이지 정렬 가중치 |

`draft: true`인 글은 일반적인 Hugo 프로덕션 빌드에서 제외됩니다. 다만 공개 GitHub 저장소에 저장된 원본 파일까지 비공개가 되는 것은 아닙니다.

---

## 5. Taxonomy와 콘텐츠 분류체계

### 5.1 Taxonomy의 의미

Taxonomy는 콘텐츠의 논리적인 분류체계를 의미합니다.

Hugo는 사용자 정의 Taxonomy를 지원하며, 동일한 분류 값을 갖는 게시글을 연결하여 목록 페이지를 생성합니다.

현재 블로그에는 다음과 같이 설정되어 있습니다.

```yaml
taxonomies:
  category: categories
  tag: tags
  series: series
  activity: activities
```

### 5.2 네 가지 분류축

| Taxonomy | 목적 |
|---|---|
| Categories | 콘텐츠가 속하는 분야 |
| Tags | 콘텐츠가 다루는 세부 기술·개념 |
| Series | 하나의 이어지는 학습·연구·프로젝트 |
| Activities | 해당 글에서 수행한 활동의 종류 |

Category와 Tag는 하나의 게시물에 복수로 지정할 수 있습니다.

Series는 같은 기술을 사용하더라도 프로젝트가 다르다면 구분할 수 있습니다. 단, 분류체계를 과도하게 세분화하기보다 실제로 필요한 경우에만 Series를 추가합니다.

### 5.3 Taxonomy와 Term

Taxonomy는 분류 방식이며, Term은 그 분류에 속한 실제 값입니다.

예를 들어 `categories`라는 Taxonomy에 `security`, `development`라는 Term을 지정할 수 있습니다.

Hugo는 기본적으로 다음과 같은 목록을 생성할 수 있습니다.

```text
/categories/
/categories/security/
/categories/development/
```

Hugo의 기본 Taxonomy는 중첩 구조가 아니라 평면적인 분류입니다.

따라서 프로젝트의 상하관계가 필요한 경우에는 콘텐츠 디렉터리 구조나 별도 인덱스 페이지를 이용할 수 있습니다.

### 5.4 분류 값의 표기 규칙

분류 식별자는 영문 소문자와 하이픈을 조합한 `kebab-case`를 사용하기로 했습니다.

예시:

```text
security-automation
ai-agent
infrastructure-assessment
```

이는 Hugo의 필수 조건이 아니라 일관된 명명 규칙을 위한 운영 기준입니다.

현재 단계에서는 별도 정규화 프로그램을 개발하지 않고, 콘텐츠를 작성할 때 규칙을 적용합니다.

### 5.5 Weight를 이용한 순서 관리

Hugo의 Weight는 정수 기반 정렬 값입니다.

값이 작은 항목이 먼저 표시되며, 일반적으로 10·20·30처럼 간격을 두고 설정하면 중간 항목을 추가하기 편리합니다.

```yaml
weight: 10
```

Taxonomy별로 별도의 정렬 기준도 사용할 수 있습니다.

```yaml
series_weight: 20
```

`weight`는 일반적인 페이지 목록에서, `series_weight`는 해당 Series의 게시글 정렬에서 사용합니다.

Weight는 목록의 순서를 조절하는 기능이지 콘텐츠의 상하계층 자체를 만드는 기능은 아닙니다.

---

## 6. Hugo 템플릿과 URL 생성 원리

### 6.1 템플릿이란?

Hugo 템플릿은 Markdown 콘텐츠를 어떤 HTML 구조에 배치할지 정의하는 파일입니다.

예를 들어 다음 템플릿을 사용하면 제목과 본문을 출력할 수 있습니다.

```go-html-template
<article>
  <h1>{{ .Title }}</h1>
  {{ .Content }}
</article>
```

`.Title`은 게시글 제목을, `.Content`는 Markdown을 렌더링한 본문을 의미합니다.

### 6.2 템플릿과 필터링

템플릿은 화면의 구조를 정의합니다.

필터링은 여러 콘텐츠 중에서 특정 조건에 맞는 게시글을 선택하는 작업입니다.

단일 게시글 템플릿은 Hugo가 전달한 현재 게시글을 렌더링하므로 별도의 글 선택 과정이 필요하지 않을 수 있습니다.

반면 목록 페이지에서는 여러 글을 순회하거나 조건에 따라 선택할 수 있습니다.

```go-html-template
{{ range .Pages }}
  <a href="{{ .RelPermalink }}">
    {{ .Title }}
  </a>
{{ end }}
```

특정 분류에 속한 게시글 목록은 Hugo의 Taxonomy 기능과 템플릿을 조합하여 표시합니다.

### 6.3 Partial과 Shortcode

Partial은 템플릿 안에서 재사용하는 HTML 구성요소입니다.

예를 들어 모든 페이지에 공통으로 삽입하는 스크립트나 푸터를 별도 파일로 작성할 수 있습니다.

Shortcode는 Markdown 본문에서 직접 호출하는 재사용 기능입니다.

현재 블로그에는 Mermaid 다이어그램, 경고 상자, Docker 실행 예시 등의 Shortcode가 존재합니다.

**Partial은 주로 템플릿에서 호출하고, Shortcode는 주로 게시글에서 호출한다는 차이**가 있습니다.

### 6.4 `index.md`와 `_index.md`

Hugo는 두 파일명을 구분합니다.

- `index.md`: 일반적으로 독립적인 게시글을 구성하는 Leaf Bundle의 대표 파일입니다.
- `_index.md`: 섹션·Taxonomy·Term 등의 Branch Bundle을 정의하는 대표 파일입니다.

예시:

```text
content/ko/portfolio/security/
├── _index.md
├── project-a/
│   └── index.md
└── project-b/
    └── index.md
```

상위 `_index.md`는 보안 포트폴리오 섹션을 정의하고, 각 프로젝트의 `index.md`는 개별 게시글을 정의합니다.

### 6.5 원본 파일 경로에서 공개 URL까지

```text
Markdown 원본
content/ko/log/example/index.md
          ↓
Hugo의 페이지 경로 해석
/log/example/
          ↓
HTML 생성
public/log/example/index.html
          ↓
GitHub Pages 배포
https://cjyjob.github.io/log/example/
```

`content/ko/`는 한국어 콘텐츠를 저장하는 원본 경로입니다.

현재 한국어가 기본 언어이고 `defaultContentLanguageInSubdir: false`이므로 공개 URL에 `/ko/`가 추가되지 않습니다.

Hugo는 콘텐츠 경로와 URL 설정 등을 이용해 출력 경로를 결정하고, 그 위치에 HTML 파일을 생성합니다.

---

## 7. GitHub Actions와 CI/CD

### 7.1 GitHub Actions란?

GitHub Actions는 GitHub에서 발생하는 이벤트를 기반으로 개발·테스트·빌드·배포 등을 자동화하는 서비스입니다.

CI/CD는 지속적 통합과 지속적 제공·배포를 의미합니다.

GitHub Actions는 소스코드의 변경을 감지하고 미리 정의된 Workflow에 따라 명령어를 실행할 수 있습니다.

### 7.2 구성요소

| 구성요소 | 의미 |
|---|---|
| Workflow | 전체 자동화 절차 |
| Job | 독립적인 실행 작업 단위 |
| Step | Job을 구성하는 개별 실행 단계 |
| Runner | Job을 실행하는 컴퓨터 환경 |
| Action | Workflow에서 재사용 가능한 실행 기능 |
| Artifact | 작업을 통해 만들어진 결과물 |

Job마다 독립된 Runner가 할당될 수 있으며, 같은 Workflow에 속한다고 해서 모든 Job이 하나의 실행환경을 공유하는 것은 아닙니다.

### 7.3 두 YAML 파일의 차이

현재 저장소에는 두 종류의 핵심 설정 파일이 있습니다.

```text
hugo.yaml
.github/workflows/hugo.yaml
```

두 파일은 이름이 같지만 읽는 프로그램과 목적이 다릅니다.

| 파일 | 해석하는 프로그램 | 역할 |
|---|---|---|
| `hugo.yaml` | Hugo | 사이트 생성 규칙 |
| `.github/workflows/hugo.yaml` | GitHub Actions | 자동화 실행 절차 |

GitHub Actions가 Workflow를 해석한 뒤 Hugo 실행 명령을 호출합니다.

그다음 Hugo가 프로젝트 루트의 `hugo.yaml`을 읽어서 콘텐츠를 빌드합니다.

### 7.4 현재 블로그의 빌드·배포 과정

```text
1. Markdown 및 코드 변경
             ↓
2. GitHub main 브랜치 Push
             ↓
3. GitHub Actions Workflow 시작
             ↓
4. Ubuntu Runner 준비
             ↓
5. Hugo 설치 및 저장소 Checkout
             ↓
6. Hugo가 설정과 콘텐츠 해석
             ↓
7. Markdown + Template → HTML 생성
             ↓
8. public/ 디렉터리에 결과 저장
             ↓
9. Pages Artifact 업로드
             ↓
10. GitHub Pages에 배포
             ↓
11. 방문자의 HTTP 요청에 정적 파일 응답
```

현재 Workflow에는 운동 데이터 병합을 수행하는 Job과 Hugo 사이트를 빌드하는 Job, 배포하는 Job이 별도로 있습니다.

이 중 `build`와 운동 데이터 병합 Job 사이에 명시적인 선행 의존관계가 없어, 병합 결과가 해당 빌드에 포함되지 않을 가능성이 있습니다. 이는 설정 분석을 통해 발견한 잠재적 문제이며 실제 장애 여부는 실행 로그 검증이 필요합니다.

### 7.5 GitHub Actions의 실행 한계

GitHub Actions는 범용 클라우드 컴퓨터가 아니라 자동화 실행 서비스입니다.

2026년 11월 기준 주요 제한은 다음과 같습니다.

| 항목 | 제한 |
|---|---|
| 일반 GitHub-hosted Runner Job | 최대 6시간 |
| Workflow Run 전체 경과기간 | 최대 35일 |
| Self-hosted Runner Job | 최대 5일 |
| 공개 저장소 표준 `ubuntu-latest` | 4 vCPU, RAM 16GB, SSD 14GB |
| Public 저장소 표준 Runner | 사용량 무료, 별도 시스템 제한 적용 |

Job의 6시간 제한과 Workflow의 35일 제한은 서로 다른 기준입니다.

35일은 월간 사용 가능시간이 아니라 하나의 Workflow Run이 지속될 수 있는 최대 경과기간입니다.

GitHub-hosted Runner는 Job 종료 후 실행환경이 폐기되므로, 장기간 상태를 유지하는 AI 서버나 게임 서버 등의 상시 서비스 운영에는 적합하지 않습니다.

GitHub의 공식 약관은 프로젝트의 소프트웨어 개발·테스트·배포·게시와 무관한 GitHub-hosted Runner 사용을 제한합니다. 위반 탐지의 구체적인 내부 알고리즘은 공개되어 있지 않습니다.

따라서 Hugo 빌드, 코드 검증, 테스트, 정적 분석 등은 GitHub Actions에 맡기고, 지속적으로 실행해야 하는 AI 서비스는 별도의 실행환경에 배치하는 것이 적절합니다.

---

## 8. AI 서비스의 주요 구성요소

### 8.1 LLM

Large Language Model의 약어입니다.

입력된 정보를 바탕으로 텍스트나 구조화된 데이터를 생성하는 모델입니다.

LLM 자체는 GitHub API를 실행하거나 운영체제 명령어를 수행하는 주체가 아닙니다.

외부 작업은 모델이 요청한 도구 호출을 AI 애플리케이션이 처리하는 방식으로 수행됩니다.

### 8.2 Agent

Agent는 목표를 달성하기 위해 모델과 도구를 조합하여 작업을 수행하는 실행 주체입니다.

예를 들어 게시글 개선 Agent는 파일을 읽고, 수정할 부분을 판단하고, 도구를 호출해 수정안을 생성할 수 있습니다.

### 8.3 Harness

Harness는 Agent를 실행하고 통제하는 시스템입니다.

Harness에는 다음과 같은 요소가 포함될 수 있습니다.

- 모델 및 Agent 실행 관리
- 도구 등록·호출
- 컨텍스트 및 세션 상태 관리
- 실행 권한과 승인 절차
- 오류 처리 및 복구
- 실행 로그와 평가

Harness의 범위는 제품마다 다르며, 모든 개발 프레임워크가 동일한 구조를 채택하는 것은 아닙니다.

### 8.4 Workflow

Workflow는 목표를 수행하기 위한 작업 순서, 분기, 의존관계 등을 정의한 절차입니다.

예시:

```text
게시글 수집
    ↓
내용 분석
    ↓
수정안 작성
    ↓
형식·링크·빌드 검사
    ↓
변경사항 검토
    ↓
사용자 승인
    ↓
게시
```

Workflow는 LLM 없이도 실행할 수 있습니다. 정형적인 작업은 일반 코드로 처리하고, 판단이 필요한 부분에 AI를 활용할 수 있습니다.

### 8.5 SDK

SDK는 Software Development Kit의 약어입니다.

특정 시스템을 개발하기 위해 제공되는 라이브러리, 예제, 개발 도구, 문서 등의 묶음입니다.

예를 들어 Agent SDK를 사용하면 모델 호출, 도구 연동, 실행 루프 등의 기능을 모두 직접 개발하지 않고 재사용할 수 있습니다.

---

## 9. MCP와 AI의 도구 호출

### 9.1 MCP의 정의

MCP(Model Context Protocol)는 AI 애플리케이션이 외부 시스템의 도구와 데이터를 활용할 수 있도록 정의된 표준 통신 규약입니다.

MCP는 AI 모델도 아니고 Agent도 아닙니다.

### 9.2 주요 구성요소

| 구성요소 | 역할 |
|---|---|
| MCP Host | AI 애플리케이션 |
| MCP Client | MCP Server와 연결하는 구성요소 |
| MCP Server | 도구와 리소스를 제공하는 프로그램 |

MCP Server는 원격 서버일 수도 있고 로컬 프로세스일 수도 있습니다.

### 9.3 제공 기능

MCP는 다음과 같은 주요 기능을 제공합니다.

- **Tools:** 외부 API 호출, 데이터 조회, 프로그램 실행 등
- **Resources:** 파일, 문서, 데이터 등의 정보 제공
- **Prompts:** 재사용 가능한 지시 템플릿 제공

### 9.4 실제 도구 호출 원리

```text
사용자 요청
    ↓
AI 애플리케이션
    ↓
LLM이 도구 호출 필요성 판단
    ↓
도구 이름 및 입력 인자 생성
    ↓
실행 환경에서 권한·입력 검증
    ↓
MCP Client → MCP Server
    ↓
외부 API 또는 프로그램 실행
    ↓
실행 결과 반환
    ↓
LLM이 결과 해석
    ↓
최종 응답 또는 후속 작업
```

여기서 중요한 것은 **LLM이 외부 시스템을 직접 실행하는 것이 아니라, 애플리케이션이 모델의 도구 호출 요청을 처리한다는 점**입니다.

MCP는 필수 구성요소가 아닙니다. 자체 코드에서 GitHub API를 직접 호출하도록 구현하는 것도 가능합니다.

MCP의 장점은 서로 다른 도구를 표준화된 인터페이스로 연결하고 여러 AI 애플리케이션에서 재사용할 수 있다는 것입니다.

### 9.5 Custom Actions와 MCP

기존 GPT Custom Actions는 OpenAPI 스키마 등을 통해 외부 API 호출 방법을 정의하는 방식입니다.

MCP는 별도의 Client·Server 규약을 통해 도구를 검색하고 호출합니다.

두 방식은 외부 API를 호출한다는 목적은 유사하지만, 도구 제공과 통신의 구조가 다릅니다.

기존 Custom Actions의 API 명세는 향후 MCP 연동을 설계하는 참고자료가 될 수 있습니다.

---

## 10. Multi-Agent와 역할 분리

### 10.1 여러 Agent가 항상 유리한가?

Multi-Agent는 여러 Agent가 서로 다른 역할을 수행하거나 작업을 병렬로 처리하는 구조입니다.

그러나 Agent 수가 많아질수록 항상 성능이 향상되는 것은 아닙니다.

작업 간 의존관계, 입력 정보의 중복, 토큰 사용량, 실행 비용, 오류 전달 등을 고려해야 합니다.

### 10.2 역할 기반 설계

사람이 일하는 조직의 직책을 그대로 Agent에 대응시키기보다, AI의 실행 특성에 따라 역할을 분리하는 것이 합리적인 설계 가설입니다.

예를 들어 다음 책임을 구분할 수 있습니다.

| 역할 | 주요 책임 |
|---|---|
| 분석 | 원본 정보와 요구사항 분석 |
| 작성 | 코드·문서 변경안 생성 |
| 검증 | 실행·형식·테스트 결과 검증 |
| 검토 | 변경사항의 품질과 누락 확인 |
| 승인 | 실제 반영 여부 결정 |

이 역할들이 반드시 서로 다른 Agent여야 하는 것은 아닙니다.

초기에는 단일 Agent와 일반 검증 프로그램을 조합한 뒤, 필요성이 확인되는 역할부터 분리하는 접근을 검토합니다.

### 10.3 Hook과 권한 제어

Hook은 특정 이벤트 또는 실행 단계에서 호출하는 제어 로직입니다.

예를 들어 파일 수정 전에 허용 경로를 검사하거나, 도구 호출 전에 필요한 자료가 준비되었는지 확인할 수 있습니다.

그러나 필수 문서를 읽도록 프롬프트에 지시하는 것만으로는 실제 읽기 수행을 보장하지 않습니다.

필요한 자료는 실행 전에 프로그램이 직접 로드하고, 읽기 성공 여부를 검증하도록 설계할 수 있습니다.

또한 읽기 전용 Agent에는 파일 수정 도구를 제공하지 않는 것처럼 실제 실행 권한을 제한하는 것이 중요합니다.

---

## 11. ARTEX와 Norma SDK

ARTEX는 LLM 기반 다중 Agent를 활용한 보안 자동화 프레임워크입니다.

공개된 ARTEX 파생 구현에서는 Go 기반 백엔드, Next.js 프런트엔드, 여러 Agent의 계획·실행 구조를 확인할 수 있습니다.

해당 파생 저장소의 `go.mod`에는 다음 의존성이 선언되어 있습니다.

```go
github.com/Autumn-27/norma v0.4.3
```

따라서 **확인한 공개 ARTEX 파생 구현은 Norma SDK v0.4.3을 사용합니다.**

Norma는 Go 기반 Agent SDK로 다음과 같은 기능을 제공합니다.

| 구성요소 | 역할 |
|---|---|
| Agent Core | Agent 실행 및 세션 |
| Harness | 실행 루프·스케줄링 |
| Tool | 도구 관리 |
| Permission | 도구 사용 권한 |
| Hook | 실행 시점별 제어 |
| MCP | 외부 도구 통신 |
| Memory | 장기 데이터 관리 |
| Subagent | 하위 Agent 실행 |
| Coordinator | 다중 Agent 조정 |

다만 파생 구현에서 확인된 의존성을 원본 ARTEX의 모든 버전에 일반화할 수는 없습니다.

Norma를 분석할 때도 실제 사용한 `v0.4.3`과 최신 브랜치를 구분해야 합니다.

ARTEX의 실행 제어 구조와 Agent 오케스트레이션은 학습 대상이 될 수 있지만, 보안 연구 자동화를 구현할 때는 허가된 범위와 격리된 환경을 전제로 해야 합니다.

---

## 12. Custom GPTs와 Plugin 전환

OpenAI는 기존 Custom GPT를 Plugin으로 이전하는 전환 절차를 안내했습니다.

2026년 11월 기준 공식 예정 종료일은 **2026년 12월 11일**입니다. 일부 승인된 워크스페이스에는 예외 일정이 적용될 수 있습니다.

### 12.1 이전되는 구성요소

| 기존 GPT 구성 | Plugin 전환 |
|---|---|
| Instructions | Skill 지침으로 이전 |
| Knowledge 파일 | Reference 파일로 이전 |
| 연결된 Apps | Plugin 앱 구성으로 이전 |
| Custom Actions | 자동 이전되지 않음 |
| 모델 선택 | 그대로 이전되지 않음 |

이전 후 원본 GPT는 종료 예정일까지 사용할 수 있지만 읽기 전용으로 전환됩니다.

따라서 기존 Custom Actions에 의존하는 기능은 별도 App 또는 MCP 연동으로 재구성해야 할 수 있습니다.

### 12.2 향후 재사용을 위한 보존 자료

AI 서비스를 새로 개발하기 전에 다음 자료를 보존할 필요가 있습니다.

- 기존 Instructions 원본
- Custom Actions의 OpenAPI 스키마
- 참고자료 및 Knowledge 파일
- 외부 API와 인증 방식의 명세
- 실제 작업 시나리오 및 기대 결과

API Key 등 실제 인증 비밀값은 일반 문서에 저장하지 않아야 합니다.

기존 GPTs의 설계를 그대로 새 시스템에 적용하기보다는 역할, 지식, 도구, Workflow를 분리하고 중복되거나 불필요한 요소를 검토할 필요가 있습니다.

---

## 13. AI 기반 블로그 운영체계의 향후 설계 방향

기존 블로그는 정적 사이트 생성기와 GitHub Actions를 이용한 배포 시스템을 유지합니다.

AI는 콘텐츠의 이해·개선·관리 과정을 보조하는 별도 서비스로 구성하는 방향을 검토합니다.

### 13.1 후보 아키텍처

```text
사용자 요청
    ↓
AI 작업 실행기
    ↓
원본 저장소 및 기준 문서 조회
    ↓
변경 대상 식별
    ↓
AI 수정안 생성
    ↓
Diff 생성
    ↓
정적 검사 및 Hugo 빌드
    ↓
사용자 검토·승인
    ↓
GitHub Pull Request 병합
    ↓
GitHub Actions 배포
    ↓
배포 결과 확인
```

이 구성은 학습 과정에서 도출한 **설계 후보**입니다. 구현 완료된 시스템은 아닙니다.

### 13.2 검증 항목

AI 도입의 효과는 다음 기준으로 평가할 수 있습니다.

| 평가 지표 | 측정 방법 |
|---|---|
| 정확성 | 사실 오류 및 누락 수 |
| 작업 효율 | 동일 작업의 소요시간 |
| 비용 | 모델 호출·토큰 사용량 |
| 안정성 | 빌드 실패·도구 호출 오류 |
| 통제 가능성 | 허용되지 않은 작업 시도·차단 |
| 유지관리성 | 변경과 복구의 난이도 |

단일 Agent와 Multi-Agent 구조를 비교할 때는 동일한 작업과 평가 기준을 사용해야 합니다.

### 13.3 앞으로 수행할 학습과 실험

- Hugo 콘텐츠·템플릿·배포 구조의 직접 수정 및 검증
- GitHub Actions 실행 로그와 Artifact 확인
- 기존 자동화 Workflow의 의존관계 점검
- Agent SDK의 실제 코드 구조 분석
- MCP Client·Server의 간단한 연동 실험
- Agent의 도구 호출·권한·승인 동작 검증
- AI 작성 결과의 정확성과 비용 평가
- 기존 콘텐츠 검토 및 정비 자동화

---

## 14. 학습 결론

이번 학습에서 도출한 핵심 내용은 다음과 같습니다.

**첫째**, Hugo는 Markdown 콘텐츠와 템플릿을 이용하여 웹페이지를 생성하고, GitHub Actions는 그 빌드·배포 절차를 실행하며, GitHub Pages는 결과물을 호스팅합니다.

**둘째**, Category·Tag·Series·Activity는 콘텐츠의 의미적 관계를 정의하며, 디렉터리 구조와 템플릿은 콘텐츠의 물리적 배치 및 화면 구성과 관련됩니다.

**셋째**, GitHub Actions의 Runner는 소프트웨어 자동화 실행환경이지 장기적으로 유지되는 범용 서버가 아닙니다.

**넷째**, LLM은 도구 호출을 요청할 수 있지만, 실제 외부 API 호출과 프로그램 실행은 애플리케이션의 실행 코드가 수행합니다.

**다섯째**, Agent는 목표를 수행하고, Harness는 실행을 관리·통제하며, Workflow는 작업 절차를 정의합니다. MCP는 외부 도구와 통신하는 표준 규약이고, SDK는 이러한 기능을 개발하는 데 활용하는 도구 묶음입니다.

**여섯째**, AI 서비스 개발에서는 Agent 수를 늘리는 것보다 책임 범위와 도구 권한을 명확히 정의하고, 실제 실행 결과를 객관적으로 평가하는 것이 중요합니다.

이번 기록을 기반으로 실제 코드 분석과 소규모 구현 실험을 진행하고, 그 결과를 계속 Log에 누적할 계획입니다. 구현과 검증이 완료된 결과는 별도의 Portfolio 산출물로 정리할 예정입니다.

---

## 참고자료

### Hugo

- [Hugo 공식 문서](https://gohugo.io/documentation/)
- [Taxonomies](https://gohugo.io/content-management/taxonomies/)
- [Page Bundles](https://gohugo.io/content-management/page-bundles/)
- [Front Matter](https://gohugo.io/content-management/front-matter/)
- [Templates](https://gohugo.io/templates/)
- [Multilingual Mode](https://gohugo.io/content-management/multilingual/)

### GitHub

- [Understanding GitHub Actions](https://docs.github.com/en/actions/get-started/understand-github-actions)
- [GitHub Actions Limits](https://docs.github.com/en/actions/reference/limits)
- [GitHub-hosted Runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
- [Custom Workflows with GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [GitHub 추가 제품 및 기능 약관](https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features)

### AI Agent·MCP

- [Model Context Protocol 공식 문서](https://modelcontextprotocol.io/)
- [MCP Architecture](https://modelcontextprotocol.io/docs/learn/architecture)
- [MCP Tools Specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Norma SDK](https://github.com/Autumn-27/Norma)
- [ARTEX 파생 공개 구현](https://github.com/jiwoochris/artex-global)

### GPT·Plugin

- [OpenAI Custom GPT 종료 및 이전 FAQ](https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq)
- [OpenAI GPT Actions 설정](https://help.openai.com/en/articles/9442513-configuring-actions-in-gpts)

---

*작성 기준일: 2026년 11월 5일*

*문서 성격: 기술 학습·기존 시스템 구조 분석 및 후속 설계 아이디어 기록*

*검증 범위: 공식 기술 문서 및 공개 저장소의 설정·의존성 확인. 자체 AI 서비스의 구현·성능 검증은 아직 수행하지 않았습니다.*
