# GitHub Text File Editor Action

Reusable GPT Action backend for safely editing long UTF-8 text files in GitHub.

## Core design

GPT may read the text and decide what needs changing, but it never needs to transport
the full file as Base64. The backend fetches the current GitHub file, verifies its SHA,
applies front matter patches and exact replacements, Base64-encodes the resulting UTF-8
bytes, writes through the GitHub Contents API, and re-reads the file for verification.

## Endpoints

- `GET /v1/files/read`
- `POST /v1/files/create`
- `POST /v1/files/update`
- `POST /v1/files/move`
- `POST /v1/files/delete`

`move` defaults to `delete_source=false`.

## Safety

- `ALLOWED_REPOS` repository allowlist
- `X-Action-Key` endpoint authentication
- `expected_sha` optimistic concurrency check
- exact replacement count validation
- write-then-read verification
- GitHub token remains server-side

## Environment

```text
GITHUB_TOKEN=github_pat_...
ACTION_API_KEY=a-long-random-secret
ALLOWED_REPOS=CJYjob/CJYjob.github.io
PORT=8000
```

## Run

```bash
docker build -t github-text-editor-action .
docker run --rm -p 8000:8000 \
  -e GITHUB_TOKEN=... \
  -e ACTION_API_KEY=... \
  -e ALLOWED_REPOS=CJYjob/CJYjob.github.io \
  github-text-editor-action
```

Deploy to an HTTPS endpoint, replace the placeholder server URL in `openapi.yaml`,
then import/paste the schema into the GPT Actions editor. Configure API-key auth using
header `X-Action-Key`.

Recommended update flow:

1. `readTextFile`
2. GPT decides only the smallest required changes.
3. `updateTextFile` with `expected_sha`, `front_matter_patch`, and/or `replacements`.
4. Treat the operation as successful only when the endpoint returns the commit SHA and
   the re-read file metadata.

For path changes, use `moveTextFile`; the service fetches the source body itself.
