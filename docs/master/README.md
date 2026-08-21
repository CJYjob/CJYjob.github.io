# Master Documents

This directory is the canonical source of truth (SSOT) for coach/system master documents used with the `CJYjob.github.io` repository.

## Canonical files

- `system-operation.md` — self-management system philosophy, coach operating model, asset workflow, repository write rules.
- `blog-operations.md` — Hugo/GitHub Pages technical setup and current blog operation guide.
- `security-five-year-plan.md` — information-security consultant five-year growth plan.

## Operating rule

Custom GPTs and coaches must read the latest `main` version of the relevant master document before repository or system-governance work. Uploaded or local copies are reference snapshots only and must not override the latest GitHub SSOT.

Repository writes use the GitHub Git Database API flow defined in `system-operation.md`. Blog content lives under `content/ko/`; this `docs/master/` directory is operational documentation and is not Hugo content.

Path names under this directory use English only. Document bodies may remain Korean.
