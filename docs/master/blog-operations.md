# Junyoung's Growth — Blog Setup and Operation Complete Guide

## Document Information

| Item | Content |
|------|---------|
| Document Version | 2.3 |
| Last Updated | August 2026 |
| Purpose | Blog setup process documentation and operation guide |
| Audience | Blog owner and Claude/ChatGPT AI |

This manual covers *blog technical operations only*. The persona, asset workflow, and coach operation conventions of the *self-management support system* — which uses this blog as its operating ground — are defined in a separate document (`docs/master/system-operation.md`).

---

# Part 1: Project Overview

## 1.1 Blog Basic Information

| Item | Content |
|------|---------|
| Blog Name | 최준영의 자람 (Junyoung's Growth) |
| URL | https://cjyjob.github.io |
| GitHub Repository | https://github.com/CJYjob/CJYjob.github.io |
| Owner | Junyoung Choi (CJYjob) |
| Created | December 2024 |
| Major Restructure | August 2026 (`content/ko` flat taxonomy migration) |

## 1.2 Blog Concept

"배우고, 경험하고, 성장하는 과정을 기록한다."

### Menu Structure

| Menu | Icon | URL | Purpose |
|------|------|-----|---------|
| Log | 📒 | /log/ | Raw accumulated data — incomplete work, reflections, structured-data time series |
| Portfolio | 🗂️ | /portfolio/ | Completed outputs and externally publishable artifacts |
| About | 📋 | /about/ | Blog introduction and meta information |
| Search | 🔍 | /search/ | Post search |

The menu structure separates assets by *completeness*: *incomplete → log*, *complete → portfolio*. Detailed asset classification principles are defined in `docs/master/system-operation.md` section *C-2-1-2 (완결성)*.

## 1.3 Technology Stack Summary

| Component | Technology | Role |
|-----------|------------|------|
| Static Site Generator | Hugo Extended | Markdown → HTML build |
| Theme | PaperMod | Layout and styling |
| Hosting | GitHub Pages | Static site hosting |
| CI/CD | GitHub Actions | Build and deploy on push |
| Search | PaperMod Fuse.js | Client-side post search |
| Analytics | Google Analytics | Traffic analytics |
| Search Indexing | Google Search Console | Indexing and SEO monitoring |
| Diagrams | Mermaid.js | Flowcharts, sequence diagrams, mind maps |
| Charts | Chart.js | Structured-data visualization |
| Data | Hugo Site.Data | JSON data loading at build time |

## 1.4 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Development PC                          │
│            Hugo + Git + VS Code + Markdown                     │
└──────────────────────────────┬──────────────────────────────────┘
                               │ git push
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Content Repository (GitHub)                 │
│        Markdown + JSON Data + Hugo config + Theme      │
└─────────────────────────────────────────────────────────────────┘
                               │ GitHub Actions
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                       Hugo Build Pipeline                        │
│             Markdown/Data → HTML/CSS/JS                         │
└──────────────────────────────┬──────────────────────────────────┘
                               │ Deploy
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                         GitHub Pages                             │
│                  https://cjyjob.github.io                       │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                  ┌────────────┴────────────┐
                  ↓                         ↓
        Google Search Console       Google Analytics
```

---

# Part 2: Initial Setup

## 2.1 GitHub Repository Creation

### Repository Settings

```
Repository name: CJYjob.github.io
Visibility: Public
Initialize: README (optional)
```

GitHub Pages user site repositories must follow the naming convention:

```
{username}.github.io
```

For this project:

```
CJYjob.github.io
```

## 2.2 Local Development Environment

### Required Tools

- Git
- Hugo Extended
- VS Code
- Web browser

### Verify Git

```bash
git --version
```

Expected example:

```text
git version 2.x.x
```

### Install Hugo Extended

Windows (Chocolatey):

```powershell
choco install hugo-extended
```

Windows (Winget):

```powershell
winget install Hugo.Hugo.Extended
```

macOS:

```bash
brew install hugo
```

Linux:

```bash
sudo apt install hugo
```

Verify:

```bash
hugo version
```

The output should include:

```text
extended
```

## 2.3 Clone Repository

```bash
git clone https://github.com/CJYjob/CJYjob.github.io.git
cd CJYjob.github.io
```

## 2.4 Initialize Hugo Site

If starting from an empty repository:

```bash
hugo new site . --force
```

Basic generated structure:

```
.
├── archetypes/
├── assets/
├── content/
├── data/
├── layouts/
├── static/
├── themes/
└── hugo.toml
```

This project uses `hugo.yaml` instead of `hugo.toml`.

## 2.5 PaperMod Theme Installation

### Add Theme as Git Submodule

```bash
git submodule add https://github.com/adityatelange/hugo-PaperMod themes/PaperMod
```

Initialize submodule:

```bash
git submodule update --init --recursive
```

Commit:

```bash
git add .
git commit -m "Add PaperMod theme"
git push
```

### Verify `.gitmodules`

```ini
[submodule "themes/PaperMod"]
    path = themes/PaperMod
    url = https://github.com/adityatelange/hugo-PaperMod
```

### Important: Clone with Submodules

When cloning the repository later:

```bash
git clone --recurse-submodules https://github.com/CJYjob/CJYjob.github.io.git
```

If already cloned:

```bash
git submodule update --init --recursive
```

## 2.6 Hugo Configuration

### `hugo.yaml`

```yaml
baseURL: "https://cjyjob.github.io/"
languageCode: "ko-kr"
title: "최준영의 자람"
theme: "PaperMod"
timeZone: "Asia/Seoul"
googleAnalytics: "G-5TKCHJG4NQ"
enableRobotsTXT: true

defaultContentLanguage: ko
defaultContentLanguageInSubdir: false
languages:
  ko:
    contentDir: content/ko
    languageCode: ko-KR
    languageName: 한국어
    title: "최준영의 자람"
    weight: 1

buildDrafts: false
buildFuture: false
buildExpired: false
enableEmoji: true

markup:
  goldmark:
    renderer:
      unsafe: true
  highlight:
    codeFences: true
    guessSyntax: true
    lineNos: true
    style: monokai

menu:
  main:
    - { identifier: log,       name: "📒 Log",       url: /log/,       weight: 10 }
    - { identifier: portfolio, name: "🗂️ Portfolio", url: /portfolio/, weight: 20 }
    - { identifier: about,     name: "📋 About",     url: /about/,     weight: 30 }
    - { identifier: search,    name: "🔍 검색",      url: /search/,    weight: 40 }

params:
  env: production
  title: "최준영의 자람"
  description: "배우고, 경험하고, 성장하는 기록"
  keywords: [보안, Security, 개발, Development, AI, RPA, 성장, 기록]
  author: "최준영"

  assets:
    favicon: "/favicon.ico"
    favicon16x16: "/favicon-16x16.png"
    favicon32x32: "/favicon-32x32.png"
    apple_touch_icon: "/apple-touch-icon.png"

  defaultTheme: auto
  disableThemeToggle: false

  ShowReadingTime: true
  ShowShareButtons: true
  ShowPostNavLinks: true
  ShowBreadCrumbs: true
  ShowCodeCopyButtons: true
  ShowWordCount: true
  ShowRssButtonInSectionTermList: true

  mainSections:
    - log
    - portfolio

  homeInfoParams:
    Title: "🌱 최준영의 자람"
    Content: "배우고, 경험하고, 성장하는 과정을 기록한다."

  socialIcons:
    - name: github
      url: "https://github.com/CJYjob"

  fuseOpts:
    isCaseSensitive: false
    shouldSort: true
    location: 0
    distance: 1000
    threshold: 0.4
    minMatchCharLength: 0
    keys: ["title", "permalink", "summary", "content"]

pagination:
  pagerSize: 5

outputs:
  home:
    - HTML
    - RSS
    - JSON

taxonomies:
  category: categories
  tag: tags
  series: series
```

The `params.mainSections: [log, portfolio]` setting restricts where the PaperMod theme pulls recent posts for the home page. `about` is a meta page and is not exposed in the home list.

## 2.6 GitHub Pages Configuration

Repository → Settings → Pages:

```
Source: GitHub Actions
```

Do not use "Deploy from a branch" when using the Hugo GitHub Actions workflow.

---

# Part 3: GitHub Actions CI/CD

## 3.1 Workflow File

Path:

```
.github/workflows/hugo.yaml
```

## 3.2 Workflow Purpose

The workflow performs:

```
Push to main
      ↓
Checkout repository
      ↓
Initialize submodules
      ↓
Install Hugo Extended
      ↓
Build static site
      ↓
Upload Pages artifact
      ↓
Deploy to GitHub Pages
```

## 3.3 Typical Workflow Structure

```yaml
name: Deploy Hugo site to Pages

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          submodules: recursive
          fetch-depth: 0

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: latest
          extended: true

      - name: Build
        run: hugo --minify

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./public

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

## 3.4 Structured Data Build Flow

```
/data/*.json
      │
      ├── Hugo Site.Data ───────────────┐
      │                                 │
      ↓                                 ↓
layouts/shortcodes/*.html         content/*.md
      │                                 │
      └──────────────┬──────────────────┘
                     ↓
                hugo --minify
                     ↓
                  public/
                     ↓
              GitHub Pages
```

In this blog, build inputs include both *Markdown* and *JSON files under `/data/`*. Hugo auto-loads `/data/` as `Site.Data` at build time. Markdown content can then render this data through Hugo shortcodes. See `docs/master/system-operation.md` section *C-2-2-2 (정형 데이터 자산 흐름)* for the full data convention.

### Key Commands

```bash
# local build
hugo --minify

# local preview
hugo server -D
```

## 3.5 Deployment Verification

After a push:

1. Open GitHub Actions.
2. Confirm the Hugo workflow succeeds.
3. Confirm the Pages deployment job succeeds.
4. Open the public URL and verify the changed page.
5. For cache-sensitive changes, use a cache-busting query or independent curl/browser request.

Repository verification and public-site verification are separate gates. A successful commit does not by itself prove that Pages has deployed the intended HTML.

---

# Part 4: Repository Structure

## 4.1 Complete Structure

```text
CJYjob.github.io/
│
├── .github/
│   └── workflows/
│       └── hugo.yaml              # GitHub Actions CI/CD config
│
├── archetypes/                    # Content templates
│   ├── default.md
│   ├── log.md
│   └── portfolio.md
│
├── content/
│   └── ko/                        # language content root (published without /ko/ prefix)
│       ├── about/
│       │   └── index.md
│       ├── categories/            # category hub pages
│       ├── log/                   # 📒 raw accumulated data
│       │   ├── _index.md
│       │   ├── {topic}/
│       │   │   └── {intermediate-N}/index.md
│       │   └── reflection/
│       │       ├── daily/
│       │       ├── weekly/
│       │       ├── monthly/
│       │       ├── quarterly/
│       │       ├── semiyearly/
│       │       └── yearly/
│       ├── portfolio/             # 🗂️ completed outputs
│       │   ├── _index.md
│       │   ├── {completed-topic}/index.md
│       │   ├── insights/index.md
│       │   └── workout.md
│       ├── series/                # series hub pages
│       └── search.md
│
├── data/                          # Hugo Site.Data source
│   ├── workout.json
│   └── workout_mapping.json
│
├── docs/
│   └── master/                    # operational SSOT; not Hugo content
│
├── layouts/
│   └── shortcodes/
│       ├── datatable.html
│       ├── workout-volume-chart.html
│       ├── workout-cardio-chart.html
│       ├── alert.html
│       ├── youtube.html
│       ├── codesandbox.html
│       ├── docker-example.html
│       └── mermaid.html
│
├── scripts/
│   └── merge_workout_pending.py
│
├── static/
│   ├── images/
│   └── CNAME                      # only if a custom domain is used
│
├── themes/
│   └── PaperMod/                  # Git submodule
│
├── hugo.yaml
├── .gitmodules
└── README.md
```

The legacy top-level content trees (`content/log`, `content/portfolio`, `content/about`, etc.) were removed after migration verification. Do not recreate them.

## 4.2 Directory Responsibilities

| Directory | Responsibility |
|-----------|----------------|
| `content/ko/log/` | Incomplete materials and reflections accumulate here |
| `content/ko/portfolio/` | Completed outputs displayed here |
| `data/` | Structured JSON data loaded by Hugo as `Site.Data` |
| `layouts/shortcodes/` | Reusable rendering logic |
| `static/` | Files published directly from the site root |
| `content/ko/categories/` | Category hub pages |
| `content/ko/series/` | Series hub pages |
| `docs/master/` | Operational SSOT; not Hugo content |

## 4.3 Asset Placement Rules

| Asset Type | Location |
|------------|----------|
| Incomplete study/practice material | `content/ko/log/...` |
| Daily/weekly/monthly/etc. reflection | `content/ko/log/reflection/...` |
| Completed unstructured output | `content/ko/portfolio/...` |
| Structured time-series raw data | `/data/{activity}.json` |
| Static structured mapping data | `/data/{mapping}.json` |
| Structured-data public page | `content/ko/portfolio/{activity}.md` or directory-style `index.md` |
| Operational SSOT | `docs/master/...` |

Detailed asset classification is defined in `docs/master/system-operation.md` section *C-2-1 (자산 구조)*.

## 4.4 Source Path vs Public URL

This repository sets Korean `contentDir` to `content/ko`; Hugo publishes those source files without a `/ko/` URL prefix. When linking between pages in Markdown, use the *live URL* (not the source path).

| Source | Public URL |
|--------|------------|
| `content/ko/log/_index.md` | `/log/` |
| `content/ko/portfolio/_index.md` | `/portfolio/` |
| `content/ko/about/index.md` | `/about/` |
| `content/ko/log/reflection/daily/2026-06-01/index.md` | `/log/reflection/daily/2026-06-01/` |
| `content/ko/portfolio/workout.md` | `/portfolio/workout/` |

Use `[Portfolio](/portfolio/)` (live URL), not `[Portfolio](/content/ko/portfolio/)`. The latter results in a 404 on the live site.

## 4.5 Legacy URLs

When content moves, preserve old public URLs with Hugo `aliases` where needed. Hugo aliases may render as static HTML with `canonical` and `meta refresh` rather than an HTTP 301/302 response. Therefore legacy verification must inspect the alias HTML or final browser behavior, not only the HTTP status code.

---

# Part 5: Content Model

## 5.1 Log

Log stores *raw accumulated data*.

Examples:

- incomplete study notes
- in-progress practice logs
- daily/weekly/monthly/quarterly/semiannual/annual reflections
- structured-data time series (physically under `/data/`, conceptually raw data)

## 5.2 Portfolio

Portfolio stores *completed outputs*.

Examples:

- completed study output
- project write-up
- vulnerability analysis
- structured-data public dashboard/page
- accumulated insights

## 5.3 About

About stores blog meta information, including:

- blog purpose
- owner introduction
- technical stack
- external tool attribution where required

## 5.4 Search

Search is implemented using PaperMod's JSON output and Fuse.js.

The `outputs.home` configuration must include `JSON`.

---

# Part 6: Front Matter Standard

## 6.1 Standard Base Fields

Every post must use YAML Front Matter with these six base fields:

```yaml
---
title: "Post Title"
date: 2026-05-28
draft: false
description: "Short description for SEO and listing"
categories: ["Security"]
tags: ["XSS", "Web Security"]
---
```

### Required Fields

| Field | Purpose |
|-------|---------|
| `title` | Page title |
| `date` | Page date |
| `draft` | Publication state |
| `description` | SEO/list summary |
| `categories` | Primary classification |
| `tags` | Search/discovery keywords |

### Publication Rule

```yaml
draft: false
```

must be confirmed before final publication.

## 6.2 Conditional Fields

Add only when needed:

```yaml
aliases:
  - /old/path/
series:
  - "Web Security"
weight: 10
ShowToc: true
TocOpen: false
```

Do not add coach metadata such as:

```text
session_started_at
session_ended_at
recorded_by
time_lookup_status
```

Coach activity timestamps are already preserved in Git history. User activity timestamps belong in structured data or natural body text according to the system-operation document.

## 6.3 Archetypes

### `archetypes/default.md`

```yaml
---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: false
description: ""
categories: []
tags: []
---
```

### `archetypes/log.md`

```yaml
---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: false
description: ""
categories: []
tags: []
---
```

### `archetypes/portfolio.md`

```yaml
---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: false
description: ""
categories: []
tags: []
---
```

---

# Part 7: Coach Repository Operations

## 7.1 Confirmation Gate

Changes via coaches use the *platform confirmation modal as the only approval gate*; a separate chat commit preview or `approve/proceed` message is not required. The full safety convention is defined in `docs/master/system-operation.md` section *PartB-5 (저장소 쓰기 확인 게이트)*.

## 7.2 Coach Repository Write Standard

Coach-driven writes use the GitHub Git Database API. The previous Contents API + Base64 PUT flow is retired.

1. Read latest `main` commit and tree.
2. Read current raw UTF-8 text for files being modified.
3. Apply only the necessary changes; do not rewrite unrelated content.
4. Create a tree using the current tree as `base_tree`.
5. Create a commit whose parent is the starting `main` commit.
6. Update `main` with `force:false`.
7. Re-read latest `main` and the target raw/tree state before declaring success.
8. On 409/non-fast-forward, restart from the latest `main` and reconstruct the intended changes.

## 7.3 Content Paths

| Asset | Path Pattern |
|-------|--------------|
| Log — in-progress study/practice | `content/ko/log/{topic}/{intermediate-1}/index.md` |
| Log — daily reflection | `content/ko/log/reflection/daily/2026-06-01/index.md` |
| Log — weekly reflection | `content/ko/log/reflection/weekly/2026-W23/index.md` |
| Portfolio — completed unstructured asset | `content/ko/portfolio/{completed-topic}/index.md` |
| Portfolio — insights | `content/ko/portfolio/insights/index.md` (single accumulating page) |
| Portfolio — structured-data public page | `content/ko/portfolio/{activity}/index.md` |

Some existing single-page assets, such as workout, use a flat Markdown file (`content/ko/portfolio/workout.md`). Preserve the existing path unless a migration is explicitly required.

## 7.4 Fine-Grained PAT Scope

For coach tokens scoped to this repository:

- **Contents**: Read/Write
- **Metadata**: Read
- **Actions Read**: only for the coach responsible for blog infrastructure

Do not reuse one token across all coaches. Keep blast radius isolated.

Detailed token policy is defined in `docs/master/system-operation.md` section *C-1 (GPT Action 토큰 관리 규약)*.

---

# Part 8: Structured Data System

## 8.1 Design

Structured data is stored separately from Markdown:

```
/data/{activity}.json
        ↓
Hugo Site.Data
        ↓
layouts/shortcodes/{renderer}.html
        ↓
content/ko/portfolio/{activity}.md
        ↓
public page
```

The repository currently does not maintain a separate `/schemas/` directory. Structured-data validation follows the established field structure in the existing JSON plus the activity-specific convention in `docs/master/system-operation.md`. If formal JSON Schema validation is introduced later, add `/schemas/` and update both documents at the same time.

## 8.2 Structured Data Write Flow

1. Read the latest `main` commit and tree, then read `/data/{activity}.json` as raw UTF-8.
2. Append or update the intended record in memory.
3. Validate the new data against the existing field structure and activity-specific convention.
4. Write the complete updated JSON through a Git Data API tree entry.
5. Create a commit whose parent is the starting `main` commit, update `main` with `force:false`, then re-read raw/tree state.
6. If `main` changed and the ref update is non-fast-forward, restart from the latest `main` and reconstruct the update.

The *original file is always fetched first* to avoid overwriting prior records.

## 8.3 Datatable Shortcode

`layouts/shortcodes/datatable.html` renders structured data as an HTML table.

### Example Usage

Use the actual executable shortcode form in a post. When documenting the syntax itself, escape it so Hugo does not execute it.

```text
{{< datatable data="workout" sort="date desc" >}}
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `data` | Yes | `Site.Data` key, e.g. `workout` |
| `sort` | No | `"field asc"` or `"field desc"`; omit to keep original order |

## 8.4 Workout Chart Shortcodes

### Volume Chart

```text
{{< workout-volume-chart >}}
```

Purpose:

- filter `type == "strength"`
- aggregate `sets[].volume_kg`
- render time-volume stacked bar chart

### Cardio Chart

```text
{{< workout-cardio-chart >}}
```

Purpose:

- filter `type == "cardio"`
- use `distance_km`
- render time-distance bar chart

## 8.5 Hugo Site.Data + Client JS Pattern

Important Hugo behavior:

```go-html-template
{{ site.Data.workout | jsonify }}
```

is inserted into JavaScript as a **JSON string**, not directly as a JavaScript array/object.

Incorrect:

```javascript
const data = {{ site.Data.workout | jsonify }};
data.filter(...); // TypeError: data.filter is not a function
```

Correct:

```javascript
const data = JSON.parse({{ site.Data.workout | jsonify }});
data.filter(...);
```

This pattern must be used in client-side Chart.js shortcodes that consume `Site.Data`.

## 8.6 Raw HTML and Goldmark

Custom HTML/JavaScript in Markdown requires:

```yaml
markup:
  goldmark:
    renderer:
      unsafe: true
```

Without this setting, raw HTML may be escaped or omitted.

## 8.7 Shortcode Escape

When *showing* shortcode syntax in documentation, escape it so Hugo does not execute it.

When *using* a shortcode in a real post, use the executable form.

Do not confuse documentation escape syntax with production shortcode syntax.

---

# Part 9: Content Creation Workflow

## 9.1 Manual Post Creation

### Log Post

```bash
hugo new --kind log log/security/xss/part-1/index.md
```

### Portfolio Post

```bash
hugo new --kind portfolio portfolio/security/xss/index.md
```

Edit the generated file, then:

```bash
git add .
git commit -m "Add XSS study output"
git push
```

## 9.2 Coach-Driven Post Creation

Typical flow:

```
User activity
    ↓
Coach summarizes/structures
    ↓
Determine log or portfolio
    ↓
Build Markdown with Front Matter
    ↓
Platform confirmation modal
    ↓
Git Data API write
    ↓
GitHub Actions build
    ↓
Public verification
```

## 9.3 Asset Conversion: Log → Portfolio

When an intermediate output is completed:

1. Preserve the original log page.
2. Create/update the portfolio output.
3. Add references between log and portfolio where appropriate.
4. Update the portfolio index page if the output belongs to a multi-page asset.

The source log is preserved for traceability.

---

# Part 10: Search

## 10.1 Search Page

`content/ko/search.md`:

```yaml
---
title: "검색"
layout: "search"
url: "/search/"
summary: "search"
---
```

## 10.2 JSON Output

`hugo.yaml` must include:

```yaml
outputs:
  home:
    - HTML
    - RSS
    - JSON
```

PaperMod uses this JSON output for Fuse.js search.

---

# Part 11: Mermaid Diagrams

## 11.1 Mermaid Shortcode

Example shortcode file:

```html
<div class="mermaid">
  {{ .Inner | safeHTML }}
</div>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>
```

## 11.2 Usage

```text
{{< mermaid >}}
flowchart TD
    A[Input] --> B[Process]
    B --> C[Output]
{{< /mermaid >}}
```

## 11.3 Recommended Uses

- system architecture
- request/response flow
- security attack path
- learning roadmap
- automation pipeline

---

# Part 12: Reusable Visual Shortcodes

## 12.1 Alert Box

Example:

```text
{{< alert type="warning" >}}
Never test a production system without authorization.
{{< /alert >}}
```

Suggested types:

- info
- warning
- danger
- success

## 12.2 YouTube Embed

```text
{{< youtube id="VIDEO_ID" >}}
```

## 12.3 CodeSandbox Embed

```text
{{< codesandbox id="SANDBOX_ID" >}}
```

## 12.4 Docker Example

```text
{{< docker-example >}}
docker run --rm -it example/image
{{< /docker-example >}}
```

---

# Part 13: SEO

## 13.1 Google Search Console

Register:

```text
https://search.google.com/search-console
```

Recommended property:

```text
https://cjyjob.github.io/
```

## 13.2 Sitemap

Hugo generates:

```text
/sitemap.xml
```

Submit:

```text
https://cjyjob.github.io/sitemap.xml
```

## 13.3 Robots

With:

```yaml
enableRobotsTXT: true
```

Hugo generates:

```text
/robots.txt
```

## 13.4 SEO Checklist

- meaningful `title`
- useful `description`
- stable public URL
- category/tag discipline
- internal links
- image alt text
- sitemap submitted
- no accidental draft/future date

---

# Part 14: Google Analytics

## 14.1 Configuration

In `hugo.yaml`:

```yaml
googleAnalytics: "G-XXXXXXXXXX"
```

Replace with the real GA4 Measurement ID.

## 14.2 Verification

After deployment:

1. Open the site.
2. Check GA4 Realtime.
3. Confirm page view appears.

---

# Part 15: Local Testing

## 15.1 Preview Drafts

```bash
hugo server -D
```

## 15.2 Production-Like Build

```bash
hugo --minify
```

## 15.3 Check Generated Output

```bash
ls public
```

Windows:

```powershell
Get-ChildItem public
```

## 15.4 Useful Verification

```bash
hugo --printPathWarnings
```

Check for:

- broken resource paths
- duplicate target paths
- invalid templates
- missing shortcode references

---

# Part 16: Troubleshooting

## 16.1 Theme Not Found

Symptom:

```text
failed to load modules
```

Fix:

```bash
git submodule update --init --recursive
```

## 16.2 GitHub Actions Build Failure

Check:

- Hugo version
- Extended build
- submodule checkout
- invalid Front Matter
- invalid shortcode syntax
- malformed JSON under `/data/`

## 16.3 Page Not Reflected

1. Confirm the intended commit is on `main`.
2. Confirm Actions deployment succeeded.
3. Confirm the source file is under `content/ko/`.
4. Confirm `draft: false`.
5. Check the public URL without a `/ko/` prefix.
6. Use cache busting if necessary.

## 16.4 Home Page Does Not Show Posts

1. Verify `params.mainSections` in `hugo.yaml` matches the section directory names under the configured language `contentDir` (`content/ko/`).
2. Confirm posts are not drafts/future-dated.
3. Confirm section index files and content paths are valid.

## 16.5 Search Does Not Work

Check:

```yaml
outputs:
  home:
    - HTML
    - RSS
    - JSON
```

Also confirm `content/ko/search.md` uses the PaperMod search layout.

## 16.6 Raw HTML Not Rendered

Confirm:

```yaml
markup:
  goldmark:
    renderer:
      unsafe: true
```

## 16.7 Datatable/Chart `filter is not a function`

Cause:

`Site.Data` was serialized into a JavaScript string.

Fix:

```javascript
const data = JSON.parse({{ site.Data.x | jsonify }});
```

## 16.8 GitHub Action Authentication

### Symptom: read works but write fails

Public repositories allow anonymous reads. A successful GET does not prove that the PAT used for writes is valid.

**Solution**: Verify token status in GitHub Settings → Fine-grained tokens. Reissue if needed and update the Authentication value in the GPT builder. Token issuance and rotation conventions are defined in `docs/master/system-operation.md` section *C-1 (GPT Action 토큰 관리 규약)*.

### Symptom: 409 Conflict / non-fast-forward

**Cause**: `main` changed after the coach read the starting commit/tree, so the attempted ref update is no longer a fast-forward.

**Solution**: Re-fetch latest `main` and its tree, reconstruct the intended minimal changes, create a new tree/commit, and retry the `main` update with `force:false`. The repository write convention (latest main/tree → modify → create tree/commit → update main with `force:false` → verify raw/tree) is defined in `docs/master/system-operation.md` section *C-1 (GPT Action 토큰 관리 규약)*.

## 16.9 Confirmation Modal Does Not Appear

**Solution**: Verify `x-openai-isConsequential: true` on the repository write operations in the coach schema, then re-save. The confirmation gate convention is defined in `docs/master/system-operation.md` section *PartB-5 (저장소 쓰기 확인 게이트)*.

## 16.10 Structured Data Format Mismatch

### Symptom: Coach halts a write because a new record does not match the existing data structure

1. Inspect the current `/data/{activity}.json` structure and the activity-specific convention.
2. Compare the attempted record with the existing field structure and value conventions.
3. Correct the new data rather than silently changing the established structure. If the structure itself must change, update the operating documents and dependent rendering logic together.

The repository currently does not maintain a separate `/schemas/` directory. The structured-data convention is defined in `docs/master/system-operation.md` section *C-2-2-2*.

## 16.11 Raw GitHub Cache Delay

`raw.githubusercontent.com` may lag for minutes after a commit.

For fresh verification, prefer:

- GitHub API raw/blob retrieval
- repository blob view

Do not treat stale raw CDN output as proof that the commit failed.

## 16.12 Korean Base64 Corruption (Historical)

Historical coach writes using the GitHub Contents API encoded the body as Base64, and Korean text occasionally became corrupted.

Current standard:

- use the Git Data API tree/commit/ref flow
- write UTF-8 text through tree-entry `content`
- re-read raw/blob after the commit

---

# Part 17: Security Practice Environment

## 17.1 Docker-Based Labs

Recommended labs:

- DVWA
- OWASP Juice Shop
- WebGoat

Example:

```bash
docker run --rm -it -p 3000:3000 bkimminich/juice-shop
```

## 17.2 Practice Documentation Pattern

Each lab write-up should record:

1. objective
2. environment
3. vulnerable flow
4. reproduction steps
5. root cause
6. mitigation
7. evidence/screenshots
8. references

Do not publish secrets, credentials, private customer information, or unauthorized target details.

---

# Part 18: Search Console / Analytics Operations

## 18.1 Routine Checks

### Search Console

- indexing status
- coverage errors
- search queries
- CTR
- sitemap state

### Analytics

- users
- sessions
- popular pages
- referral sources
- engagement

## 18.2 Suggested Review Cycle

Weekly:

- failed builds
- broken links/images
- indexing issues

Monthly:

- traffic trend
- top pages
- search queries
- content gaps

---

# Part 19: Publishing Checklist

## 19.1 Before Commit

- [ ] Correct English-only repository path
- [ ] Six base Front Matter fields present
- [ ] `draft: false` for final public content
- [ ] Conditional fields used only when required
- [ ] Internal links use public URLs, not source paths
- [ ] No accidental `/ko/` prefix in public links
- [ ] Referenced static assets exist
- [ ] Required legacy aliases preserved
- [ ] No unrelated body text rewritten

## 19.2 After Commit

- [ ] `main` points to the intended commit
- [ ] Raw/tree state matches intended changes
- [ ] GitHub Actions deployment succeeded
- [ ] Public URL reflects the latest content
- [ ] Legacy aliases resolve correctly when applicable

---

# Part 20: Migration Notes

## 20.1 Current Canonical Source Tree

The current canonical content tree is:

```text
content/ko/
├── log/
├── portfolio/
├── about/
├── categories/
├── series/
└── search.md
```

The historical top-level content trees were removed after migration verification.

## 20.2 Legacy URL Preservation

During structural migrations:

1. preserve old URLs with `aliases`
2. verify alias HTML/canonical target
3. verify new canonical page
4. update internal links to the new public URL
5. only then remove obsolete source trees

---

# Part 21: Operational Principles

## 21.1 Minimal Change

When editing an existing file:

- fetch the current raw content first
- modify only the necessary lines
- do not rewrite unrelated paragraphs
- preserve headings, terminology, and ordering unless the change requires otherwise

## 21.2 Source of Truth

For blog technical operations:

```text
docs/master/blog-operations.md
```

For the self-management support system:

```text
docs/master/system-operation.md
```

For the security career roadmap:

```text
docs/master/security-five-year-plan.md
```

If a local/uploaded copy conflicts with `main`, the GitHub `main` copy is authoritative after migration is complete.

---

# Appendix A: Quick Command Reference

## Git

```bash
git status
git add .
git commit -m "message"
git push
```

## Hugo

```bash
hugo server -D
hugo --minify
```

## Submodules

```bash
git submodule update --init --recursive
```

## Docker

```bash
docker ps
docker images
```

---

# Appendix B: Key File Reference

| File | Purpose |
|------|---------|
| `hugo.yaml` | Hugo/PaperMod configuration |
| `.github/workflows/hugo.yaml` | CI/CD |
| `content/ko/log/_index.md` | Log landing page |
| `content/ko/portfolio/_index.md` | Portfolio landing page |
| `content/ko/about/index.md` | About page |
| `content/ko/search.md` | Search page |
| `/data/*.json` | Structured data |
| `layouts/shortcodes/*.html` | Data/visual rendering |
| `docs/master/system-operation.md` | System operation convention |
| `docs/master/blog-operations.md` | This manual |

---

# Appendix C: Known Technical Pitfalls

## C.1 Hugo `Site.Data` + Client JavaScript

Use:

```javascript
const data = JSON.parse({{ site.Data.x | jsonify }});
```

not:

```javascript
const data = {{ site.Data.x | jsonify }};
```

when JavaScript expects an array/object.

## C.2 Raw HTML

Custom HTML/JS requires:

```yaml
markup:
  goldmark:
    renderer:
      unsafe: true
```

## C.3 Shortcode Escape

Use escaped syntax only when *displaying shortcode syntax as text*. Use executable syntax in real content.

## C.4 Raw CDN Cache

`raw.githubusercontent.com` can lag after a commit. Use GitHub API raw/blob for immediate verification.

## C.5 Korean Text Writes

The current Git Data API flow avoids the historical Base64 encoding path. Re-read the stored UTF-8 content after Korean-text writes.

---

# Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2024-12 | 1.0 | Initial blog setup |
| 2025 | 1.x | PaperMod customization and operational refinements |
| 2026-06 | 2.0 | Menu restructure (Log/Portfolio), `/data/` and `/schemas/` introduced, structured-data rendering mechanism, coach Action integration acknowledged, system-document cross-references added, troubleshooting expanded |
| 2026-08 | 2.3 | Updated source paths to `content/ko`, documented category/series hubs and legacy-tree removal, aligned the current `hugo.yaml`, retired Contents API/Base64 write guidance in favor of Git Data API, and recorded the current no-`/schemas/` implementation. |

---

# SSOT Rule

The GitHub `main` version of this document (`docs/master/blog-operations.md`) is the canonical blog-operations reference. Uploaded/local copies are snapshots only.
