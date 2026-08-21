# Junyoung's Growth — Blog Setup and Operation Complete Guide

## Document Information

| Item | Content |
|------|---------|
| Document Version | 2.3 |
| Last Updated | August 2026 |
| Purpose | Blog setup process documentation and operation guide |
| Audience | Blog owner and Claude/ChatGPT AI |

This manual covers *blog technical operations only*. The persona, asset workflow, and coach operation conventions of the *self-management support system* — which uses this blog as its operating ground — are defined in `docs/master/system-operation.md`.

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

The menu structure separates assets by *completeness*: *incomplete → log*, *complete → portfolio*. Detailed asset classification principles are defined in `docs/master/system-operation.md`.

## 1.3 Technology Stack Summary

```text
User Browser
    ↑ HTTPS
GitHub Pages
    ↑ GitHub Actions
Hugo build
    ↑
Repository (`content/ko`, data, layouts, static, scripts)
```

## 1.4 Version Information

### Core Tools

| Tool | Version | Purpose | Notes |
|------|---------|---------|-------|
| Hugo | 0.152.2 Extended | Static site generator | Extended version required |
| PaperMod | Git Submodule | Hugo theme | Managed under `themes/PaperMod` |
| Git | Current | Version control | Used by GitHub and local tooling |

### External Services

| Service | Purpose | Status |
|---------|---------|--------|
| GitHub Pages | Static hosting | Active |
| Google Search Console | SEO/search registration | Registered |
| Google Analytics | Visitor analytics | Connected |

---

# Part 2: Current Hugo Configuration

## 2.1 Content Root

The repository uses multilingual Hugo configuration with Korean as the default language.

```yaml
defaultContentLanguage: ko
defaultContentLanguageInSubdir: false
languages:
  ko:
    contentDir: content/ko
```

Therefore source files live under `content/ko/`, but public URLs do **not** use a `/ko/` prefix.

Correct public URL examples:

- `/log/`
- `/portfolio/`
- `/series/investment-strategy/`
- `/categories/investment/`

Incorrect hard-coded URL examples:

- `/ko/log/`
- `/ko/portfolio/...`
- `/content/ko/...`

## 2.2 Current Directory Structure

```text
CJYjob.github.io/
├── .github/
│   └── workflows/
│       └── hugo.yaml
├── archetypes/
│   ├── default.md
│   ├── log.md
│   └── portfolio.md
├── content/
│   └── ko/
│       ├── about/
│       │   └── index.md
│       ├── categories/
│       │   ├── english/_index.md
│       │   └── investment/_index.md
│       ├── log/
│       ├── portfolio/
│       ├── series/
│       └── search.md
├── data/
├── docs/
│   └── master/
├── layouts/
├── scripts/
├── static/
├── themes/
│   └── PaperMod/
└── hugo.yaml
```

The legacy `content/log`, `content/portfolio`, `content/about`, and `content/search.md` structure was removed after migration verification. Do not recreate it.

## 2.3 Menu and Main Sections

Current primary sections are `log` and `portfolio`. About and Search are meta pages.

## 2.4 Front Matter

Base fields:

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

Conditional fields are allowed only when their Hugo function is actually needed:

- `aliases` — legacy URL preservation or URL migration
- `series` — series taxonomy membership
- `weight` — explicit series/list ordering
- `ShowToc` — post-level TOC override
- `TocOpen` — post-level TOC-open override

These conditional fields are not injected by default archetypes.

## 2.5 Archetypes

`archetypes/default.md`, `archetypes/log.md`, and `archetypes/portfolio.md` generate the six base Front Matter fields only. Log/Portfolio classification is determined by file location, not by automatically writing `Log` or `PortFolio` into `categories`.

---

# Part 3: GitHub Repository Operations

## 3.1 Write Method

Coach-driven writes use the **GitHub Git Database API**. The previous GitHub Contents API + Base64 PUT flow is retired.

Standard flow:

1. Read latest `main` commit SHA.
2. Read that commit's tree SHA.
3. Read the current raw UTF-8 content for every file being modified.
4. Apply only the requested changes.
5. `createGitTree` using the current tree SHA as `base_tree`.
6. `createGitCommit` using the new tree SHA and the original latest commit SHA as the parent.
7. `updateMainReference` with the new commit SHA and `force:false`.
8. Re-read `main`, raw files, and/or the recursive tree to verify the final state.

Do not confuse commit SHA, tree SHA, and blob SHA.

## 3.2 Confirmation Gate

The ChatGPT platform consequential Action confirmation modal is the only user-approval gate for repository writes.

- Do not require a separate chat message such as "승인" or "진행".
- Do not require a chat commit preview.
- Group changes into one atomic Git tree/commit when practical.
- Stop further writes when an API stage fails and report the actual stage/status.

## 3.3 Raw Verification

After a commit, verify actual raw UTF-8 content or tree state. A successful tree creation or commit creation alone is not proof that the intended state is live on `main`.

---

# Part 4: Content Operations

## 4.1 Asset Classification

- Incomplete/in-progress material → `content/ko/log/`
- Completed/public artifact → `content/ko/portfolio/`
- Category hubs → `content/ko/categories/`
- Series hubs → `content/ko/series/`

## 4.2 Path Naming

Repository paths use English only. If Korean material must be represented in a path, use an English translation or romanized reading.

## 4.3 Internal Links

Markdown internal links use public site URLs, not source paths.

Correct:

```text
/portfolio/...
/log/...
/series/...
/categories/...
```

Incorrect:

```text
/ko/portfolio/...
/content/ko/portfolio/...
```

## 4.4 Legacy URLs

Use Front Matter `aliases` to preserve old public URLs after content moves. Hugo may render aliases as static HTML containing `canonical` and `meta refresh` rather than an HTTP 301/302 response. Therefore legacy verification must inspect the alias HTML or browser final behavior, not only the HTTP status code.

## 4.5 Static Assets

Files under `static/` are exposed from the site root. Example:

```text
static/business-cycle.svg → /business-cycle.svg
```

Do not leave required assets inside deleted legacy content trees.

---

# Part 5: Workout Automation

The current workout automation uses these paths:

- `content/ko/portfolio/workout.md`
- `data/workout.json`
- `data/workout_mapping.json`
- `scripts/merge_workout_pending.py`
- `.github/workflows/hugo.yaml`

Do not restore dependencies on legacy `content/portfolio/...` paths.

---

# Part 6: Hugo Technical Notes

## 6.1 Site.Data + Client JavaScript

When Hugo's `jsonify` result is embedded as a JavaScript string, parse it before calling array methods.

```javascript
const data = JSON.parse({{ site.Data.x | jsonify }});
```

Calling `.filter`, `.map`, etc. on an unparsed JSON string causes runtime errors.

## 6.2 Raw HTML

Custom HTML/JS in Markdown requires:

```yaml
markup:
  goldmark:
    renderer:
      unsafe: true
```

## 6.3 Shortcode Escape

Distinguish between shortcode syntax displayed as documentation and shortcode syntax intended to execute. Do not leave escaped documentation syntax in content that should render an actual shortcode.

## 6.4 Raw GitHub Cache

`raw.githubusercontent.com` may lag immediately after a commit. Verify fresh content through GitHub raw/blob APIs when necessary.

## 6.5 Korean/Base64 Historical Issue

Intermittent Korean text corruption was observed in the retired Base64 Contents API flow. Current Git Data API writes send UTF-8 text through the tree entry `content` field and do not use Base64.

---

# Part 7: Deployment Verification

Repository verification and public-site verification are separate gates.

## 7.1 Repository Verification

Confirm:

1. `main` points to the new commit.
2. expected files exist or deleted files are absent.
3. raw content matches the intended content.
4. unrelated files were not modified.

## 7.2 Public-Site Verification

Confirm, when applicable:

1. core pages return successfully (`/`, `/log/`, `/portfolio/`, `/about/`, `/search/`).
2. the latest expected HTML is actually deployed.
3. legacy aliases resolve to the intended canonical/meta-refresh destination.
4. static assets load from their final URLs.

Do not declare public deployment complete based only on repository state or another person's browser report. If the verification path is cached, use a cache-busting query, an independent browser/network request, or curl.

---

# Part 8: Publishing Checklist

Before commit:

- English path names
- six base Front Matter fields
- `draft: false` for final public posts
- conditional fields only when required
- no obsolete `/ko/` hard-coded links
- required aliases preserved
- referenced static assets exist
- no unnecessary body rewrites

After commit:

- latest `main` verified
- raw/tree verified
- deployment checked
- public URL checked
- legacy alias checked when relevant

---

# Part 9: Search and Analytics

- GitHub Pages hosts the generated site.
- GitHub Actions builds and deploys Hugo.
- Google Search Console manages indexing/search visibility.
- Google Analytics provides visitor analytics.
- The home search index is generated through Hugo's JSON output and PaperMod search configuration.

---

# Part 10: SSOT Rule

The GitHub `main` copies under `docs/master/` are the canonical operating references.

- `docs/master/system-operation.md`
- `docs/master/blog-operations.md`
- `docs/master/security-five-year-plan.md`

Uploaded/local copies are snapshots only. Before repository or governance work, coaches should read the relevant `main` document and use it over stale local context.
