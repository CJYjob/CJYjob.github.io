---
title: "운동 기록"
date: 2026-05-28
draft: false
description: "정형 데이터 기반 운동 기록 공개 페이지"
---

# 운동 기록

## 시간-볼륨 그래프 (최근 30일, strength)

{{</* workout-volume-chart days="30" */>}}

## 시간-거리 그래프 (최근 30일, cardio)

{{</* workout-cardio-chart days="30" */>}}

## 분석

(이 절은 운동 코치가 누적 데이터를 토대로 갱신한다.)

## 운동 기록 (일자 내림차순)

{{</* datatable activity="workout" sort="date desc" */>}}
