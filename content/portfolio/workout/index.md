---
title: "운동 기록"
date: 2026-05-28
draft: false
description: "정형 데이터, 근력, 유산소, 체력 운동 기록 공개 페이지"
---

# 운동 기록

## 웨이트 (최근 30일, strength)

{{< workout-volume-chart days="30" >}}

## 유산소 (최근 30일, cardio)

{{< workout-cardio-chart days="30" >}}

## 분석

현재 메인 데이터(`data/workout.json`)에 바로 반영된 마지막 운동 기록은 2026-06-09 아침 세션까지입니다. 누적 기준은 총 기록 37건, 세션 7회, 총 기록 운동 시간 약 428.66분, 누적 유산소 거리 약 9.02km, 누적 웨이트 볼륨 약 15,836.37kg입니다.

2026-06-10 아침 세션은 별도 pending 파일(`data/workout_pending_2026-06-10-morning.json`)로 보존되어 있으며, 아직 메인 데이터에는 병합되지 않았습니다. 해당 세션은 인클라인 트레드밀 총 22분, 약 1.18km와 상체 관절 풀기 3분, 무릎 기능 운동 약 4.65분으로 구성됩니다. 왼쪽 어깨 불편감이 지속되어 상체 웨이트는 제외했습니다.

다음 병합 시에는 pending 파일의 4건을 메인 `data/workout.json`에 추가하고, 공개 페이지의 누적 지표를 41건, 8세션, 총 458.31분, 유산소 10.20km로 갱신해야 합니다.

## 운동 기록 (일자 내림차순)

{{< datatable activity="workout" sort="date desc" >}}
