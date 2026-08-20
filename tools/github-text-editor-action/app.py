import base64
import os
from io import StringIO
from typing import Any, Literal

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field
from ruamel.yaml import YAML

app = FastAPI(
    title="GitHub Text File Editor Action",
    version="1.0.0",
    description="Safe UTF-8 text-file editing facade over the GitHub Contents API.",
)

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
ACTION_API_KEY = os.environ.get("ACTION_API_KEY", "")
ALLOWED_REPOS = {x.strip() for x in os.environ.get("ALLOWED_REPOS", "").split(",") if x.strip()}

yaml = YAML()
yaml.preserve_quotes = True
yaml.width = 4096

class Replacement(BaseModel):
    old: str = Field(min_length=1)
    new: str
    expected_occurrences: int = Field(default=1, ge=0)

class FileTarget(BaseModel):
    owner: str
    repo: str
    branch: str = "main"

class CreateRequest(FileTarget):
    path: str
    content_utf8: str
    commit_message: str

class UpdateRequest(FileTarget):
    path: str
    expected_sha: str
    commit_message: str
    front_matter_patch: dict[str, Any] = Field(default_factory=dict)
    remove_front_matter_keys: list[str] = Field(default_factory=list)
    replacements: list[Replacement] = Field(default_factory=list)

class MoveRequest(FileTarget):
    source_path: str
    destination_path: str
    expected_source_sha: str
    commit_message: str
    front_matter_patch: dict[str, Any] = Field(default_factory=dict)
    remove_front_matter_keys: list[str] = Field(default_factory=list)
    replacements: list[Replacement] = Field(default_factory=list)
    delete_source: bool = False
    delete_commit_message: str | None = None

class DeleteRequest(FileTarget):
    path: str
    expected_sha: str
    commit_message: str

def require_action_key(x_action_key: str | None = Header(default=None)) -> None:
    if not ACTION_API_KEY:
        raise HTTPException(500, "ACTION_API_KEY is not configured")
    if x_action_key != ACTION_API_KEY:
        raise HTTPException(401, "Invalid action API key")

def ensure_repo_allowed(owner: str, repo: str) -> None:
    full = f"{owner}/{repo}"
    if ALLOWED_REPOS and full not in ALLOWED_REPOS:
        raise HTTPException(403, f"Repository not allowed: {full}")

def github_headers() -> dict[str, str]:
    if not GITHUB_TOKEN:
        raise HTTPException(500, "GITHUB_TOKEN is not configured")
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "github-text-editor-action/1.0",
    }

async def github_request(method: Literal["GET", "PUT", "DELETE"], url: str, *, params=None, json=None) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.request(method, url, headers=github_headers(), params=params, json=json)
    if response.status_code >= 400:
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise HTTPException(response.status_code, detail)
    return response.json() if response.content else {}

def contents_url(owner: str, repo: str, path: str) -> str:
    path = path.lstrip("/")
    return f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"

async def read_file(owner: str, repo: str, path: str, ref: str) -> dict[str, Any]:
    ensure_repo_allowed(owner, repo)
    data = await github_request("GET", contents_url(owner, repo, path), params={"ref": ref})
    if data.get("type") != "file":
        raise HTTPException(400, "Path is not a file")
    if data.get("encoding") != "base64":
        raise HTTPException(502, "GitHub did not return base64 file content")
    try:
        raw = base64.b64decode(data["content"], validate=False)
        text = raw.decode("utf-8")
    except Exception as exc:
        raise HTTPException(415, f"File is not valid UTF-8 text: {exc}") from exc
    return {"path": data["path"], "sha": data["sha"], "size": data["size"], "content_utf8": text, "html_url": data.get("html_url")}

def split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        raise HTTPException(422, "Opening YAML front matter has no closing delimiter")
    front_text = text[4:end]
    body = text[end + 5:]
    data = yaml.load(front_text) or {}
    if not isinstance(data, dict):
        raise HTTPException(422, "Front matter must be a YAML mapping")
    return data, body

def join_front_matter(front: dict[str, Any], body: str) -> str:
    if not front:
        return body
    buf = StringIO()
    yaml.dump(front, buf)
    return f"---\n{buf.getvalue()}---\n{body}"

def apply_edit(text: str, front_matter_patch: dict[str, Any], remove_front_matter_keys: list[str], replacements: list[Replacement]) -> str:
    edited = text
    if front_matter_patch or remove_front_matter_keys:
        front, body = split_front_matter(edited)
        for key in remove_front_matter_keys:
            front.pop(key, None)
        for key, value in front_matter_patch.items():
            front[key] = value
        edited = join_front_matter(front, body)
    for item in replacements:
        actual = edited.count(item.old)
        if actual != item.expected_occurrences:
            raise HTTPException(409, {"message": "Replacement occurrence count mismatch", "old": item.old, "expected_occurrences": item.expected_occurrences, "actual_occurrences": actual})
        if actual:
            edited = edited.replace(item.old, item.new)
    return edited

async def put_file(owner: str, repo: str, path: str, branch: str, commit_message: str, content_utf8: str, sha: str | None = None) -> dict[str, Any]:
    ensure_repo_allowed(owner, repo)
    payload = {"message": commit_message, "content": base64.b64encode(content_utf8.encode("utf-8")).decode("ascii"), "branch": branch}
    if sha:
        payload["sha"] = sha
    return await github_request("PUT", contents_url(owner, repo, path), json=payload)

async def delete_file(owner: str, repo: str, path: str, branch: str, commit_message: str, sha: str) -> dict[str, Any]:
    ensure_repo_allowed(owner, repo)
    return await github_request("DELETE", contents_url(owner, repo, path), json={"message": commit_message, "sha": sha, "branch": branch})

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/v1/files/read", dependencies=[Depends(require_action_key)])
async def read_text_file(owner: str = Query(...), repo: str = Query(...), path: str = Query(...), ref: str = Query("main")):
    return await read_file(owner, repo, path, ref)

@app.post("/v1/files/create", dependencies=[Depends(require_action_key)])
async def create_text_file(req: CreateRequest):
    result = await put_file(req.owner, req.repo, req.path, req.branch, req.commit_message, req.content_utf8)
    created = await read_file(req.owner, req.repo, req.path, req.branch)
    return {"status": "created", "commit_sha": result.get("commit", {}).get("sha"), "file": created}

@app.post("/v1/files/update", dependencies=[Depends(require_action_key)])
async def update_text_file(req: UpdateRequest):
    current = await read_file(req.owner, req.repo, req.path, req.branch)
    if current["sha"] != req.expected_sha:
        raise HTTPException(409, {"message": "SHA mismatch", "expected_sha": req.expected_sha, "actual_sha": current["sha"]})
    edited = apply_edit(current["content_utf8"], req.front_matter_patch, req.remove_front_matter_keys, req.replacements)
    if edited == current["content_utf8"]:
        return {"status": "unchanged", "commit_sha": None, "file": current}
    result = await put_file(req.owner, req.repo, req.path, req.branch, req.commit_message, edited, sha=current["sha"])
    updated = await read_file(req.owner, req.repo, req.path, req.branch)
    return {"status": "updated", "commit_sha": result.get("commit", {}).get("sha"), "file": updated}

@app.post("/v1/files/move", dependencies=[Depends(require_action_key)])
async def move_text_file(req: MoveRequest):
    current = await read_file(req.owner, req.repo, req.source_path, req.branch)
    if current["sha"] != req.expected_source_sha:
        raise HTTPException(409, {"message": "SHA mismatch", "expected_sha": req.expected_source_sha, "actual_sha": current["sha"]})
    edited = apply_edit(current["content_utf8"], req.front_matter_patch, req.remove_front_matter_keys, req.replacements)
    create_result = await put_file(req.owner, req.repo, req.destination_path, req.branch, req.commit_message, edited)
    destination = await read_file(req.owner, req.repo, req.destination_path, req.branch)
    delete_result = None
    if req.delete_source:
        delete_result = await delete_file(req.owner, req.repo, req.source_path, req.branch, req.delete_commit_message or f"Delete moved file: {req.source_path}", current["sha"])
    return {
        "status": "moved" if req.delete_source else "copied_and_edited",
        "create_commit_sha": create_result.get("commit", {}).get("sha"),
        "delete_commit_sha": delete_result.get("commit", {}).get("sha") if delete_result else None,
        "source_sha": current["sha"],
        "destination": destination,
    }

@app.post("/v1/files/delete", dependencies=[Depends(require_action_key)])
async def delete_text_file(req: DeleteRequest):
    current = await read_file(req.owner, req.repo, req.path, req.branch)
    if current["sha"] != req.expected_sha:
        raise HTTPException(409, {"message": "SHA mismatch", "expected_sha": req.expected_sha, "actual_sha": current["sha"]})
    result = await delete_file(req.owner, req.repo, req.path, req.branch, req.commit_message, current["sha"])
    return {"status": "deleted", "commit_sha": result.get("commit", {}).get("sha"), "deleted_sha": current["sha"]}
