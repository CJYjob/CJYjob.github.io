# Junyoung's Growth — Blog Setup and Operation Complete Guide

## Document Information

| Item | Content |
|------|---------|
| Document Version | 2.2 |
| Last Updated | June 2026 |
| Purpose | Blog setup process documentation and operation guide |
| Audience | Blog owner and Claude/ChatGPT AI |

This manual covers *blog technical operations only*. The persona, asset workflow, and coach operation conventions of the *self-management support system* — which uses this blog as its operating ground — are defined in a separate document (`자기관리_보조_시스템_운영_철학_및_구현.md`).

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
| Major Restructure | May 2026 (Diary/Gallery/Lab → Log/Portfolio) |

## 1.2 Blog Concept

"배우고 경험한 내용을 기록하고 공유하는 공간"

### Menu Structure

| Menu | Icon | URL | Purpose |
|------|------|-----|---------|
| Log | 📝 | /log/ | Raw accumulated data — incomplete work, reflections, structured-data time series |
| Portfolio | 🖼️ | /portfolio/ | Completed outputs and externally publishable artifacts |
| About | 📋 | /about/ | Blog introduction and meta information |
| Search | 🔍 | /search/ | Post search |

The menu structure separates assets by *completeness*: *incomplete → log*, *complete → portfolio*. Detailed asset classification principles are defined in `자기관리_보조_시스템_운영_철학_및_구현.md` section *C-2-1-2 (완결성)*.

## 1.3 Technology Stack Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Browser                              │
│                    https://cjyjob.github.io                      │
└─────────────────────────────────────────────────────────────────┘
                                 ↑
                                 │ HTTPS (Free SSL)
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                   GitHub Pages (Static Hosting)                  │
│                    Serves HTML/CSS/JS files                      │
└─────────────────────────────────────────────────────────────────┘
                                 ↑
                                 │ Automatic Deployment (CD)
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                   GitHub Actions (CI/CD)                         │
│              Auto Hugo build and deploy on Commit                │
└─────────────────────────────────────────────────────────────────┘
                                 ↑
                                 │ Commit (GitHub Web / Git / GPT Coach Action)
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Content Repository (GitHub)                 │
│        Markdown + JSON Data + Schemas + Hugo config + Theme      │
└─────────────────────────────────────────────────────────────────┘
```

## 1.4 Version Information (As of June 2026)

### Core Tools

| Tool | Version | Purpose | Notes |
|------|---------|---------|-------|
| Hugo | 0.152.2 Extended | Static site generator | Extended version required |
| PaperMod | Latest (Git Submodule) | Hugo theme | Requires Hugo 0.146.0+ |
| Git | Latest | Version control | Required for local work |

### GitHub Actions Environment

| Item | Version/Setting |
|------|-----------------|
| Runner | ubuntu-latest |
| Hugo | 0.152.2 (specified in workflow) |
| Node.js | Auto-installed |

### External Services

| Service | Purpose | Status |
|---------|---------|--------|
| GitHub Pages | Free hosting | ✅ Active |
| Google Search Console | SEO, search registration | ✅ Registered |
| Google Analytics | Visitor analytics | ✅ Connected |

### CDN Libraries

| Library | Purpose | Load Method |
|---------|---------|-------------|
| Mermaid.js | Diagrams/Mindmaps | jsdelivr CDN (latest) |

### Docker Images (For Security Practice)

| Image | Purpose | Default Port |
|-------|---------|--------------|
| vulnerables/web-dvwa | Web vulnerability practice | 80 |
| bkimminich/juice-shop | OWASP Top 10 practice | 3000 |
| webgoat/webgoat | Web security learning | 8080, 9090 |

---

# Part 2: Blog Setup Guide (Step-by-Step)

This section is a reference guide for building the same blog from scratch.

## 2.1 Prerequisites

### Required Accounts

| Service | URL | Purpose |
|---------|-----|---------|
| GitHub | https://github.com | Repository, hosting |
| Google | https://google.com | Search Console, Analytics |

### Local Development Environment (Optional)

The current operator manages content through the **GitHub web interface** and **coach GPT Actions**. A local environment is optional; install the following tools if needed.

#### Windows Installation (Using Winget)

```powershell
# Install Hugo Extended
winget install Hugo.Hugo.Extended

# Install Git
winget install Git.Git

# Install Docker Desktop (for security practice)
winget install Docker.DockerDesktop

# Install VS Code (optional)
winget install Microsoft.VisualStudioCode

# Verify installation (restart PowerShell first)
hugo version
git --version
docker --version
```

## 2.2 Create Hugo Site (Local)

```powershell
# Navigate to working directory
cd C:\Projects

# Create Hugo site
hugo new site my-blog

# Navigate to directory
cd my-blog

# Initialize Git
git init

# Install PaperMod theme (as submodule)
git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
```

## 2.3 Create GitHub Repository

1. Go to GitHub
2. Click **New repository**
3. Repository name: `[username].github.io` (e.g., `CJYjob.github.io`)
4. Select **Public**
5. Click **Create repository**

## 2.4 GitHub Actions Workflow Setup

Create `.github/workflows/hugo.yaml` file:

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
  group: "pages"
  cancel-in-progress: false

defaults:
  run:
    shell: bash

jobs:
  build:
    runs-on: ubuntu-latest
    env:
      HUGO_VERSION: 0.152.2
    steps:
      - name: Install Hugo CLI
        run: |
          wget -O ${{ runner.temp }}/hugo.deb https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.deb \
          && sudo dpkg -i ${{ runner.temp }}/hugo.deb
      
      - name: Install Dart Sass
        run: sudo snap install dart-sass
      
      - name: Checkout
        uses: actions/checkout@v4
        with:
          submodules: recursive
          fetch-depth: 0
      
      - name: Setup Pages
        id: pages
        uses: actions/configure-pages@v5
      
      - name: Install Node.js dependencies
        run: "[[ -f package-lock.json || -f npm-shrinkwrap.json ]] && npm ci || true"
      
      - name: Build with Hugo
        env:
          HUGO_CACHEDIR: ${{ runner.temp }}/hugo_cache
          HUGO_ENVIRONMENT: production
          TZ: Asia/Seoul
        run: |
          hugo \
            --gc \
            --minify \
            --baseURL "${{ steps.pages.outputs.base_url }}/"
      
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

## 2.5 hugo.yaml Configuration (Currently in Use)

```yaml
baseURL: "https://cjyjob.github.io/"
languageCode: "ko-kr"
title: "최준영의 자람"
theme: "PaperMod"
googleAnalytics: "G-XXXXXXXXXX"  # Replace with actual measurement ID
enableRobotsTXT: true
buildDrafts: false
buildFuture: false
buildExpired: false
enableEmoji: true

mainSections:
  - log
  - portfolio

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
    - identifier: log
      name: 📝 Log
      url: /log/
      weight: 10
    - identifier: portfolio
      name: 🖼️ Portfolio
      url: /portfolio/
      weight: 20
    - identifier: about
      name: 📋 About
      url: /about/
      weight: 30
    - identifier: search
      name: 🔍 검색
      url: /search/
      weight: 40

params:
  env: production
  title: "최준영의 자람"
  description: "배우고 경험한 내용을 기록하고 공유하는 공간"
  keywords: [보안, Security, 개발, Development, 자동화, AI, RPA, 성장, 기록]
  author: "최준영"
  
  defaultTheme: auto
  disableThemeToggle: false
  
  ShowReadingTime: true
  ShowShareButtons: true
  ShowPostNavLinks: true
  ShowBreadCrumbs: true
  ShowCodeCopyButtons: true
  ShowWordCount: true
  ShowRssButtonInSectionTermList: true
  
  homeInfoParams:
    Title: "🌱 최준영의 자람"
    Content: "배우고 경험한 내용을 기록하고 공유하는 공간입니다."
  
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

The `mainSections: [log, portfolio]` setting restricts where the PaperMod theme pulls recent posts for the home page. `about` is a meta page and is not exposed in the home list.

## 2.6 GitHub Pages Configuration

1. Repository → **Settings** tab
2. Left menu → **Pages**
3. Source: Select **GitHub Actions**
4. Save

## 2.7 Google Search Console Registration

1. Go to [Google Search Console](https://search.google.com/search-console)
2. **Add property** → **URL prefix** → `https://cjyjob.github.io`
3. Select **HTML tag** verification method
4. Add the provided meta tag to `layouts/partials/extend_head.html`:

```html
<!-- Google Search Console -->
<meta name="google-site-verification" content="verification-code" />
```

5. Click **Verify**
6. Submit `sitemap.xml` in the **Sitemaps** menu

## 2.8 Google Analytics Setup

### Get Measurement ID

1. Go to [Google Analytics](https://analytics.google.com)
2. Create account → Create property → Create web stream
3. Copy the measurement ID (e.g., `G-ABC123DEF4`)

### Apply to Blog

Add to `hugo.yaml` file:

```yaml
googleAnalytics: "G-ABC123DEF4"  # Your measurement ID
```

---

# Part 3: Technical Details

## 3.1 Hugo (Static Site Generator)

### Concept

Hugo is a **Static Site Generator (SSG)**.

| Aspect | Dynamic Site | Static Site |
|--------|--------------|-------------|
| Operation | Server generates pages on request | Pre-generated HTML files served |
| Server | Requires PHP, Node.js, etc. | Web server only |
| Database | Required | Not required |
| Speed | Relatively slow | Very fast |
| Security | Vulnerability risks | Minimal attack surface |
| Hosting Cost | Paid server required | Free hosting possible (GitHub Pages) |

### How It Works

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Markdown      │     │      Hugo       │     │   HTML/CSS/JS   │
│   (.md files)   │ ──→ │   Build Engine  │ ──→ │  (Static files) │
│   + Theme       │     │                 │     │   public/ folder│
│   + Data (JSON) │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
      [Input]               [Process]               [Output]
```

In this blog, build inputs include both *Markdown* and *JSON files under `/data/`*. Hugo auto-loads `/data/` as `Site.Data` at build time. Markdown content can then render this data through Hugo shortcodes. See `자기관리_보조_시스템_운영_철학_및_구현.md` section *C-2-2-2 (정형 데이터 자산 흐름)* for the full data convention.

### Key Commands

```bash
# Create new site
hugo new site [sitename]

# Create new content
hugo new [path]/[filename].md

# Run development server (including drafts)
hugo server -D

# Production build
hugo --minify

# Check version
hugo version
```

## 3.2 PaperMod (Hugo Theme)

### Role

- Provides blog design and layout
- Dark mode support
- SEO optimization
- Search functionality
- Automatic table of contents

### Location

```
themes/PaperMod/  (Managed as Git submodule)
```

### Requirements

- Hugo Extended version
- Hugo 0.146.0 or higher

## 3.3 GitHub Pages (Hosting)

### Concept

Free static website hosting service provided by GitHub.

### Features

| Item | Content |
|------|---------|
| Cost | Free |
| URL | `[username].github.io` |
| SSL | Automatic HTTPS |
| Storage | 1GB recommended per repository |
| Bandwidth | 100GB per month |

## 3.4 GitHub Actions (CI/CD)

### CI/CD Concepts

| Term | Full Name | Meaning |
|------|-----------|---------|
| CI | Continuous Integration | Automatic build/test on code changes |
| CD | Continuous Deployment | Automatic deployment on successful build |

### Workflow

```
1. Commit on GitHub web / Git push / Coach Action commit
                ↓
2. GitHub Actions auto-triggers
                ↓
3. Ubuntu virtual environment created
                ↓
4. Hugo installed (specified version)
                ↓
5. Repository code checked out (including submodules)
                ↓
6. hugo --minify executed (build)
                ↓
7. public/ folder deployed to GitHub Pages
                ↓
8. https://cjyjob.github.io updated
```

### Configuration File Location

```
.github/workflows/hugo.yaml
```

## 3.5 Mermaid.js (Diagrams)

### Role

Creates text-based diagrams within Markdown.

### Supported Diagrams

- `mindmap`: Mind maps
- `flowchart`: Flowcharts
- `graph TD/LR`: Directional graphs
- `sequenceDiagram`: Sequence diagrams
- `classDiagram`: Class diagrams

### Usage Example

```markdown
{{</* mermaid */>}}
mindmap
  root((Topic))
    Subtopic1
      DetailA
      DetailB
    Subtopic2
      DetailC
{{</* /mermaid */>}}
```

---

# Part 4: Directory Structure

## 4.1 Complete Structure

```
CJYjob.github.io/
│
├── .github/
│   └── workflows/
│       └── hugo.yaml              # GitHub Actions CI/CD config
│
├── archetypes/                    # Content templates
│   ├── default.md                 # Default template
│   ├── log.md                     # Log template
│   └── portfolio.md               # Portfolio template
│
├── content/                       # Markdown content
│   │
│   ├── log/                       # 📝 Log (raw accumulated data)
│   │   ├── _index.md              # Log section index
│   │   ├── {topic}/               # In-progress study/practice materials
│   │   │   └── {intermediate-N}/
│   │   │       └── index.md
│   │   └── reflection/            # Reflections (daily/weekly/monthly/quarterly/semiannual/annual)
│   │       ├── daily/
│   │       │   └── {YYYY-MM-DD}/
│   │       │       └── index.md
│   │       ├── weekly/
│   │       ├── monthly/
│   │       ├── quarterly/
│   │       ├── semiannual/
│   │       └── annual/
│   │
│   ├── portfolio/                 # 🖼️ Portfolio (completed outputs)
│   │   ├── _index.md              # Portfolio section index
│   │   ├── {completed-topic}/     # Completed unstructured document assets
│   │   │   └── index.md
│   │   ├── workout/               # Workout structured-data public page
│   │   │   └── index.md
│   │   └── insights/              # Insights (from reflections)
│   │       └── index.md
│   │
│   ├── about/                     # 📋 About
│   │   └── index.md
│   │
│   └── search.md                  # 🔍 Search page
│
├── data/                          # 🗂️ Structured data (Site.Data)
│   ├── workout.json
│   ├── workout_mapping.json
│   ├── sleep.json
│   ├── meal.json
│   └── ... (per-activity JSON)
│
├── schemas/                       # 🔍 JSON Schemas (validation only, not used by Hugo build)
│   ├── workout.schema.json
│   ├── workout_mapping.schema.json
│   ├── sleep.schema.json
│   └── ... (per-activity schemas)
│
├── layouts/                       # Custom layouts
│   ├── partials/
│   │   └── extend_head.html       # <head> extension (Mermaid, Analytics, Search Console, etc.)
│   │
│   └── shortcodes/                # Custom shortcodes
│       ├── mermaid.html           # Diagrams
│       ├── datatable.html         # Structured data table rendering (with sort support)
│       ├── workout-volume-chart.html  # Strength volume stacked bar chart (Chart.js)
│       ├── workout-cardio-chart.html  # Cardio distance bar chart (Chart.js)
│       ├── warning.html           # Warning box
│       ├── youtube.html           # YouTube embedding
│       ├── codesandbox.html       # CodeSandbox embedding
│       └── docker-run.html        # Docker command box
│
├── static/                        # Static files
│   ├── images/                    # Images
│   └── css/
│       └── custom.css             # Custom CSS
│
├── themes/
│   └── PaperMod/                  # Hugo theme (Git submodule)
│
├── public/                        # Build output (auto-generated, Git ignored)
│
├── hugo.yaml                      # Hugo main config
├── .gitignore                     # Git ignore list
└── .gitmodules                    # Git submodule config
```

## 4.2 Key File Roles

| File/Folder | Role |
|-------------|------|
| `hugo.yaml` | Overall blog settings (title, menu, mainSections, theme params, etc.) |
| `content/log/` | Incomplete materials and reflections accumulate here |
| `content/portfolio/` | Completed outputs displayed here |
| `data/` | Structured data (JSON). Hugo auto-loads as Site.Data |
| `schemas/` | JSON schemas. Coaches validate at write time (unrelated to Hugo build) |
| `layouts/shortcodes/` | User-defined shortcodes (datatable, etc.) |
| `static/` | Images, CSS, and other static assets |
| `themes/PaperMod/` | Theme files (do not modify) |
| `.github/workflows/` | CI/CD automation settings |

## 4.3 Source Path vs Live URL

Hugo strips the `content/` prefix at build time. When linking between pages in Markdown, use the *live URL* (not the source path).

| Location | Source Path (in repository) | Live URL (after publish) |
|----------|-----------------------------|--------------------------|
| Log index | `content/log/_index.md` | `/log/` |
| Portfolio index | `content/portfolio/_index.md` | `/portfolio/` |
| About | `content/about/index.md` | `/about/` |
| Daily reflection (example) | `content/log/reflection/daily/2026-06-01/index.md` | `/log/reflection/daily/2026-06-01/` |
| Workout public page | `content/portfolio/workout/index.md` | `/portfolio/workout/` |

Use `[Portfolio](/portfolio/)` (live URL), not `[Portfolio](/content/portfolio/)`. The latter results in a 404 on the live site.

---

# Part 5: Content Creation Guide

## 5.1 Working Methods

This blog is modified through three paths:

1. **GitHub web interface** — operator edits files directly.
2. **Automation coach GPT Action** — automation/blog operations changes.
3. **Life coach and other domain coach GPT Actions** — operational records, reflections, and domain asset updates.

Changes via coaches always pass through *commit preview → user confirmation modal*. The full safety convention is defined in `자기관리_보조_시스템_운영_철학_및_구현.md` section *PartB-5 (저장소 쓰기 확인 게이트)*.

## 5.2 Creating Content on GitHub Web

### New Post Creation Procedure

#### Step 1: Access Repository

```
https://github.com/CJYjob/CJYjob.github.io
```

#### Step 2: Create New File

1. Click **Add file** button
2. Select **Create new file**

#### Step 3: Enter File Path

Enter the full path in the top input field (typing `/` auto-creates folders):

| Asset Type | File Path Example |
|------------|-------------------|
| Log — in-progress study/practice | `content/log/{topic}/{intermediate-1}/index.md` |
| Log — daily reflection | `content/log/reflection/daily/2026-06-01/index.md` |
| Log — weekly reflection | `content/log/reflection/weekly/2026-W23/index.md` |
| Portfolio — completed unstructured asset | `content/portfolio/{completed-topic}/index.md` |
| Portfolio — insights | `content/portfolio/insights/index.md` (single accumulating page) |
| Portfolio — structured-data public page | `content/portfolio/{activity}/index.md` |

#### Step 4: Write Content

```markdown
---
title: "Post Title"
date: 2026-06-01
draft: false
description: "Post description (for SEO)"
categories: ["Category"]
tags: ["Tag1", "Tag2"]
---

Write body content here...
```

#### Step 5: Commit (Save)

1. Click **Commit changes...** at bottom of page
2. Enter commit message (e.g., `Add: new daily reflection`)
3. Click **Commit changes**

#### Step 6: Verify Deployment

1. Check build status in **Actions** tab (✅ green)
2. Verify result at `https://cjyjob.github.io`

## 5.3 Editing Existing Files

1. Click on file to open
2. Click **pencil icon** (Edit this file) at top right
3. Edit content
4. Click **Commit changes**

## 5.4 Deleting Files

1. Click on file to open
2. Click **trash icon** at top right
3. Click **Commit changes**

## 5.5 Uploading Images

### Method 1: Upload to static folder

1. Navigate to `static/images/` folder
2. **Add file** → **Upload files**
3. Drag and drop image files
4. **Commit changes**

### Method 2: Reference in content

```markdown
![Image description](/images/filename.png)
```

## 5.6 Front Matter (Post Metadata)

YAML-format settings at the top of every Markdown file:

```yaml
---
title: "Post Title"                # Required
date: 2026-06-01                   # Creation date (required)
draft: false                       # true excludes from build
description: "Post description"    # For SEO, preview
categories: ["Log", "Web"]         # Categories
tags: ["XSS", "Security"]          # Tags
series: ["OWASP Top 10"]           # Series (serial posts)
weight: 10                         # Sort order (lower = first)
ShowToc: true                      # Show table of contents
TocOpen: true                      # TOC expanded state
---
```

### draft Setting

| Value | Meaning |
|-------|---------|
| `draft: true` | Draft — excluded from build, not shown on site |
| `draft: false` | Published — included in build, shown on site |

Operational standard: *always verify `draft: false` before commit*.

## 5.7 Shortcode Usage

### Mermaid (Diagrams/Mindmaps)

```markdown
{{</* mermaid */>}}
mindmap
  root((Web Security))
    Injection
      SQL Injection
      Command Injection
    XSS
      Stored XSS
      Reflected XSS
{{</* /mermaid */>}}
```

### Datatable (Structured Data Table)

```markdown
{{</* datatable activity="workout" */>}}
{{</* datatable activity="workout" sort="date desc" */>}}
```

Renders `/data/{activity}.json` as a cumulative table. The `sort` parameter accepts `"field asc"` or `"field desc"` form; omit to keep original order. The underlying data flow and schema convention are defined in `자기관리_보조_시스템_운영_철학_및_구현.md` section *C-2-2-2*.

### Workout Volume Chart (Strength Stacked Bar)

```markdown
{{</* workout-volume-chart days="30" */>}}
```

Reads `/data/workout.json`, filters records with `type: "strength"` from the last N days (default 30), and renders a stacked bar chart of volume (kg) per exercise per day using Chart.js. The chart's data source is the same `volume_kg` field accumulated per set (= `weight_kg × reps`).

Schema convention is defined in `자기관리_보조_시스템_운영_철학_및_구현.md` section *C-2-2-3*. See also the *Hugo Site.Data + Client JS Pattern* note in the Appendix.

### Workout Cardio Chart (Distance Bar)

```markdown
{{</* workout-cardio-chart days="30" */>}}
```

Reads `/data/workout.json`, filters records with `type: "cardio"` from the last N days (default 30), and renders a bar chart of cumulative distance (km) per exercise per day. Uses `distance_km` if present; otherwise computes from `speed_kmh × (duration_min / 60)`.

### Warning (Warning Box)

```markdown
{{</* warning */>}}
This experiment should only be used for educational purposes.
{{</* /warning */>}}
```

### YouTube Embedding

```markdown
{{</* youtube id="VIDEO_ID" title="Video Title" */>}}
```

`https://youtube.com/watch?v=ABC123` → `id="ABC123"`

### CodeSandbox Embedding

```markdown
{{</* codesandbox id="sandbox-id" height="400" */>}}
```

### Docker Run Command Box

```markdown
{{</* docker-run image="vulnerables/web-dvwa" port="80" name="dvwa" localport="8080" */>}}
```

## 5.8 Asset-Type Content Templates

### Log — In-Progress Study/Practice

```markdown
---
title: "Topic — Intermediate Output 1"
date: 2026-06-01
draft: false
description: "Scope covered by this intermediate output"
categories: ["Log"]
tags: ["topic-tag"]
ShowToc: true
---

## Goal

- Goal 1
- Goal 2

## Progress

(Accumulated work-in-progress content)

## Blockers / Attempts

- (If any)

## Next Steps

- (If any)
```

### Log — Daily Reflection

```markdown
---
title: "2026-06-01 Daily Reflection"
date: 2026-06-01
draft: false
description: "Daily reflection"
categories: ["Log", "Reflection"]
tags: ["Daily Reflection"]
---

## Plan

- (Day's planned items)

## Record

- HH:MM — Activity
- HH:MM — Activity

## Analysis

- (Time allocation and execution rate analysis)

## Reflection

- (What went well / what to improve / carry into next cycle)
```

Higher reflection tiers (weekly, monthly, quarterly, semiannual, annual) follow the same skeleton. Tier handling and insight-extraction rules are defined in `자기관리_보조_시스템_운영_철학_및_구현.md` section *C-2-2-1*.

### Portfolio — Completed Unstructured Asset

```markdown
---
title: "Completed Topic"
date: 2026-06-01
draft: false
description: "Summary of the completed output (SEO / external readers)"
categories: ["Portfolio", "{domain}"]
tags: ["{domain-tag}"]
ShowToc: true
---

## Overview

(Topic introduction in reader-friendly tone)

## Mind Map

{{</* mermaid */>}}
mindmap
  root((Topic))
    Subtopic1
    Subtopic2
{{</* /mermaid */>}}

## Body

### Section 1

(Completed content — intermediate outputs accumulated in log, now restructured)

## References

- [Link](URL)
```

### Portfolio — Structured-Data Public Page

```markdown
---
title: "Workout Records"
date: 2026-06-01
draft: false
description: "Cumulative workout records"
categories: ["Portfolio", "Workout"]
tags: ["Workout", "Data"]
---

## Overview

Cumulative workout records. Data updates are owned solely by the workout coach.

## Cumulative Data

{{</* datatable name="workout" */>}}

## Activity Analysis

(Activity analysis — updated by the workout coach)
```

### Portfolio — Insights

```markdown
---
title: "Insights"
date: 2026-06-01
draft: false
description: "Cumulative insights extracted from reflections"
categories: ["Portfolio", "Insights"]
tags: ["Insight"]
ShowToc: true
---

## YYYY-MM-DD — Insight title

(Insight body — appended by the life coach when extracted during reflection)

---

## YYYY-MM-DD — Another insight

(Same pattern continues)
```

---

# Part 6: Operations and Maintenance

## 6.1 Daily Operations Workflow

```
1. Organize content ideas
        ↓
2. Create new file via GitHub web or coach GPT
        ↓
3. Write content in Markdown (or coach presents preview)
        ↓
4. Verify draft: false
        ↓
5. Commit (coach: confirm modal)
        ↓
6. Check build in Actions tab (takes 1-2 minutes)
        ↓
7. Verify result on site
```

## 6.2 GitHub Actions Status Check

| Status | Icon | Meaning | Action |
|--------|------|---------|--------|
| Success | ✅ Green | Deployment complete | None |
| In Progress | 🟡 Yellow | Building | Wait |
| Failed | ❌ Red | Error occurred | Check logs |

### How to Check Logs on Failure

1. Click Actions tab
2. Click failed workflow
3. Click red step to see error message

## 6.3 Google Search Console Monitoring

### Check Frequency: Weekly

- **Performance**: Check impressions, clicks
- **Indexing → Pages**: Check indexed page count
- **Sitemaps**: Check sitemap status

### Request Indexing for New Content

1. Enter new post URL in top search bar
2. Click **Request indexing**

## 6.4 Google Analytics Monitoring

### Items to Check

| Menu | What to Check |
|------|---------------|
| Real-time | Current visitor count |
| Reports → Acquisition | Traffic sources (search, direct, SNS, etc.) |
| Reports → Engagement | Popular pages, session duration |

## 6.5 Theme Updates (When Needed)

When PaperMod theme update is required:

### Update in Local Environment

```powershell
cd C:\Projects\my-blog
git submodule update --remote --merge
git add .
git commit -m "Update: PaperMod theme"
git push
```

### Cautions

- Build errors may occur after theme update
- Check Hugo version compatibility

---

# Part 7: Docker Practice Environment (For Security Practice)

## 7.1 Docker Basic Concepts

Docker is a platform that runs applications in isolated environments called **containers**.

### Advantages

- Environment consistency (runs the same anywhere)
- Isolation (separated from host system)
- Easy install/uninstall

## 7.2 Docker Basic Commands

```powershell
# Run container
docker run -d --name [name] -p [localport]:[containerport] [image]

# Check running containers
docker ps

# Check all containers
docker ps -a

# Stop container
docker stop [name]

# Remove container
docker rm [name]

# Check container logs
docker logs [name]

# List images
docker images

# Clean unused images
docker image prune
```

## 7.3 Vulnerability Practice Environments

### DVWA (Damn Vulnerable Web Application)

```powershell
# Run
docker run -d --name dvwa -p 8080:80 vulnerables/web-dvwa

# Access: http://localhost:8080
# Login: admin / password
# Initial setup: Click Create/Reset Database

# Shutdown
docker stop dvwa && docker rm dvwa
```

### OWASP Juice Shop

```powershell
# Run
docker run -d --name juice-shop -p 3000:3000 bkimminich/juice-shop

# Access: http://localhost:3000

# Shutdown
docker stop juice-shop && docker rm juice-shop
```

### WebGoat

```powershell
# Run
docker run -d --name webgoat -p 8080:8080 -p 9090:9090 webgoat/webgoat

# WebGoat Access: http://localhost:8080/WebGoat
# WebWolf Access: http://localhost:9090/WebWolf

# Shutdown
docker stop webgoat && docker rm webgoat
```

---

# Part 8: Troubleshooting Guide

## 8.1 GitHub Actions Build Failure

### Cause 1: Hugo Version Mismatch

**Symptom**: `hugo v0.146.0 or greater is required`

**Solution**:
1. Edit `.github/workflows/hugo.yaml`
2. Verify `HUGO_VERSION: 0.152.2`
3. Commit

### Cause 2: Theme Submodule Missing

**Symptom**: `theme not found` error

**Solution**: Verify `submodules: recursive` setting in workflow

### Cause 3: mainSections Mismatch

**Symptom**: Home page shows empty post list

**Solution**:
1. Verify `mainSections` in `hugo.yaml` matches the directory names under `content/`
2. Current standard: `mainSections: [log, portfolio]`

## 8.2 Changes Not Reflected on Site

### Verification Order

1. **Verify commit completed**
2. **Check build status in Actions tab**
3. **Clear browser cache** (Ctrl+Shift+R)

## 8.3 Google Search Console Indexing Failure

### Sitemap "Couldn't fetch"

**Cause**: Google crawler delay

**Solution**: Wait 24–48 hours for automatic resolution

### Page Not Indexed

**Solution**:
1. Enter the URL in URL inspection tool
2. Click "Request indexing"

## 8.4 Images Not Displaying

### Things to Check

1. Verify file is in `static/images/`
2. Verify path starts with `/images/filename.png`
3. Check filename case sensitivity

## 8.5 Coach GPT Action Failures

### Symptom: 401 Unauthorized

**Cause**: Token expired, revoked, or insufficient permissions.

**Solution**: Verify token status in GitHub Settings → Fine-grained tokens. Reissue if needed and update the Authentication value in the GPT builder. Token issuance and rotation conventions are defined in `자기관리_보조_시스템_운영_철학_및_구현.md` section *C-1 (GPT Action 토큰 관리 규약)*.

### Symptom: 422 Unprocessable Entity (sha mismatch)

**Cause**: File has been modified since the coach read it; the sha is stale.

**Solution**: The coach should re-fetch and retry automatically. If it persists, check the conflict directly on GitHub. The structured-data write convention (GET → modify/validate → PUT with sha) is defined in `자기관리_보조_시스템_운영_철학_및_구현.md` section *C-2-2-2*.

### Symptom: Modal does not appear and write fires immediately

**Cause**: `x-openai-isConsequential: true` missing from the write operation in the OpenAPI schema.

**Solution**: Verify the value in the coach's schema for write operations (PUT, DELETE), then re-save. The confirmation gate convention is defined in `자기관리_보조_시스템_운영_철학_및_구현.md` section *PartB-5 (저장소 쓰기 확인 게이트)*.

## 8.6 Structured Data / Schema Mismatch

### Symptom: Coach halts a write due to schema validation failure

**Solution**:
1. Inspect `/schemas/{activity}.schema.json` directly.
2. Compare the data format the coach attempted with the schema.
3. If the schema is stale, update the schema; if the data is wrong, request the coach to correct it.

Schema updates affect data integrity and should be made carefully. The structured-data convention is defined in `자기관리_보조_시스템_운영_철학_및_구현.md` section *C-2-2-2*.

---

# Part 9: Appendix

## 9.1 Useful Links

### Official Documentation

| Service | URL |
|---------|-----|
| Hugo | https://gohugo.io/documentation/ |
| PaperMod | https://adityatelange.github.io/hugo-PaperMod/ |
| GitHub Pages | https://docs.github.com/en/pages |
| GitHub Actions | https://docs.github.com/en/actions |
| GitHub Contents API | https://docs.github.com/en/rest/repos/contents |
| Mermaid.js | https://mermaid.js.org/ |
| timeapi.io | https://timeapi.io/ |
| JSON Schema | https://json-schema.org/ |

### Vulnerability Practice

| Platform | URL |
|----------|-----|
| DVWA | https://github.com/digininja/DVWA |
| Juice Shop | https://owasp.org/www-project-juice-shop/ |
| WebGoat | https://owasp.org/www-project-webgoat/ |

## 9.2 Common Markdown Syntax

```markdown
# Heading 1
## Heading 2
### Heading 3

**Bold**
*Italic*
~~Strikethrough~~

- List item
- List item

1. Ordered list
2. Ordered list

[Link text](URL)

![Image description](image URL)

`inline code`

​```language
code block
​```

| Header1 | Header2 |
|---------|---------|
| Content1 | Content2 |

> Blockquote
```

## 9.3 Git Commands (For Local Environment)

```bash
# Clone repository
git clone git@github.com:CJYjob/CJYjob.github.io.git

# Check status
git status

# Stage all changes
git add .

# Commit
git commit -m "message"

# Push
git push

# Pull (get remote changes)
git pull

# Initialize submodules
git submodule update --init --recursive

# Update theme
git submodule update --remote --merge
```

## 9.4 Cross-References to System Documentation

This manual covers *blog technical operations only*. The following topics are defined in the system design document.

| Topic | Reference |
|-------|-----------|
| Asset classification and completeness | `자기관리_보조_시스템_운영_철학_및_구현.md` C-2-1 |
| Unstructured document asset flow | C-2-2-1 |
| Structured data asset flow | C-2-2-2 |
| Workout structured-data schema (session_id, sets, etc.) | C-2-2-3 |
| Operational records (reflections, daily pages) | C-2-2-1 |
| Coach personas | C-3 |
| Time signal, time-API mechanism, token management | C-1 |
| Response format, write confirmation gate | PartB-5, PartB-6 |
| Operational diagnostic assets (D group) | Appendix D |

## 9.5 Technical Notes

### Hugo Site.Data + Client JS Pattern

When rendering `/data/*.json` content in client-side JavaScript (Chart.js, custom widgets, etc.), `{{ site.Data.X | jsonify }}` produces a *JSON-encoded string*, not a native JS object/array when embedded into a JS variable. Calling `data.filter(...)` on the result therefore fails with `TypeError: a.filter is not a function`.

Standard implementation: wrap the Hugo expression with `JSON.parse(...)`:

```html
<script>
  const data = JSON.parse({{ site.Data.workout | jsonify }});
  // data is now a real JS array; data.filter(...) etc. work normally
</script>
```

This pattern is used in `workout-volume-chart.html` and `workout-cardio-chart.html`. Any future shortcode that consumes Site.Data from client JS should follow the same pattern.

### Markdown + Raw HTML/Script Rendering

PaperMod with the current `hugo.yaml` (`markup.goldmark.renderer.unsafe: true`) allows raw HTML/script inside markdown bodies. Shortcodes that emit `<div>`, `<canvas>`, and `<script>` elements (such as the workout chart shortcodes) therefore render correctly when called from a content page's markdown body. If this setting is changed back to `unsafe: false`, all client-side chart shortcodes break — verify this setting before any future shortcode that relies on inline script/markup.

### Shortcode Escape Notation vs Live Invocation

Hugo documentation conventions use `{{</* shortcode */>}}` (with `/*` and `*/` inside the braces) to *show* a shortcode in documentation without executing it. When writing instructions for a coach (or any agent) to insert a shortcode into a content file, give the *live invocation form* (`{{< shortcode >}}`) inside code blocks — the agent may copy escape notation verbatim into the content file and break rendering.

---

# Change History

| Date | Version | Changes |
|------|---------|---------|
| 2025-03 | 1.0 | Initial creation — Diary/Gallery/Lab structure |
| 2026-06 | 2.0 | Menu restructure (Log/Portfolio), `/data/` and `/schemas/` introduced, structured-data rendering mechanism, coach Action integration acknowledged, system-document cross-references added, troubleshooting expanded |
| 2026-06 | 2.1 | Restored English tone; removed sections duplicated with system design doc (coach integration table, token rotation, structured-data rendering mechanism); reduced 5.1 to working-paths summary with reference; troubleshooting now cites system doc instead of duplicating |
| 2026-06 | 2.2 | Added workout-volume-chart and workout-cardio-chart shortcodes (Chart.js); datatable shortcode `sort` parameter; datatable attribute fixed from `name` to `activity` (matched implementation); 9.5 Technical Notes added (Hugo Site.Data + Client JS pattern, raw HTML rendering, shortcode escape convention) |

---

# End of Document
