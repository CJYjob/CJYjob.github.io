---
title: "학습 중"
description: "학습 중인 내용을 AI 없이 직접 기재합니다. 추후 다른 게시글로 이전될 예정입니다."
date: 2026-11-05T00:00:00-00:00
---

# 블로그 학습 중

## Hugo
정적 사이트 생성기(Static Site Generator, SSG)입니다. 
일반적으로 사이트를 빌드할 때 실행됩니다. 
동적 웹사이트는 방문자 요청이 들어오면 서버 애플리케이션에서 요청에 맞춰 처리하여 응답을 생성 및 전달합니다. 
반면, Hugo 블로그는 먼저 Hugo로 사이트를 빌드하고 완성된 파일을 Github Pages에 저장하고 있다가, 방문자 요청 시 단순 전달하는 구조입니다. 

## YAML
YAML은 설정과 데이터를 표현하는 파일 형식입니다. 확장자는 `.yaml` 또는 `.yml`을 사용합니다. 예를 들어 다음과 같은 설정을 작성할 수 있습니다.
``` yaml
title: "최준영의 자람"
theme: "PaperMod"
buildDrafts: false

menu:
 main:
  - name: "Log"
   url: "/log/"
  - name: "Portfolio"
   url: "/portfolio/"
```
여기서 중요한 문법은 네가지 입니다.

|문법|의미|
|---|---|
|title: "..."|이름과 값의 쌍|
|buildDrafts: false|참/거짓 값|
|들여쓰기|상위/하위 구조 표현|
|- name: ...|목록의 한 항목|

JSON과 비슷한 데이터를 표현할 수 있지만, 사람이 읽고 편집하기 쉽도록 작성된 형식입니다.
특히, **들여쓰기가 문법의 일부**이므로 주의해야 합니다. 일반적으로 공백을 사용하고 탭은 사용하지 않습니다.
YAML은 파일의 형식일 뿐입니다. `hugo.yaml`은 Hugo가 해석하는 설정이고, `.github/workflows/hugo.yaml`은 Github Actions가 해석하는 설정입니다.

### 현재 블로그의 hugo.yaml 해석
핵심은 `hugo.yaml`이 프로그램의 실행 코드가 아니라 Hugo에게 웹사이트를 어떻게 만들지 알려주는 설정이라는 점입니다. 
``` yaml
baseURL: "https://cjyjob.github.io/"
title: "최준영의 자람"
theme: "PaperMod"
timeZone: "Asia/Seoul"
```
- baseURL: 웹사이트의 기본 주소
- title: 사이트 제목
- theme: 사용할 테마
- timeZone: 날짜를 처리할 시간대
<br>

``` yaml
languages:
 ko:
  contentDir: content/ko
  languageCode: ko-KR
```
한국어 콘텐츠의 경로를 content/ko 로 지정합니다. 
<br>

``` yaml
buildDrafts: false
buildFuture: false
```
게시 조건으로 각각 초안과 미래 날짜 게시글을 일반 빌드에서 제외한다는 뜻입니다.
<br>

```yaml
menu:
 main:
  - identifier: log
   name: "📒 Log"
   url: /log/
   weight: 10
```
메뉴에 log 항목을 추가하고 `/log/`로 연결합니다. `weight`는 메뉴의 정렬 순서를 결정하는 데 사용됩니다. 

## Github Actions
Github가 제공하는 자동화 실행 플랫폼입니다. Github 저장소에 특정 이벤트가 발생하면 미리 정의한 작업을 실행합니다.
그 작업을 정의한 파일을 **워크플로(Workflow)**라고 합니다.
현재 블로그의 예시로는 `.github/workflows/hugo.yaml`이 있습니다.

이 파일에 적힌 작업이 실행되면 Github는 일반적으로 **러너(Runner)**라는 실행 환경을 준비합니다. 
현재 블로그 설정에서는 Github가 제공하는 Ubuntu 가상 머신을 사용합니다.

즉 워크플로우는 다음의 순서를 따릅니다.
```
1. Github 저장소에 이벤트(커밋, 수동 실행, 등) 발생
2. Github Actions Runner
  a. Hugo 프로그램 다운로드 및 설치
  b. Github 저장소 코드 가져오기
  c. Hugo --gc --minify 실행
  d. 빌드 산출물 업로드
3. GitHub Pages로 빌드 산출물 배포 (방문자 요청시 완성된 파일 제공)
```

현재 설정에 다음 코드가 있습니다.
``` yaml
jobs:
 build:
  runs-on: ubuntu-latest
  env:
   HUGO_VERSION: 0.152.2
```
이는 build 라는 작업을 Ubuntu Runner에서 실행하고 Hugo 버전을 지정한다는 뜻입니다.

그리고 다음 명령으로 Hugo를 설치합니다.
``` bash
wget -O ... hugo_extended_0.152.2_linux-amd64.deb
sudo dpkg -i ...
```
이후 hugo 명령을 실행해 사이트를 생성합니다.

Github Actions는 CI/CD를 구현할 수 있는 도구입니다.
### CI/CD
#### CI(Continuous Integration) - 현재 블로그의 Hugo
코드 변경을 자동으로 통합하고 빌드 및 검사하는 과정
#### CD(Continuous Delivery/Deployment) - 현재 블로그의 Github Pages
빌드 결과를 배포 가능한 상태로 만들거나 실제 배포하는 과정

## 현재 배포 워크플로
`/.github/workflows/hugo.yaml` 가 실제 파일입니다. 큰 구조만 보겠습니다.
``` yaml
name: Deploy Hugo site to Pages

on:
 push:
  branches:
   - main
 workflow_dispatch:
```
워크플로의 이름과 실행 조건입니다.
- name: Github Actions 화면에 표시되는 이름
- on: 워크플로를 실행할 이벤트
- push: main에 코드가 반영될 때 실행
- workflow_dispatch: Github에서 수동 실행 가능
<br>

``` yaml
jobs:
 merge_workout:
  runs-on: ubuntu-latest

 build:
  runs-on: ubuntu-latest

 deploy:
  runs-on: ubuntu-latest
  needs: build
```
여기서 jobs는 작업들의 집합이고, 각 작업 안에는 순서대로 실행하는 steps가 들어갑니다. 세 작업의 역할은 다음과 같습니다.
|JOB|역할|
|---|---|
|merge_workout|Python으로 운동 기록 병합|
|build|Hugo로 웹사이트 생성|
|deploy|빌드 결과를 Github Pages에 배포|
`deploy`의 `needs: build`는 빌드 작업이 성공적으로 끝난 뒤 배포 작업을 실행한다는 의미입니다.

참고로 on, jobs, steps, runs-on, uses, run 등은 Github Actions가 정의한 설정 키워드입니다. YAML 자체에 이런실행 기능이 있는 것은 아닙니다.

## PaperMod
Hugo가 웹사이트를 만드는 엔진이라면, PaperMod는 웹사이트의 기본 화면 구조와 디자인을 제공하는 테마입니다.
예를 들어 동일한 Markdown 글이라도 어떤 테마를 적용하느냐에 따라 글 목록, 메뉴, 본문 폭, 다크 모드, 페이지 디자인 등이 달라집니다.

현재 저장소에서는 다음 위치에 있습니다. `themes/PaperMod/`

그리고 `hugo.yaml`에서 다음과 같이 지정합니다.
``` yaml
theme: "PaperMod"
```
PaperMod는 HTML 템플릿과 스타일, 일부 기능 구현도 포함합니다.
현재 블로그의 `layouts/` 폴더는 기본 테마를 유지하면서 블로그만의 화면과 기능을 추가하거나 덮어쓰는 곳입니다. 그래서 테마 원본을 직접 수정하는 것보다 `layouts/`를 활용하는 방법을 배우는 것이 좋습니다.

### Python
python은 일반적으로 인터프리터 방식으로 실행하는 고수준 프로그래밍 언어입니다. 사용자가 작성한 `.py` 파일은 사람이 읽을 수 있는 소스코드이고, 실행하려면 Python 실행 환경이 필요합니다.
현재 운동 자동화도 Github Actions Runner에 Python을 설치한 뒤 다음 명령으로 실행합니다.
``` bash
python scripts/merge_workout_pending.py
```

## 실제 파일 구조 예시
예를 들어 운동 기록 페이지를 보면,
### 입력 데이터 처리 영역
data/workout_pending_*.json(새 운동 기록을 임시로 보관) 
-> scripts/merge_workout_pending.py(운동 기록 검사 및 병합)
-> data/workout.json(누적 운동 데이터)
### 웹페이지 생성 영역
content/ko/portfolio/workout.md(운동 페이지 본문과 그래프 삽입 위치), 
layouts/shortcodes/(운동 데이터로 표와 그래프를 만드는 사용자 정의 기능), 
themes/PaperMod/ + hugo.yaml(기본 디자인과 전체 사이트 설정) 
-> Hugo 빌드
-> Github Pages
와 같습니다. 즉, 한 파일이 모든 기능을 담당하지 않습니다.
