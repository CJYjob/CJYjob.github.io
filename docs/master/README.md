# Master Documents

This directory is the canonical source of truth (SSOT) for coach/system master documents used with the `CJYjob.github.io` repository.

## Canonical files

- `system-operation.md` — self-management system philosophy, coach operating model, asset workflow, repository write rules.
- `blog-operations.md` — Hugo/GitHub Pages technical setup and current blog operation guide.
- `security-five-year-plan.md` — information-security consultant five-year growth plan.

## Operating rule

Custom GPTs and coaches must read the latest `main` version of the relevant master document before repository or system-governance work. Uploaded or local copies are reference snapshots only and must not override the latest GitHub SSOT.

Repository writes use the GitHub Git Database API flow defined in `system-operation.md`. Blog content lives under `content/ko/`; this `docs/master/` directory is operational documentation and is not Hugo content.

## Current integration status

`system-operation.md` and `blog-operations.md` contain the current operating rules directly; this README is an index and must not override them.

Source-preserving master-document patches are implemented by `scripts/apply_exact_patch.py` and `.github/workflows/apply-doc-patch.yaml`. The automation coach Custom GPT Action exposes the fixed workflow dispatch and run lookup operations, and the mechanism has been verified with real master-document patches using blob-SHA checks, exact one-time replacements, diff limits, and post-commit raw/tree verification.

`docs/action-schemas/automation-coach-doc-patch.openapi.yaml` is reference-only and may be removed once the Builder configuration is considered stable. Other coaches should be instantiated from their existing Instructions plus the current `system-operation.md` role definitions rather than duplicating the full SSOT into each Custom GPT.

## Archive

`docs/master/_archive/` stores source documents exactly as originally supplied for restoration and comparison. Archive files are reference-only and are not SSOT. To preserve original identity, filenames inside `_archive/` may retain their original language and naming; this is an explicit exception to the normal English-path convention.

Outside `_archive/`, path names under `docs/master/` use English only. Document bodies may remain Korean.
