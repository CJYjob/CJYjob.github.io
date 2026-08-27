#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

USER_AGENT = "cjyjob-daily-job-briefing/1.0"
OPENAI_URL = "https://api.openai.com/v1/responses"
CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
HACKERONE_URL = "https://api.hackerone.com/v1/hackers/hacktivity"
ARXIV_URL = "https://export.arxiv.org/api/query"

SECURITY_TERMS = {
    "critical": 5, "remote code execution": 10, "rce": 8, "authentication bypass": 10,
    "authorization": 7, "privilege escalation": 7, "ssrf": 9, "request smuggling": 10,
    "desync": 10, "xss": 6, "sql injection": 8, "sqli": 8, "path traversal": 7,
    "directory traversal": 7, "command injection": 9, "template injection": 9,
    "prototype pollution": 8, "csrf": 5, "idor": 8, "access control": 8,
    "oauth": 7, "saml": 7, "jwt": 6, "api": 4, "web": 3, "browser": 4,
    "zero-day": 10, "0-day": 10, "actively exploited": 10, "exploit": 6,
}
AI_TERMS = {
    "security": 8, "vulnerability": 9, "exploit": 8, "cybersecurity": 8,
    "agent": 8, "agentic": 8, "tool use": 7, "rag": 7, "retrieval augmented": 7,
    "code generation": 7, "coding": 5, "software engineering": 6, "developer": 4,
    "automation": 8, "workflow": 5, "reasoning": 5, "browser": 5, "web agent": 8,
    "static analysis": 8, "dynamic analysis": 8, "program analysis": 8,
    "fuzz": 8, "pentest": 9, "penetration test": 9,
}
LOW_VALUE_TERMS = {
    "earnings": 10, "bounty payout": 10, "made $": 10, "income proof": 12,
    "motivation": 4, "giveaway": 10, "sponsored": 6,
}


@dataclass
class Candidate:
    candidate_id: str
    category: str
    source: str
    title: str
    url: str
    published_at: str
    text: str
    rule_score: int
    metadata: dict[str, Any]


def now_kst() -> datetime:
    return datetime.now(ZoneInfo("Asia/Seoul"))


def iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    value = re.sub(r"<[^>]+>", " ", html.unescape(value))
    return re.sub(r"\s+", " ", value).strip()


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        pass
    try:
        dt = parsedate_to_datetime(value)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def http_get(url: str, headers: dict[str, str] | None = None, timeout: int = 30) -> bytes:
    merged = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if headers:
        merged.update(headers)
    req = urllib.request.Request(url, headers=merged)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def http_json(url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
    return json.loads(http_get(url, headers=headers).decode("utf-8"))


def within_window(value: str | None, cutoff: datetime) -> bool:
    dt = parse_date(value)
    return bool(dt and dt >= cutoff)


def score_terms(text: str, terms: dict[str, int], cap: int) -> int:
    t = text.lower()
    return min(cap, sum(weight for term, weight in terms.items() if term in t))


def stable_id(prefix: str, source: str, url: str, title: str) -> str:
    digest = hashlib.sha1(f"{source}|{url}|{title}".encode("utf-8")).hexdigest()[:8].upper()
    return f"{prefix}-{digest}"


def source_prefix(category: str) -> str:
    return {"security_news": "SEC", "bug_bounty": "BUG", "ai_research": "AI"}[category]


def add_candidate(items: list[Candidate], category: str, source: str, title: str, url: str,
                  published_at: str, text: str, score: int, metadata: dict[str, Any]) -> None:
    title = clean_text(title)
    text = clean_text(text)
    if not title or not url:
        return
    items.append(Candidate(
        candidate_id=stable_id(source_prefix(category), source, url, title),
        category=category,
        source=source,
        title=title[:300],
        url=url,
        published_at=published_at,
        text=text[:6000],
        rule_score=max(0, min(100, int(score))),
        metadata=metadata,
    ))


def collect_cisa(cutoff: datetime) -> list[Candidate]:
    out: list[Candidate] = []
    data = http_json(CISA_KEV_URL)
    for v in data.get("vulnerabilities", []):
        date_added = v.get("dateAdded")
        try:
            dt = datetime.strptime(date_added, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            continue
        if dt < cutoff:
            continue
        title = f"{v.get('cveID', '')} — {v.get('vulnerabilityName', '')}".strip(" —")
        body = " ".join(filter(None, [v.get("shortDescription"), v.get("requiredAction"), v.get("notes"), v.get("vendorProject"), v.get("product")]))
        score = 65 + score_terms(f"{title} {body}", SECURITY_TERMS, 25)
        cve = v.get("cveID")
        url = f"https://nvd.nist.gov/vuln/detail/{cve}" if cve else CISA_KEV_URL
        add_candidate(out, "security_news", "CISA KEV", title, url, dt.isoformat(), body, score, {"known_exploited": True, "cve": [cve] if cve else [], "vendor": v.get("vendorProject")})
    return out


def extract_cvss(cve: dict[str, Any]) -> float | None:
    metrics = cve.get("metrics", {})
    for key in ("cvssMetricV40", "cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        rows = metrics.get(key) or []
        if rows:
            score = rows[0].get("cvssData", {}).get("baseScore")
            if isinstance(score, (int, float)):
                return float(score)
    return None


def collect_nvd(cutoff: datetime, now: datetime) -> list[Candidate]:
    out: list[Candidate] = []
    params = {"lastModStartDate": iso_utc(cutoff), "lastModEndDate": iso_utc(now), "resultsPerPage": "200"}
    headers = {"Accept": "application/json"}
    if os.getenv("NVD_API_KEY"):
        headers["apiKey"] = os.environ["NVD_API_KEY"]
    data = http_json(NVD_URL + "?" + urllib.parse.urlencode(params), headers=headers)
    for row in data.get("vulnerabilities", []):
        cve = row.get("cve", {})
        cve_id = cve.get("id", "")
        descriptions = cve.get("descriptions") or []
        desc = next((d.get("value", "") for d in descriptions if d.get("lang") == "en"), "")
        published = cve.get("published") or cve.get("lastModified") or ""
        cvss = extract_cvss(cve)
        score = 20 + score_terms(f"{cve_id} {desc}", SECURITY_TERMS, 30)
        if cvss is not None:
            score += 25 if cvss >= 9 else 18 if cvss >= 7 else 8 if cvss >= 4 else 0
        add_candidate(out, "security_news", "NVD", cve_id or "NVD vulnerability", f"https://nvd.nist.gov/vuln/detail/{cve_id}", published, desc, score, {"known_exploited": False, "cve": [cve_id] if cve_id else [], "cvss": cvss})
    return out


def rss_items(xml_bytes: bytes) -> Iterable[dict[str, str]]:
    root = ET.fromstring(xml_bytes)
    channel = root.find("channel")
    if channel is not None:
        for item in channel.findall("item"):
            yield {"title": clean_text(item.findtext("title")), "link": clean_text(item.findtext("link")), "date": clean_text(item.findtext("pubDate") or item.findtext("date")), "summary": clean_text(item.findtext("description") or item.findtext("content"))}
        return
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall("atom:entry", ns):
        link = ""
        for el in entry.findall("atom:link", ns):
            if el.attrib.get("rel", "alternate") == "alternate":
                link = el.attrib.get("href", "")
                break
        yield {"title": clean_text(entry.findtext("atom:title", default="", namespaces=ns)), "link": link, "date": clean_text(entry.findtext("atom:published", default="", namespaces=ns) or entry.findtext("atom:updated", default="", namespaces=ns)), "summary": clean_text(entry.findtext("atom:summary", default="", namespaces=ns) or entry.findtext("atom:content", default="", namespaces=ns))}


def collect_rss(feed: dict[str, Any], cutoff: datetime) -> list[Candidate]:
    out: list[Candidate] = []
    category = feed["category"]
    xml = http_get(feed["url"])
    for item in rss_items(xml):
        dt = parse_date(item["date"])
        if dt is None or dt < cutoff:
            continue
        text = f"{item['title']} {item['summary']}"
        relevance = score_terms(text, SECURITY_TERMS if category != "ai_research" else AI_TERMS, 35)
        penalty = score_terms(text, LOW_VALUE_TERMS, 25)
        score = 20 + int(feed.get("trust", 10)) + relevance - penalty
        add_candidate(out, category, feed["name"], item["title"], item["link"], dt.isoformat(), item["summary"], score, {"feed_url": feed["url"]})
    return out


def collect_hackerone(cutoff: datetime) -> list[Candidate]:
    username = os.getenv("HACKERONE_USERNAME")
    token = os.getenv("HACKERONE_API_TOKEN")
    if not username or not token:
        return []
    query = f"disclosed:true AND disclosed_at:>={cutoff.date().isoformat()}"
    params = urllib.parse.urlencode({"queryString": query, "sort": "-disclosed_at", "page[size]": "100"})
    import base64
    basic = base64.b64encode(f"{username}:{token}".encode()).decode()
    data = http_json(HACKERONE_URL + "?" + params, headers={"Accept": "application/json", "Authorization": f"Basic {basic}"})
    out: list[Candidate] = []
    for row in data.get("data", []):
        a = row.get("attributes", {})
        disclosed = a.get("disclosed_at") or a.get("latest_disclosable_activity_at") or ""
        if not within_window(disclosed, cutoff):
            continue
        rel = row.get("relationships", {})
        summary = rel.get("report_generated_content", {}).get("data", {}).get("attributes", {}).get("hacktivity_summary", "")
        severity = (a.get("severity_rating") or "").lower()
        score = 35 + score_terms(f"{a.get('title','')} {summary} {a.get('cwe') or ''}", SECURITY_TERMS, 30) + {"critical": 20, "high": 15, "medium": 8, "low": 2}.get(severity, 0)
        add_candidate(out, "bug_bounty", "HackerOne Hacktivity", a.get("title", "HackerOne disclosure"), a.get("url") or f"https://hackerone.com/reports/{row.get('id')}", disclosed, summary, score, {"severity": severity or None, "cwe": a.get("cwe") or None, "cve": a.get("cve_ids") or []})
    return out


def collect_arxiv(cutoff: datetime, config: dict[str, Any]) -> list[Candidate]:
    query = " OR ".join(f"cat:{cat}" for cat in config.get("arxiv_categories", ["cs.CR", "cs.AI", "cs.CL", "cs.SE"]))
    params = urllib.parse.urlencode({"search_query": query, "start": "0", "max_results": str(config.get("arxiv_max_results", 60)), "sortBy": "submittedDate", "sortOrder": "descending"})
    root = ET.fromstring(http_get(ARXIV_URL + "?" + params))
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    out: list[Candidate] = []
    for entry in root.findall("atom:entry", ns):
        published = clean_text(entry.findtext("atom:published", default="", namespaces=ns))
        dt = parse_date(published)
        if dt is None or dt < cutoff:
            continue
        title = clean_text(entry.findtext("atom:title", default="", namespaces=ns))
        summary = clean_text(entry.findtext("atom:summary", default="", namespaces=ns))
        url = clean_text(entry.findtext("atom:id", default="", namespaces=ns))
        score = 18 + score_terms(f"{title} {summary}", AI_TERMS, 55)
        add_candidate(out, "ai_research", "arXiv", title, url, published, summary, score, {"authors": [clean_text(a.findtext("atom:name", default="", namespaces=ns)) for a in entry.findall("atom:author", ns)][:8]})
    return out


def deduplicate(items: list[Candidate]) -> list[Candidate]:
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    out: list[Candidate] = []
    for item in sorted(items, key=lambda x: x.rule_score, reverse=True):
        url = item.url.split("#", 1)[0].rstrip("/")
        title_key = re.sub(r"[^a-z0-9가-힣]+", "", item.title.lower())
        if url in seen_urls or title_key in seen_titles:
            continue
        seen_urls.add(url)
        seen_titles.add(title_key)
        out.append(item)
    return out


def collect_all(config: dict[str, Any]) -> tuple[list[Candidate], list[str]]:
    now = now_kst()
    cutoff = now - timedelta(hours=int(config.get("lookback_hours", 36)))
    items: list[Candidate] = []
    errors: list[str] = []
    collectors = [("CISA KEV", lambda: collect_cisa(cutoff)), ("NVD", lambda: collect_nvd(cutoff, now)), ("HackerOne Hacktivity", lambda: collect_hackerone(cutoff)), ("arXiv", lambda: collect_arxiv(cutoff, config))]
    for feed in config.get("rss_feeds", []):
        collectors.append((feed["name"], lambda feed=feed: collect_rss(feed, cutoff)))
    for name, fn in collectors:
        try:
            items.extend(fn())
        except Exception as exc:
            errors.append(f"{name}: {type(exc).__name__}: {exc}")
    return deduplicate(items), errors


def shortlist(items: list[Candidate], config: dict[str, Any]) -> list[Candidate]:
    floor = int(config.get("candidate_score_floor", 45))
    per_category = int(config.get("llm_candidates_per_category", 12))
    selected: list[Candidate] = []
    for category in ("security_news", "bug_bounty", "ai_research"):
        rows = [x for x in items if x.category == category and x.rule_score >= floor]
        selected.extend(sorted(rows, key=lambda x: x.rule_score, reverse=True)[:per_category])
    return selected


def briefing_schema() -> dict[str, Any]:
    return {"type": "object", "additionalProperties": False, "properties": {"briefing_date": {"type": "string"}, "items": {"type": "array", "items": {"type": "object", "additionalProperties": False, "properties": {"candidate_id": {"type": "string"}, "category": {"type": "string", "enum": ["security_news", "bug_bounty", "ai_research"]}, "core_summary": {"type": "string"}, "why_it_matters": {"type": "string"}, "concepts": {"type": "array", "items": {"type": "string"}}, "web_security_connection": {"type": "string"}, "bug_bounty_connection": {"type": "string"}, "automation_connection": {"type": "string"}, "learning_value": {"type": "string", "enum": ["HIGH", "MEDIUM", "NONE"]}, "next_action": {"type": ["string", "null"]}}, "required": ["candidate_id", "category", "core_summary", "why_it_matters", "concepts", "web_security_connection", "bug_bounty_connection", "automation_connection", "learning_value", "next_action"]}}, "completion": {"type": "object", "additionalProperties": False, "properties": {"status": {"type": "string", "enum": ["generated"]}, "selected_item_id": {"type": ["string", "null"]}, "decision": {"type": ["string", "null"]}}, "required": ["status", "selected_item_id", "decision"]}}, "required": ["briefing_date", "items", "completion"]}


def call_llm(candidates: list[Candidate], config: dict[str, Any]) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required. Add it as a GitHub Actions repository secret.")
    model = os.getenv("OPENAI_MODEL") or config.get("openai_model", "gpt-5-mini")
    limits = config["limits"]
    compact = [{"candidate_id": x.candidate_id, "category": x.category, "source": x.source, "title": x.title, "url": x.url, "published_at": x.published_at, "rule_score": x.rule_score, "text": x.text[:3000], "metadata": x.metadata} for x in candidates]
    instructions = f"""당신은 직무 정보 브리핑의 최종 편집자다. 목표는 읽을 자료를 늘리는 것이 아니라 읽지 않아도 되는 자료를 제거하는 것이다. 항목 수를 채우지 마라. 가치가 없으면 해당 영역을 0개로 반환하라.
사용자 초점: 웹 취약점 점검/모의해킹, HackerOne/Find the Gap 버그바운티, AI/Python/RPA 자동화와 개발 생산성.
선별 원칙: 출처와 날짜가 명확한 후보만 사용한다. 같은 사건/기법 중복은 하나만 남긴다. 단순 수익 인증, 잡담, 광고, 평범한 툴 목록은 제외한다. 연결점이 없으면 '직접 연결 없음'이라고 쓰고 억지로 만들지 않는다. 다음 행동은 실제로 할 가치가 있을 때만 정확히 1개, 아니면 null이다. 논문은 문제→방법→결과→실무 연결을 짧게 파악하게 한다. 보안 뉴스는 실제 악용, 고위험 신규 취약점, 공격 캠페인, 중요한 기술/업계 변화를 우선한다. 버그바운티는 재사용 가능한 방법론, 공개 리포트, 우회/체인, 공격 아이디어를 우선한다.
카테고리별 최대 출력: security_news={limits['security_news']}, bug_bounty={limits['bug_bounty']}, ai_research={limits['ai_research']}. candidate_id는 반드시 입력 후보 값을 그대로 사용한다."""
    body = {"model": model, "store": False, "instructions": instructions, "input": json.dumps(compact, ensure_ascii=False), "text": {"format": {"type": "json_schema", "name": "daily_job_briefing", "schema": briefing_schema(), "strict": True}}}
    req = urllib.request.Request(OPENAI_URL, data=json.dumps(body).encode("utf-8"), headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API HTTP {exc.code}: {detail[:1200]}") from exc
    parts: list[str] = []
    for output in payload.get("output", []):
        if output.get("type") == "message":
            for content in output.get("content", []):
                if content.get("type") == "output_text" and content.get("text"):
                    parts.append(content["text"])
    if not parts:
        raise RuntimeError("OpenAI response contained no output_text")
    return json.loads("".join(parts))


def validate_and_hydrate(result: dict[str, Any], candidates: list[Candidate], config: dict[str, Any]) -> dict[str, Any]:
    by_id = {x.candidate_id: x for x in candidates}
    counts = {"security_news": 0, "bug_bounty": 0, "ai_research": 0}
    hydrated: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in result.get("items", []):
        cid = item.get("candidate_id")
        if cid in seen or cid not in by_id:
            continue
        src = by_id[cid]
        if item.get("category") != src.category or counts[src.category] >= int(config["limits"][src.category]):
            continue
        counts[src.category] += 1
        seen.add(cid)
        hydrated.append({"id": cid, "category": src.category, "title": src.title, "source": src.source, "date": src.published_at, "url": src.url, "score": src.rule_score, "core_summary": clean_text(item.get("core_summary")), "why_it_matters": clean_text(item.get("why_it_matters")), "concepts": [clean_text(x) for x in item.get("concepts", []) if clean_text(x)][:5], "web_security_connection": clean_text(item.get("web_security_connection")), "bug_bounty_connection": clean_text(item.get("bug_bounty_connection")), "automation_connection": clean_text(item.get("automation_connection")), "learning_value": item.get("learning_value", "NONE"), "next_action": clean_text(item.get("next_action")) or None})
    return {"briefing_date": now_kst().date().isoformat(), "items": hydrated, "completion": {"status": "generated", "selected_item_id": None, "decision": None}}


def render_markdown(briefing: dict[str, Any], errors: list[str]) -> str:
    labels = {"security_news": "1. 정보보안 주요 뉴스", "bug_bounty": "2. HackerOne / 버그바운티 커뮤니티", "ai_research": "3. AI 주요 논문·전문자료"}
    lines = [f"# 직무 정보 브리핑 — {briefing['briefing_date']}", "", "선별 기준을 통과한 자료만 표시합니다. 항목 수를 채우기 위해 낮은 가치의 자료를 넣지 않습니다.", ""]
    for category in ("security_news", "bug_bounty", "ai_research"):
        lines += [f"## {labels[category]}", ""]
        rows = [x for x in briefing["items"] if x["category"] == category]
        if not rows:
            lines += ["오늘 선별 기준을 통과한 자료 없음.", ""]
            continue
        for item in rows:
            lines += [f"### [{item['id']}] {item['title']}", "", f"- 출처: {item['source']}", f"- 날짜: {item['date']}", f"- 원문: {item['url']}", f"- 선별 점수: {item['score']}", "", "**핵심 내용**", "", item["core_summary"], "", "**왜 중요한가**", "", item["why_it_matters"], "", "**내가 알아야 할 개념**", ""]
            lines.extend([f"- {c}" for c in item["concepts"]] or ["- 별도 핵심 개념 없음"])
            lines += ["", "**현재 웹 취약점 점검 / 모의해킹과 연결점**", "", item["web_security_connection"] or "직접 연결 없음.", "", "**HackerOne / Find the Gap 버그바운티와 연결점**", "", item["bug_bounty_connection"] or "직접 연결 없음.", "", "**AI / 자동화와 연결점**", "", item["automation_connection"] or "직접 연결 없음.", "", f"**오늘 추가로 읽거나 실습할 가치:** {item['learning_value']}", "", "**실제 다음 행동 1개**", "", item["next_action"] or "추가 행동 없음.", "", "---", ""]
    lines += ["## 오늘의 종료 판단", "", "브리핑 생성만으로는 완료가 아닙니다. 이 Issue에 아래 둘 중 하나만 댓글로 남기면 오늘 정보 소비 사이클을 닫습니다.", "", "- 가져갈 내용이 있으면: `/take ITEM_ID`", "- 추가 행동이 없으면: `/no-action`", "", "예: `/take BUG-1A2B3C4D`", "", "<!-- daily-job-briefing -->", f"<!-- briefing-date: {briefing['briefing_date']} -->"]
    if errors:
        lines += ["", "<details>", "<summary>수집기 상태</summary>", "", "일부 수집원이 실패했지만 나머지 소스로 브리핑을 생성했습니다.", ""]
        lines.extend(f"- `{e}`" for e in errors)
        lines += ["", "</details>"]
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(briefing: dict[str, Any], markdown: str, raw_candidates: list[Candidate], errors: list[str]) -> None:
    date = briefing["briefing_date"]
    root = Path("data/job-briefing")
    root.mkdir(parents=True, exist_ok=True)
    payload = {**briefing, "collector_errors": errors, "candidate_count": len(raw_candidates)}
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    (root / f"{date}.json").write_text(text, encoding="utf-8")
    (root / "latest.json").write_text(text, encoding="utf-8")
    (root / f"{date}.md").write_text(markdown, encoding="utf-8")
    (root / "latest.md").write_text(markdown, encoding="utf-8")


def generate(config_path: str) -> None:
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    candidates, errors = collect_all(config)
    short = shortlist(candidates, config)
    if not short:
        briefing = {"briefing_date": now_kst().date().isoformat(), "items": [], "completion": {"status": "generated", "selected_item_id": None, "decision": None}}
    else:
        briefing = validate_and_hydrate(call_llm(short, config), short, config)
    markdown = render_markdown(briefing, errors)
    write_outputs(briefing, markdown, candidates, errors)
    print(json.dumps({"briefing_date": briefing["briefing_date"], "selected_items": len(briefing["items"]), "candidates": len(candidates), "collector_errors": errors}, ensure_ascii=False))


def decide(issue_title: str, comment: str) -> None:
    match = re.fullmatch(r"\[Daily Job Briefing\]\s+(\d{4}-\d{2}-\d{2})", issue_title.strip())
    if not match:
        raise ValueError("Issue title is not a Daily Job Briefing title.")
    date = match.group(1)
    source_path = Path("data/job-briefing") / f"{date}.json"
    if not source_path.exists():
        raise FileNotFoundError(f"Briefing data not found: {source_path}")
    briefing = json.loads(source_path.read_text(encoding="utf-8"))
    command = comment.strip()
    if command == "/no-action":
        decision, item_id = "no_action", None
    else:
        take = re.fullmatch(r"/take\s+([A-Z]+-[A-F0-9]{8})", command)
        if not take:
            raise ValueError("Use `/take ITEM_ID` or `/no-action`.")
        item_id = take.group(1)
        if item_id not in {x["id"] for x in briefing.get("items", [])}:
            raise ValueError(f"Unknown ITEM_ID: {item_id}")
        decision = "takeaway"
    record = {"date": date, "decision": decision, "item_id": item_id, "cycle_status": "closed"}
    path = Path("data/job-briefing/decisions") / f"{date}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily job briefing automation")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("--config", default="config/job_briefing.json")
    dec = sub.add_parser("decide")
    dec.add_argument("--issue-title", required=True)
    dec.add_argument("--comment", required=True)
    args = parser.parse_args()
    if args.command == "generate":
        generate(args.config)
    else:
        decide(args.issue_title, args.comment)


if __name__ == "__main__":
    main()
