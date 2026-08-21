#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
WORKOUT = DATA / "workout.json"
PAGE = ROOT / "content" / "ko" / "portfolio" / "workout.md"


def load(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not all(isinstance(x, dict) for x in data):
        raise ValueError(f"{path} must be a JSON array of objects")
    return data


def save(path: Path, data: list[dict[str, Any]]) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def key(r: dict[str, Any]) -> tuple[Any, ...]:
    return (
        r.get("date"),
        r.get("session_id"),
        r.get("type"),
        r.get("exercise"),
        r.get("started_at"),
        r.get("ended_at"),
    )


def append_note_once(record: dict[str, Any], marker: str) -> bool:
    note = str(record.get("note", ""))
    if marker in note:
        return False
    record["note"] = note + ("\n" if note else "") + marker
    return True


def validate(records: list[dict[str, Any]]) -> None:
    required = {
        "date",
        "session_id",
        "type",
        "exercise",
        "started_at",
        "ended_at",
        "duration_min",
        "note",
    }
    seen: set[tuple[Any, ...]] = set()

    for i, r in enumerate(records):
        missing = required - set(r)
        if missing:
            raise ValueError(f"record {i} missing {sorted(missing)}")

        started = datetime.fromisoformat(str(r["started_at"]))
        ended = datetime.fromisoformat(str(r["ended_at"]))
        actual = (ended - started).total_seconds() / 60
        if abs(actual - float(r["duration_min"])) > 0.08:
            raise ValueError(f"record {i} duration mismatch")

        for s in r.get("sets", []):
            expected = round(float(s["weight_kg"]) * int(s["reps"]), 2)
            if abs(expected - round(float(s["volume_kg"]), 2)) > 0.02:
                raise ValueError(f"record {i} volume mismatch")

        k = key(r)
        if k in seen:
            raise ValueError(f"duplicate record {k}")
        seen.add(k)


def correct(records: list[dict[str, Any]]) -> int:
    """Apply narrowly scoped historical data corrections before rendering.

    New workout-session details should be stored in pending workout JSON files,
    not hard-coded here. Keep this function limited to already-approved
    historical corrections that repair old records.
    """
    changed = 0

    for r in records:
        if (
            r.get("date") == "2026-06-08"
            and r.get("session_id") == "2026-06-08-evening"
            and r.get("exercise") == "Machine Arm Curl"
            and r.get("started_at") == "2026-06-08T20:16:31+09:00"
            and r.get("ended_at") == "2026-06-08T20:21:11+09:00"
        ):
            r["exercise"] = "Straight-Arm Pulldown"
            r["target_muscles"] = ["Latissimus Dorsi"]
            marker = (
                "Corrected from Machine Arm Curl / Biceps Brachii to "
                "Straight-Arm Pulldown / Latissimus Dorsi."
            )
            if append_note_once(r, marker):
                changed += 1

        if (
            r.get("date") == "2026-06-14"
            and r.get("session_id") == "2026-06-14-afternoon"
            and r.get("exercise") == "Squat"
            and r.get("target_muscles") != ["Lower Body Muscles"]
        ):
            r["target_muscles"] = ["Lower Body Muscles"]
            marker = "Target muscle corrected to Lower Body Muscles."
            if append_note_once(r, marker):
                changed += 1

        if (
            r.get("date") == "2026-06-23"
            and r.get("session_id") == "2026-06-23-morning"
            and r.get("exercise") == "Assisted Chin-Up"
            and r.get("target_muscles") != ["Latissimus Dorsi"]
        ):
            r["target_muscles"] = ["Latissimus Dorsi"]
            marker = (
                "Target muscle corrected to Latissimus Dorsi only "
                "based on user approval."
            )
            if append_note_once(r, marker):
                changed += 1

    return changed


def merge(records: list[dict[str, Any]], pending: list[dict[str, Any]]) -> int:
    seen = {key(r) for r in records}
    added = 0

    for r in pending:
        if key(r) in seen:
            continue
        records.append(r)
        seen.add(key(r))
        added += 1

    records.sort(key=lambda r: (r.get("date", ""), r.get("ended_at", "")))
    return added


def stats(records: list[dict[str, Any]]) -> dict[str, Any]:
    latest = max((str(r["date"]) for r in records), default="")
    return {
        "latest": latest,
        "count": len(records),
        "sessions": len({r["session_id"] for r in records}),
        "duration": round(
            sum(float(r.get("duration_min", 0)) for r in records),
            2,
        ),
        "distance": round(
            sum(
                float(r.get("distance_km", 0))
                for r in records
                if r.get("type") == "cardio"
            ),
            2,
        ),
        "volume": round(
            sum(
                float(s.get("volume_kg", 0))
                for r in records
                if r.get("type") == "strength"
                for s in r.get("sets", [])
            ),
            2,
        ),
    }


def render(records: list[dict[str, Any]]) -> str:
    s = stats(records)
    latest = [r for r in records if r["date"] == s["latest"]]

    cardio_min = sum(
        float(r.get("duration_min", 0))
        for r in latest
        if r.get("type") == "cardio"
    )
    cardio_km = sum(
        float(r.get("distance_km", 0))
        for r in latest
        if r.get("type") == "cardio"
    )
    mobility = sum(
        float(r.get("duration_min", 0))
        for r in latest
        if r.get("type") == "mobility"
    )
    prehab = sum(
        float(r.get("duration_min", 0))
        for r in latest
        if r.get("type") == "prehab"
    )

    return f'''---
title: "운동 기록"
date: 2026-05-28
draft: false
description: "정형 데이터, 그래프, 유산소와 철봉 운동 기록 공개 페이지"
categories:
  - "Workout"
tags:
  - "Workout"
  - "Strength"
  - "Cardio"
ShowToc: true
aliases:
  - /portfolio/workout/
---

# 운동 기록

## 웨이트 ({s["latest"]} 기준 최근 30일, strength)
{{{{< workout-volume-chart days="30" >}}}}

## 유산소 ({s["latest"]} 기준 최근 30일, cardio)
{{{{< workout-cardio-chart days="30" >}}}}

## 분석

현재 누적 기준으로 운동 기록은 총 {s["count"]}건, 세션 {s["sessions"]}회, 총 운동 시간 약 {s["duration"]}분, 유산소 거리 약 {s["distance"]}km, 누적 웨이트 볼륨 약 {s["volume"]}kg입니다.

최근 세션 기준으로 유산소는 약 {cardio_min:.0f}분, 약 {cardio_km:.2f}km 수행되었습니다. 관절 품질과 회복성, 워업 준비를 위한 스트레칭·모빌리티는 약 {mobility:.2f}분, 무릎 기능 운동은 약 {prehab:.2f}분 기록되었습니다.

현재 운동 패턴은 일관된 트래킹을 기반으로 근력과 유산소 축을 함께 누적하는 구조입니다. 웨이트 그래프는 운동 종류가 아니라 타깃 근육별 누적 볼륨으로 표시됩니다.

## 운동 기록
(일자 내림차순)

{{{{< datatable activity="workout" sort="date desc" >}}}}
'''


def main() -> None:
    records = load(WORKOUT)
    corrections = correct(records)

    pending_paths = sorted(DATA.glob("workout_pending_*.json"))
    pending: list[dict[str, Any]] = []
    for p in pending_paths:
        pending.extend(load(p))

    validate(records)
    if pending:
        validate(pending)

    added = merge(records, pending) if pending else 0
    validate(records)

    if corrections or added:
        save(WORKOUT, records)
        PAGE.write_text(render(records), encoding="utf-8")
        print(f"Applied {corrections} corrections and merged {added} records.")
    else:
        print(
            "No pending workout files or workout corrections found. "
            "Nothing to merge."
        )

    for p in pending_paths:
        p.unlink()
        print(f"Removed pending file: {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
