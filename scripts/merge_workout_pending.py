#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORKOUT_PATH = ROOT / "data" / "workout.json"
PAGE_PATH = ROOT / "content" / "portfolio" / "workout" / "index.md"
PENDING_PATTERN = "workout_pending_*.json"

def read_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array.")
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"{path} item {idx} must be an object.")
    return data

def write_json(path: Path, data: list[dict[str, Any]]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

def record_key(record: dict[str, Any]) -> tuple[Any, ...]:
    return (
        record.get("date"),
        record.get("session_id"),
        record.get("type"),
        record.get("exercise"),
        record.get("started_at"),
        record.get("ended_at"),
    )

def validate_record(record: dict[str, Any], index: int) -> None:
    required = ["date", "session_id", "type", "exercise", "started_at", "ended_at", "duration_min", "note"]
    for field in required:
        if field not in record:
            raise ValueError(f"record {index} missing required field: {field}")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(record["date"])):
        raise ValueError(f"record {index} has invalid date: {record['date']}")
    started = datetime.fromisoformat(str(record["started_at"]))
    ended = datetime.fromisoformat(str(record["ended_at"]))
    duration = float(record["duration_min"])
    actual = (ended - started).total_seconds() / 60
    if abs(actual - duration) > 0.08:
        raise ValueError(f"record {index} duration mismatch: duration_min={duration}, actual={actual:.2f}")
    if record["type"] in {"strength", "prehab"} and "sets" in record:
        if not isinstance(record["sets"], list):
            raise ValueError(f"record {index} sets must be a list.")
        for set_idx, item in enumerate(record["sets"]):
            for field in ["set_number", "weight_kg", "reps", "volume_kg", "rest_sec"]:
                if field not in item:
                    raise ValueError(f"record {index} set {set_idx} missing field: {field}")
            expected = round(float(item["weight_kg"]) * int(item["reps"]), 2)
            actual_volume = round(float(item["volume_kg"]), 2)
            if abs(expected - actual_volume) > 0.02:
                raise ValueError(f"record {index} set {set_idx} volume mismatch: expected={expected}, actual={actual_volume}")
    if record["type"] == "cardio" and "distance_km" in record and float(record["distance_km"]) < 0:
        raise ValueError(f"record {index} has negative distance_km.")

def validate_all(records: list[dict[str, Any]]) -> None:
    seen = set()
    for idx, record in enumerate(records):
        validate_record(record, idx)
        key = record_key(record)
        if key in seen:
            raise ValueError(f"duplicate workout record detected: {key}")
        seen.add(key)

def merge_records(workout_records: list[dict[str, Any]], pending_records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    existing = {record_key(record) for record in workout_records}
    added = 0
    for record in pending_records:
        key = record_key(record)
        if key not in existing:
            workout_records.append(record)
            existing.add(key)
            added += 1
    workout_records.sort(key=lambda item: (item.get("date", ""), item.get("ended_at", "")))
    return workout_records, added

def calculate_stats(records: list[dict[str, Any]]) -> dict[str, float | int | str]:
    sessions = {record["session_id"] for record in records}
    total_duration = sum(float(record.get("duration_min", 0)) for record in records)
    cardio_distance = sum(float(record.get("distance_km", 0)) for record in records if record.get("type") == "cardio")
    volume = 0.0
    for record in records:
        if record.get("type") != "strength":
            continue
        for item in record.get("sets", []):
            volume += float(item.get("volume_kg", 0))
    latest_date = max((str(record["date"]) for record in records), default="")
    return {
        "count": len(records),
        "sessions": len(sessions),
        "total_duration": round(total_duration, 2),
        "cardio_distance": round(cardio_distance, 2),
        "strength_volume": round(volume, 2),
        "latest_date": latest_date,
    }

def render_page(records: list[dict[str, Any]], stats: dict[str, float | int | str]) -> str:
    latest_records = [r for r in records if r["date"] == stats["latest_date"]]
    latest_cardio_min = sum(float(r.get("duration_min", 0)) for r in latest_records if r.get("type") == "cardio")
    latest_cardio_km = sum(float(r.get("distance_km", 0)) for r in latest_records if r.get("type") == "cardio")
    latest_mobility = sum(float(r.get("duration_min", 0)) for r in latest_records if r.get("type") == "mobility")
    latest_prehab = sum(float(r.get("duration_min", 0)) for r in latest_records if r.get("type") == "prehab")
    shoulder_note = ""
    if any("shoulder discomfort" in str(r.get("note", "")).lower() for r in latest_records):
        shoulder_note = (
            "\n\n최근 세션에서는 왼쪽 어깨 불편감이 지속되어 상체 웨이트를 제외하고, "
            "유산소·관절 풀기·무릎 기능 운동으로 세션을 전환했습니다. "
            "다음 상체 웨이트는 통증 확인용 저강도 테스트로만 재진입합니다."
        )
    return f'''---
title: "운동 기록"
date: 2026-05-28
draft: false
description: "정형 데이터, 근력, 유산소, 체력 운동 기록 공개 페이지"
---

# 운동 기록

## 웨이트 (최근 30일, strength)

{{{{< workout-volume-chart days="30" >}}}}

## 유산소 (최근 30일, cardio)

{{{{< workout-cardio-chart days="30" >}}}}

## 분석

현재 누적 기준으로 운동 기록은 {stats["latest_date"]} 세션까지 병합되어 있습니다. 누적 기록은 총 {stats["count"]}건, 세션 {stats["sessions"]}회, 총 운동 시간 약 {stats["total_duration"]}분, 유산소 거리 약 {stats["cardio_distance"]}km, 누적 웨이트 볼륨 약 {stats["strength_volume"]}kg입니다.

최근 세션 기준으로 유산소는 약 {latest_cardio_min:.0f}분, 약 {latest_cardio_km:.2f}km 수행되었습니다. 관절 풀기와 회복성 움직임은 약 {latest_mobility:.2f}분, 무릎 기능 운동은 약 {latest_prehab:.2f}분 기록되었습닄.{shoulder_note}

현재 운동 패턴은 인클라인 트레드밀을 기본 유산소 축으로 두고, 상체 웨이트는 어깨 상태에 따라 조절합니다. `Dumbbell Incline Bench Press`는 상부 대흉근, `Dumbbell Incline Bench Row`와 `Seated Row`는 중부 승모근, `Side Lateral Raise`는 측면 삼각근, `Lat Pulldown`, `Straight-Arm Pulldown`, `Assisted Chin-Up`은 광배근 기준으로 정리합니다.

## 운동 기록 (일자 내림차순)

{{{{< datatable activity="workout" sort="date desc" >}}}}
'''

def main() -> None:
    if not WORKOUT_PATH.exists():
        raise FileNotFoundError(WORKOUT_PATH)
    pending_paths = sorted((ROOT / "data").glob(PENDING_PATTERN))
    if not pending_paths:
        print("No pending workout files found. Nothing to merge.")
        return
    workout_records = read_json(WORKOUT_PATH)
    pending_records: list[dict[str, Any]] = []
    for path in pending_paths:
        pending_records.extend(read_json(path))
    validate_all(workout_records)
    validate_all(pending_records)
    merged_records, added = merge_records(workout_records, pending_records)
    validate_all(merged_records)
    if added:
        write_json(WORKOUT_PATH, merged_records)
        PAGE_PATH.write_text(render_page(merged_records, calculate_stats(merged_records)), encoding="utf-8")
        print(f"Merged {added} workout records.")
    else:
        print("Pending records were already present in workout.json.")
    for path in pending_paths:
        path.unlink()
        print(f"Removed pending file: {path.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
