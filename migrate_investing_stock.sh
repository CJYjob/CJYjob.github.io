#!/usr/bin/env bash
# =====================================================================
# 블로그 재구성: 투자 > 주식 > {이론, 실습}  (Option C)
#  - 이론  = 기존 투자 기초 9파트를 git mv 로 이동(이력 보존)
#  - 실습  = ETF 시리즈 12파트(본문은 이후 v2.md에서 채움; 여기선 골격)
#  - 옛 ETF 페이지/로그 삭제, 수동 네비 블록 삭제(자동 이전/다음으로 대체)
#  - nav 파셜 오버라이드(현재 섹션 한정) + ShowPostNavLinks: true
# 사용: 저장소 루트(hugo.yaml 보이는 곳)에서  bash migrate_investing_stock.sh
# =====================================================================
set -euo pipefail

# 0) 안전 점검 -------------------------------------------------------
[ -f hugo.yaml ] && [ -d content/portfolio ] || {
  echo "❌ 저장소 루트에서 실행하세요 (hugo.yaml 이 보이는 위치)."; exit 1; }

ROOT="content/portfolio/investing"
STOCK="$ROOT/stock"
THEORY="$STOCK/theory"
PRACTICE="$STOCK/practice"
FOUND="content/portfolio/investment-foundations"

echo "▶ 1) 디렉터리 생성"
mkdir -p "$THEORY" "$PRACTICE" layouts/_partials content/log/etf-live-trading

echo "▶ 2) 이론(투자 기초) 9파트 이동 (git mv, 이력 보존)"
for p in part-01-market-structure part-02-products-and-accounts part-03-financial-statements \
         part-04-company-analysis part-05-technical-indicators part-06-derivatives-etf-mechanism \
         part-07-investment-judgment-structure part-08-rule-based-investing part-09-mock-investment; do
  git mv "$FOUND/$p" "$THEORY/$p"
done
git rm -q "$FOUND/_index.md"
rmdir "$FOUND" 2>/dev/null || true

echo "▶ 3) 이동된 이론 파트: 옛 경로 링크 치환 + 하단 수동 네비 블록 삭제"
# (안전망) 본문에 남은 옛 경로를 새 경로로
perl -i -pe 's{/portfolio/investment-foundations/}{/portfolio/investing/stock/theory/}g' "$THEORY"/*/index.md
# 하단 '## 투자 기초 시리즈 전체 링크' 블록 + 그 앞 구분선(---) 제거
for f in "$THEORY"/*/index.md; do
  perl -0777 -i -pe 's/\n+---\n+## 투자 기초 시리즈 전체 링크.*\z/\n/s' "$f"
done

echo "▶ 4) 옛 ETF 페이지·로그 삭제 (실습 시리즈로 통합)"
git rm -qr content/portfolio/etf-dual-strategy content/portfolio/etf-dual-strategy-* 2>/dev/null || true
git rm -qr content/log/etf-dual-strategy-* 2>/dev/null || true

echo "▶ 5) _index.md 4개 작성 (투자 / 주식 / 이론 / 실습)"
# ---- 투자(최상위) ----
cat > "$ROOT/_index.md" <<'EOF'
---
title: "투자"
date: 2026-06-09
draft: false
description: "자산군별 투자 학습. 현재는 주식(코스피200·코스닥150)을 이론과 실습으로 정리한다."
categories: ["Portfolio", "Investment"]
tags: ["Investment"]
ShowToc: false
---

## 개요

자산군별로 투자 학습을 정리한다. 현재 트랙은 다음과 같다.

- **[주식](/portfolio/investing/stock/)** — 코스피200·코스닥150 중심. 이론과 실습으로 나뉜다.
EOF

# ---- 주식(중간) : 이론·실습 허브 ----
cat > "$STOCK/_index.md" <<'EOF'
---
title: "주식"
date: 2026-06-09
draft: false
description: "코스피200·코스닥150 중심의 주식 투자 학습을 이론과 실습 두 트랙으로 정리한다."
categories: ["Portfolio", "Investment"]
tags: ["Investment", "Stock"]
weight: 10
ShowToc: false
---

## 개요

주식 투자 학습을 두 트랙으로 나눈다.

- **[투자 이론](/portfolio/investing/stock/theory/part-01-market-structure/)** — 시장 구조부터 규칙 기반 투자·모의투자까지 판단의 토대.
- **[투자 실습](/portfolio/investing/stock/practice/part-01-foundation-and-edge/)** — 그 이론을 코스피200·코스닥150 양방향 ETF 전략으로 구현·백테스트·자동화·실전 기록.
EOF

# ---- 이론(투자 기초) : cascade 9 ----
cat > "$THEORY/_index.md" <<'EOF'
---
title: "투자 이론"
date: 2026-06-08
draft: false
description: "시장 구조, 금융상품·절세계좌, 재무제표, 기업 분석, 기술적 지표, 파생·ETF 메커니즘, 투자 판단 구조, 규칙 기반 투자, 모의투자까지 투자의 이론적 토대를 정리한다."
categories: ["Portfolio", "Investment"]
tags: ["Investment", "Foundations"]
weight: 10
ShowToc: true
TocOpen: true
cascade:
  - weight: 10
    summary: "시장 구조와 자산배분의 기본 개념을 정리한다."
    target: { path: "{/portfolio/investing/stock/theory/part-01-market-structure,/portfolio/investing/stock/theory/part-01-market-structure/**}" }
  - weight: 20
    summary: "예금, 채권, 펀드, ETF, ISA, 연금저축, IRP 등 투자상품과 절세 계좌를 정리한다."
    target: { path: "{/portfolio/investing/stock/theory/part-02-products-and-accounts,/portfolio/investing/stock/theory/part-02-products-and-accounts/**}" }
  - weight: 30
    summary: "재무상태표, 손익계산서, 현금흐름표와 기본 투자 지표를 정리한다."
    target: { path: "{/portfolio/investing/stock/theory/part-03-financial-statements,/portfolio/investing/stock/theory/part-03-financial-statements/**}" }
  - weight: 40
    summary: "산업, 경쟁력, 사업보고서, 돈 버는 구조, 경쟁사 비교, 성장주와 가치주를 정리한다."
    target: { path: "{/portfolio/investing/stock/theory/part-04-company-analysis,/portfolio/investing/stock/theory/part-04-company-analysis/**}" }
  - weight: 50
    summary: "이동평균, 볼린저밴드, ADX, ATR, MACD, z-점수 등 기술적 지표의 기본 원리를 정리한다."
    target: { path: "{/portfolio/investing/stock/theory/part-05-technical-indicators,/portfolio/investing/stock/theory/part-05-technical-indicators/**}" }
  - weight: 60
    summary: "선물, 베이시스, 롤오버, ETF NAV, 괴리율, AP·LP, 인버스 ETF 구조를 정리한다."
    target: { path: "{/portfolio/investing/stock/theory/part-06-derivatives-etf-mechanism,/portfolio/investing/stock/theory/part-06-derivatives-etf-mechanism/**}" }
  - weight: 70
    summary: "관찰, 아이디어, 가설, 검증, 체크리스트, 판단, 기록, 복기로 이어지는 투자 판단 구조를 정리한다."
    target: { path: "{/portfolio/investing/stock/theory/part-07-investment-judgment-structure,/portfolio/investing/stock/theory/part-07-investment-judgment-structure/**}" }
  - weight: 80
    summary: "감정이 아니라 규칙이 판단하도록 규칙 설계, 백테스트, 자동화 구조를 정리한다."
    target: { path: "{/portfolio/investing/stock/theory/part-08-rule-based-investing,/portfolio/investing/stock/theory/part-08-rule-based-investing/**}" }
  - weight: 90
    summary: "모의투자, 매수·매도 이유, 리스크 요인, 가격 판단, 복기와 시스템 개선을 정리한다."
    target: { path: "{/portfolio/investing/stock/theory/part-09-mock-investment,/portfolio/investing/stock/theory/part-09-mock-investment/**}" }
---

## 개요

이 트랙은 투자 판단의 이론적 토대를 1부부터 9부까지 정리한다.

`경제·시장 → 금융상품 → 재무제표 → 기업분석 → 기술적 지표 → 파생·ETF 메커니즘 → 판단 구조 → 규칙 기반 투자 → 모의투자`

여기서 익힌 구조는 [투자 실습](/portfolio/investing/stock/practice/part-01-foundation-and-edge/) 트랙에서 코스피200·코스닥150 양방향 ETF 전략으로 구현된다.
EOF

# ---- 실습(ETF 시리즈) : cascade 12 ----
cat > "$PRACTICE/_index.md" <<'EOF'
---
title: "투자 실습"
date: 2026-06-09
draft: false
description: "투자 이론을 코스피200·코스닥150 정방향/인버스 ETF 전략으로 구현한다. 전략 논리·국면 지표·상품 메커니즘·운용·리스크·백테스트·코드·자동매매·실전 기록까지."
categories: ["Portfolio", "Investment"]
tags: ["Investment", "ETF", "System Trading", "Backtest"]
weight: 20
ShowToc: true
TocOpen: true
cascade:
  - weight: 10
    summary: "양방향 보유의 실체와 수익 원천(방향 A / 변동성 수확 B)."
    target: { path: "{/portfolio/investing/stock/practice/part-01-foundation-and-edge,/portfolio/investing/stock/practice/part-01-foundation-and-edge/**}" }
  - weight: 20
    summary: "추세·횡보 1차 축과 5단계 국면, KOSPI·KOSDAQ 차이, 하락 비대칭."
    target: { path: "{/portfolio/investing/stock/practice/part-02-market-regimes,/portfolio/investing/stock/practice/part-02-market-regimes/**}" }
  - weight: 30
    summary: "국면 판별 지표 6분류와 선택한 4개(SMA·ADX·BB %B·수급 z-score)."
    target: { path: "{/portfolio/investing/stock/practice/part-03-regime-indicators,/portfolio/investing/stock/practice/part-03-regime-indicators/**}" }
  - weight: 40
    summary: "외국인·기관 수급 읽기와 정규화(시총 대비·z-점수)."
    target: { path: "{/portfolio/investing/stock/practice/part-04-supply-demand,/portfolio/investing/stock/practice/part-04-supply-demand/**}" }
  - weight: 50
    summary: "ETF 가격 메커니즘, 선물·베이시스·콘탱고, 비용과 세금 비대칭."
    target: { path: "{/portfolio/investing/stock/practice/part-05-etf-futures-cost,/portfolio/investing/stock/practice/part-05-etf-futures-cost/**}" }
  - weight: 60
    summary: "국면별 포지션 비중과 위험조정 성과 지표."
    target: { path: "{/portfolio/investing/stock/practice/part-06-position-and-metrics,/portfolio/investing/stock/practice/part-06-position-and-metrics/**}" }
  - weight: 70
    summary: "진입 전 거르는 리스크·예외 조건과 인버스 사용 원칙."
    target: { path: "{/portfolio/investing/stock/practice/part-07-risk-and-exceptions,/portfolio/investing/stock/practice/part-07-risk-and-exceptions/**}" }
  - weight: 80
    summary: "미래참조 차단·비용·과적합 방지를 포함한 백테스트 9단계 설계."
    target: { path: "{/portfolio/investing/stock/practice/part-08-backtest-design,/portfolio/investing/stock/practice/part-08-backtest-design/**}" }
  - weight: 90
    summary: "pykrx 데이터 수집과 국면 라벨링 구현 코드."
    target: { path: "{/portfolio/investing/stock/practice/part-09-implementation,/portfolio/investing/stock/practice/part-09-implementation/**}" }
  - weight: 100
    summary: "미래참조 차단·비용/세금·검증을 담은 백테스트 엔진 코드."
    target: { path: "{/portfolio/investing/stock/practice/part-10-backtest-engine,/portfolio/investing/stock/practice/part-10-backtest-engine/**}" }
  - weight: 110
    summary: "데이터→신호→주문→기록 자동매매 구조와 운용 원칙."
    target: { path: "{/portfolio/investing/stock/practice/part-11-automation,/portfolio/investing/stock/practice/part-11-automation/**}" }
  - weight: 120
    summary: "모의·실전 매매와 복기 기록(/log 연결)."
    target: { path: "{/portfolio/investing/stock/practice/part-12-live-and-review,/portfolio/investing/stock/practice/part-12-live-and-review/**}" }
---

## 개요

[투자 이론](/portfolio/investing/stock/theory/part-01-market-structure/)에서 익힌 구조를 KODEX 200·인버스, KODEX 코스닥150·인버스에 적용한 실습 트랙이다.

`전략 논리 → 국면 도구 → 상품 메커니즘 → 운용·리스크 → 백테스트 설계·코드 → 자동매매 → 모의·실전 기록`
EOF

echo "▶ 6) nav 파셜 오버라이드 (현재 섹션 한정 이전/다음)"
cat > layouts/_partials/post_nav_links.html <<'EOF'
{{- $pages := .CurrentSection.RegularPages }}
{{- if and (gt (len $pages) 1) (in $pages . ) }}
<nav class="paginav">
  {{- with $pages.Next . }}
  <a class="prev" href="{{ .Permalink }}">
    <span class="title">« {{ i18n "prev_page" }}</span>
    <span>{{- .Name -}}</span>
  </a>
  {{- end }}
  {{- with $pages.Prev . }}
  <a class="next" href="{{ .Permalink }}">
    <span class="title">{{ i18n "next_page" }} »</span>
    <span>{{- .Name -}}</span>
  </a>
  {{- end }}
</nav>
{{- end }}
EOF

echo "▶ 7) hugo.yaml: ShowPostNavLinks -> true"
perl -i -pe 's/ShowPostNavLinks:\s*false/ShowPostNavLinks: true/' hugo.yaml

echo "▶ 8) 실습 12파트 골격 생성 (front matter + 본문 TODO)"
PARTS=(
"part-01-foundation-and-edge|①|전략의 출발점과 수익 원천|v2 0·1장"
"part-02-market-regimes|②|시장을 국면으로 나누기|v2 2장"
"part-03-regime-indicators|③|국면 판별 지표|v2 3장"
"part-04-supply-demand|④|수급 읽기|v2 4장"
"part-05-etf-futures-cost|⑤|ETF·선물·비용 메커니즘|v2 5·6·7장"
"part-06-position-and-metrics|⑥|포지션 운용과 성과 지표|v2 8·9장"
"part-07-risk-and-exceptions|⑦|리스크와 예외 조건|repo 9-1/9-2/9-3"
"part-08-backtest-design|⑧|백테스트 설계|v2 10장"
"part-09-implementation|⑨|구현 — 데이터 수집·국면 라벨링|v2 11장(python 셀1-4)"
"part-10-backtest-engine|⑩|백테스트 엔진·검증|v2 12장(python 셀5-8+검증표)"
"part-11-automation|⑪|자동매매와 운용 원칙|v2 13장+conclusion"
"part-12-live-and-review|⑫|모의·실전 운용과 복기|신규+/log 연결"
)
for row in "${PARTS[@]}"; do
  IFS='|' read -r slug num title src <<< "$row"
  mkdir -p "$PRACTICE/$slug"
  cat > "$PRACTICE/$slug/index.md" <<EOF
---
title: "투자 실습 $num $title"
date: 2026-06-09
draft: false
description: "$title — $src 기반."
categories: ["Investment"]
tags: ["Investment", "ETF"]
---

<!-- TODO: 본문을 여기에 채우세요 — 출처: $src -->
EOF
done

echo "▶ 9) 실전 기록 로그 트랙 생성"
cat > content/log/etf-live-trading/_index.md <<'EOF'
---
title: "ETF 실전 매매 기록"
date: 2026-06-09
draft: false
description: "양방향 ETF 전략의 모의·실전 매매와 복기를 누적 기록한다."
categories: ["Investment"]
tags: ["Investment", "ETF", "Trading"]
---

진입 전 최소 기록: 현재 국면 판단 · 선택한 ETF 방향 · 진입 이유 · 비중 결정 이유 · 종료 조건 · 예외 조건 해당 여부.
EOF

echo "▶ 10) 스테이징"
git add -A

echo
echo "✅ 구조 재편 완료. 남은 일:"
echo "   1) $PRACTICE/part-*/index.md 의 본문 TODO 를 v2.md 에서 채우기"
echo "   2) (선택) hugo server 로 미리보기"
echo "   3) git commit -m \"Restructure: 투자 > 주식 > {이론, 실습} 시리즈\" && git push"
echo
echo "ℹ️  남은 옛 경로 참조 점검:"
grep -rn '/portfolio/investment-foundations/\|/portfolio/etf-dual-strategy' content 2>/dev/null || echo "   (없음 — 깨질 내부 링크 없음)"
