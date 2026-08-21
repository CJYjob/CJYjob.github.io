# Master Documents

This directory is the canonical source of truth (SSOT) for coach/system master documents used with the `CJYjob.github.io` repository.

## Canonical files

- `system-operation.md` — self-management system philosophy, coach operating model, asset workflow, repository write rules.
- `blog-operations.md` — Hugo/GitHub Pages technical setup and current blog operation guide.
- `security-five-year-plan.md` — information-security consultant five-year growth plan.

## Operating rule

Custom GPTs and coaches must read the latest `main` version of the relevant master document before repository or system-governance work. Uploaded or local copies are reference snapshots only and must not override the latest GitHub SSOT.

Repository writes use the GitHub Git Database API flow defined in `system-operation.md`. Blog content lives under `content/ko/`; this `docs/master/` directory is operational documentation and is not Hugo content.

## Cross-document consistency rules

The following rules reflect the current repository implementation and resolve older wording that may remain in the larger master documents:

- The six-field Front Matter standard (`title`, `date`, `draft`, `description`, `categories`, `tags`) applies to ordinary Log/Portfolio asset pages. Functional/meta pages and hubs — such as `search.md`, section `_index.md` files, category hubs, and series hubs — may use only the Front Matter required by their Hugo function and page role.
- New ordinary posts are public by default. `archetypes/default.md`, `archetypes/log.md`, and `archetypes/portfolio.md` currently generate `draft: false`. Use `draft: true` only when a page is intentionally unpublished.
- Direct GitHub Actions build-status inspection belongs to the automation coach, which holds Actions Read permission. Other coaches may verify repository state and public-page state within their own permissions, but should not assume Actions access they do not have.
- `content/ko/` is the only current Hugo content root. Historical top-level `content/log`, `content/portfolio`, `content/about`, and similar legacy trees must not be recreated.
- Public URLs do not include `/ko/`. Internal Markdown links use public URLs rather than repository source paths.

When a statement in `system-operation.md` or `blog-operations.md` conflicts with one of the implementation facts above, use this section as the current reconciliation rule until the older wording is directly revised in that source document.

## Pending Custom GPT integration

The repository already contains `scripts/apply_exact_patch.py` and `.github/workflows/apply-doc-patch.yaml` for source-preserving exact replacements in `docs/master/`. A reference Action schema is stored at `docs/action-schemas/automation-coach-doc-patch.openapi.yaml`.

When Custom GPT Action editing is available on PC, resume from this point:

1. Add the fixed document-patch workflow dispatch and workflow-run lookup operations to the automation coach Action schema.
2. Configure the automation-coach GitHub credential with the minimum Actions Read/Write access required for this workflow.
3. Test one small master-document replacement using the current blob SHA, one exact old/new replacement, and a small `max_changed_lines` limit.
4. Verify workflow success, resulting Git diff, latest `main`, and raw content before using the mechanism on the remaining stale statements in `system-operation.md` and `blog-operations.md`.
5. After those master documents are directly reconciled, remove or reduce the temporary cross-document reconciliation rules above if they are no longer needed.

The reference Action-schema file is optional infrastructure and may be removed after the Custom GPT schema is updated; the patch script and workflow are the reusable repository-side implementation.

## Archive

`docs/master/_archive/` stores source documents exactly as originally supplied for restoration and comparison. Archive files are reference-only and are not SSOT. To preserve original identity, filenames inside `_archive/` may retain their original language and naming; this is an explicit exception to the normal English-path convention.

Outside `_archive/`, path names under `docs/master/` use English only. Document bodies may remain Korean.
