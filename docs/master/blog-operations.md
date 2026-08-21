# Junyoung's Growth - Blog Setup and Operation Complete Guide

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

### Design Principles

- **Growth Journey**: Record learning and experience, not just results
- **Learning → Practice → Output**: Connect theory to hands-on practice and portfolio artifacts
- **Consistency**: Build long-term knowledge assets through continuous documentation
- **Public by Default**: Posts are published unless explicitly marked as draft
- **Automation-friendly**: AI coaches can read, update, and validate repository assets through GitHub Actions/API workflows

## 1.3 Technology Stack

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

### System Architecture

```text
┌─────────────────────────────────────────────────────────────────────┐
│                         GitHub Repository                            │
│        Markdown + JSON Data + Hugo config + Theme      │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ push
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         GitHub Actions                               │
│                   Hugo build + validation                           │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ deploy
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          GitHub Pages                                │
│                      https://cjyjob.github.io                        │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
      Google Search       Google Analytics      Public Users
        Console
```

---

# Part 2: Environment Setup

## 2.1 Prerequisites

### Required Software

| Software | Recommended | Purpose |
|----------|-------------|---------|
| Git | Latest stable | Version control |
| Hugo Extended | Current stable | Local build and preview |
| VS Code | Current stable | Markdown editing |
| GitHub account | - | Repository and Pages hosting |

### Verify Installation

```bash
git --version
hugo version
```

Hugo must be the **Extended** build when the theme or SCSS pipeline requires it.

## 2.2 Clone Repository

```bash
git clone --recurse-submodules https://github.com/CJYjob/CJYjob.github.io.git
cd CJYjob.github.io
```

If already cloned without submodules:

```bash
git submodule update --init --recursive
```

## 2.3 Local Preview

```bash
hugo server -D
```

Default local URL:

```text
http://localhost:1313/
```

Useful options:

```bash
hugo server -D --disableFastRender
hugo server --minify
```

---

# Part 3: Theme and Hugo Configuration

## 3.1 PaperMod Theme

PaperMod is managed as a Git submodule.

```bash
git submodule add https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
git submodule update --init --recursive
```

Do not manually copy theme files into the repository unless intentionally vendoring the theme.

## 3.2 Current `hugo.yaml`

The live repository uses the following configuration pattern:

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

## 3.3 Main Sections

The `params.mainSections: [log, portfolio]` setting restricts where the PaperMod theme pulls recent posts for the home page. `about` is a meta page and is not exposed in the home list.

---

# Part 4: GitHub Pages Deployment

## 4.1 GitHub Actions Workflow

The repository deploys through `.github/workflows/hugo.yaml`.

Typical structure:

```yaml
name: Deploy Hugo site to Pages

on:
  push:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false
```

The workflow checks out the repository including submodules, installs Hugo Extended, builds the site, uploads the Pages artifact, and deploys it.

## 4.2 Build Inputs

In this blog, build inputs include both *Markdown* and *JSON files under `/data/`*. Hugo auto-loads `/data/` as `Site.Data` at build time. Markdown content can then render this data through Hugo shortcodes. See `docs/master/system-operation.md` section *C-2-2-2 (정형 데이터 자산 흐름)* for the full data convention.

## 4.3 Deployment Verification

After a push:

1. Open GitHub Actions.
2. Confirm the Hugo workflow succeeds.
3. Confirm the Pages deployment job succeeds.
4. Open the public URL and verify the changed page.
5. For cache-sensitive changes, use a cache-busting query or independent curl/browser request.

Repository verification and public-site verification are separate gates. A successful commit does not by itself prove that Pages has deployed the intended HTML.

---

# Part 5: Content Structure

## 5.1 Current Repository Structure

```text
├── .github/workflows/hugo.yaml
├── archetypes/
│   ├── default.md
│   ├── log.md
│   └── portfolio.md
├── content/
│   └── ko/
│       ├── about/index.md
│       ├── categories/
│       ├── log/
│       ├── portfolio/
│       ├── series/
│       └── search.md
├── data/
│   ├── workout.json
│   └── workout_mapping.json
├── docs/master/
├── layouts/
│   └── shortcodes/
├── scripts/
│   └── merge_workout_pending.py
├── static/
├── themes/PaperMod/
└── hugo.yaml
```

The legacy top-level content trees (`content/log`, `content/portfolio`, `content/about`, etc.) were removed after migration verification. Do not recreate them.

## 5.2 Directory Responsibilities

| Path | Responsibility |
|------|----------------|
| `content/ko/log/` | Incomplete materials and reflections accumulate here |
| `content/ko/portfolio/` | Completed outputs displayed here |
| `data/` | Structured JSON data loaded by Hugo as `Site.Data` |
| `layouts/shortcodes/` | Reusable rendering logic |
| `static/` | Files published directly from the site root |
| `content/ko/categories/` | Category hub pages |
| `content/ko/series/` | Series hub pages |
| `docs/master/` | Operational SSOT; not Hugo content |

## 5.3 Source Path vs Public URL

This repository sets Korean `contentDir` to `content/ko`; Hugo publishes those source files without a `/ko/` URL prefix. When linking between pages in Markdown, use the *live URL* (not the source path).

| Source | Public URL |
|--------|------------|
| `content/ko/log/_index.md` | `/log/` |
| `content/ko/portfolio/_index.md` | `/portfolio/` |
| `content/ko/about/index.md` | `/about/` |
| `content/ko/log/reflection/daily/2026-06-01/index.md` | `/log/reflection/daily/2026-06-01/` |
| `content/ko/portfolio/workout.md` | `/portfolio/workout/` |

Use `[Portfolio](/portfolio/)` (live URL), not `[Portfolio](/content/ko/portfolio/)`. The latter results in a 404 on the live site.

## 5.4 Legacy URLs

When content moves, preserve old public URLs with Hugo `aliases` where needed. Hugo aliases may render as static HTML with `canonical` and `meta refresh` rather than an HTTP 301/302 response. Therefore legacy verification must inspect the alias HTML or final browser behavior, not only the HTTP status code.

---

# Part 6: Coach Repository Operations

## 6.1 Confirmation Gate

Changes via coaches use the *platform confirmation modal as the only approval gate*; a separate chat commit preview or `approve/proceed` message is not required. The full safety convention is defined in `docs/master/system-operation.md` section *PartB-5 (저장소 쓰기 확인 게이트)*.

### Coach repository write standard

Coach-driven writes use the GitHub Git Database API. The previous Contents API + Base64 PUT flow is retired.

1. Read latest `main` commit and tree.
2. Read current raw UTF-8 text for files being modified.
3. Apply only the necessary changes; do not rewrite unrelated content.
4. Create a tree using the current tree as `base_tree`.
5. Create a commit whose parent is the starting `main` commit.
6. Update `main` with `force:false`.
7. Re-read latest `main` and the target raw/tree state before declaring success.
8. On 409/non-fast-forward, restart from the latest `main` and reconstruct the intended changes.

## 6.2 Content Paths

| Asset | Path Pattern |
|-------|--------------|
| Log — in-progress study/practice | `content/ko/log/{topic}/{intermediate-1}/index.md` |
| Log — daily reflection | `content/ko/log/reflection/daily/2026-06-01/index.md` |
| Log — weekly reflection | `content/ko/log/reflection/weekly/2026-W23/index.md` |
| Portfolio — completed unstructured asset | `content/ko/portfolio/{completed-topic}/index.md` |
| Portfolio — insights | `content/ko/portfolio/insights/index.md` (single accumulating page) |
| Portfolio — structured-data public page | `content/ko/portfolio/{activity}/index.md` |

Some existing single-page assets, such as workout, use a flat Markdown file (`content/ko/portfolio/workout.md`). Preserve the existing path unless a migration is explicitly required.

## 6.3 Front Matter

Standard base fields:

```yaml
---
title: "Post Title"
date: 2026-08-21
draft: false
description: "Post description"
categories: ["Category"]
tags: ["Tag"]
---
```

Conditional fields may be added only when needed:

```yaml
aliases: []
series: []
weight: 10
ShowToc: true
TocOpen: false
```

Do not add coach metadata such as `session_started_at`, `session_ended_at`, `recorded_by`, or `time_lookup_status` to Front Matter.

## 6.4 Archetypes

`archetypes/default.md`, `archetypes/log.md`, and `archetypes/portfolio.md` should inject only the six base Front Matter fields. Conditional fields are added manually when required.

---

# Part 7: Structured Data and Shortcodes

## 7.1 Data Files

Structured data lives under `/data/` and is loaded by Hugo as `Site.Data`.

Examples:

- `/data/workout.json`
- `/data/workout_mapping.json`

## 7.2 Datatable Shortcode

Renders `/data/{activity}.json` as a cumulative table. The `sort` parameter accepts `"field asc"` or `"field desc"` form; omit to keep original order. The underlying data flow and schema convention are defined in `docs/master/system-operation.md` section *C-2-2-2*.

## 7.3 Workout Charts

The workout public page uses structured data and chart shortcodes such as:

- `workout-volume-chart`
- `workout-cardio-chart`
- `datatable`

Schema convention is defined in `docs/master/system-operation.md` section *C-2-2-3*. See also the *Hugo Site.Data + Client JS Pattern* note in the Appendix.

## 7.4 Raw HTML and Goldmark

Custom HTML/JavaScript in Markdown requires:

```yaml
markup:
  goldmark:
    renderer:
      unsafe: true
```

## 7.5 Shortcode Escape

When documenting shortcode syntax, distinguish escaped display examples from actual executable shortcode syntax. Do not leave documentation escape syntax in a post that is intended to execute the shortcode.

---

# Part 8: Troubleshooting

## 8.1 Hugo Build Failure

### Symptom: theme/template error

1. Verify PaperMod submodule state.
2. Run `git submodule update --init --recursive`.
3. Confirm Hugo Extended version.
4. Run a local `hugo --minify` build.

## 8.2 Page Not Reflected

1. Confirm the intended commit is on `main`.
2. Confirm Actions deployment succeeded.
3. Confirm the source file is under `content/ko/`.
4. Confirm `draft: false`.
5. Check the public URL without a `/ko/` prefix.
6. Use cache busting if necessary.

## 8.3 Home Page Does Not Show Posts

1. Verify `params.mainSections` in `hugo.yaml` matches the section directory names under the configured language `contentDir` (`content/ko/`).
2. Confirm posts are not drafts/future-dated.
3. Confirm section index files and content paths are valid.

## 8.4 GitHub Action Authentication

### Symptom: read works but write fails

Public repositories allow anonymous reads. A successful GET does not prove that the PAT used for writes is valid.

**Solution**: Verify token status in GitHub Settings → Fine-grained tokens. Reissue if needed and update the Authentication value in the GPT builder. Token issuance and rotation conventions are defined in `docs/master/system-operation.md` section *C-1 (GPT Action 토큰 관리 규약)*.

### Symptom: 409 Conflict / non-fast-forward

**Cause**: `main` changed after the coach read the starting commit/tree, so the attempted ref update is no longer a fast-forward.

**Solution**: Re-fetch latest `main` and its tree, reconstruct the intended minimal changes, create a new tree/commit, and retry the `main` update with `force:false`. The repository write convention (latest main/tree → modify → create tree/commit → update main with `force:false` → verify raw/tree) is defined in `docs/master/system-operation.md` section *C-1 (GPT Action 토큰 관리 규약)*.

## 8.5 Confirmation Modal Does Not Appear

**Solution**: Verify `x-openai-isConsequential: true` on the repository write operations in the coach schema, then re-save. The confirmation gate convention is defined in `docs/master/system-operation.md` section *PartB-5 (저장소 쓰기 확인 게이트)*.

## 8.6 Structured Data Format Mismatch

### Symptom: Coach halts a write because a new record does not match the existing data structure

1. Inspect the current `/data/{activity}.json` structure and the activity-specific convention.
2. Compare the attempted record with the existing field structure and value conventions.
3. Correct the new data rather than silently changing the established structure. If the structure itself must change, update the operating documents and dependent rendering logic together.

The repository currently does not maintain a separate `/schemas/` directory. The structured-data convention is defined in `docs/master/system-operation.md` section *C-2-2-2*.

---

# Part 9: External Services

## 9.1 Google Search Console

- Verify ownership through the deployed site.
- Submit sitemap when needed.
- Monitor indexing and coverage.

## 9.2 Google Analytics

The current measurement ID is configured in `hugo.yaml`.

## 9.3 Useful References

| Resource | URL |
|----------|-----|
| Hugo | https://gohugo.io/ |
| PaperMod | https://github.com/adityatelange/hugo-PaperMod |
| Git Database API | https://docs.github.com/en/rest/git |
| GitHub Pages | https://docs.github.com/en/pages |
| Google Search Console | https://search.google.com/search-console |

---

# Part 10: Operation Checklist

## Before Publishing

- [ ] Correct English-only repository path
- [ ] Six base Front Matter fields present
- [ ] `draft: false` for final public content
- [ ] Conditional fields used only when required
- [ ] Internal links use public URLs, not source paths
- [ ] No accidental `/ko/` prefix in public links
- [ ] Referenced static assets exist
- [ ] Required legacy aliases preserved
- [ ] No unrelated body text rewritten

## After Publishing

- [ ] `main` points to the intended commit
- [ ] Raw/tree state matches intended changes
- [ ] GitHub Actions deployment succeeded
- [ ] Public URL reflects the latest content
- [ ] Legacy aliases resolve correctly when applicable

---

# Appendix A: Hugo Site.Data + Client JS Pattern

Hugo's `jsonify` output can be embedded as a JSON string in client-side JavaScript. If the value is a string, array methods such as `.filter()` fail.

Use:

```javascript
const data = JSON.parse({{ site.Data.x | jsonify }});
```

Do not call array methods on the unparsed string.

# Appendix B: Raw GitHub Cache

`raw.githubusercontent.com` may lag immediately after a commit. For fresh verification, prefer GitHub API raw/blob retrieval or the repository blob view.

# Appendix C: Historical Korean Base64 Issue

The retired Contents API + Base64 PUT flow occasionally produced Korean text corruption. The current Git Data API flow writes UTF-8 text through tree-entry `content` and avoids that encoding path.

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
