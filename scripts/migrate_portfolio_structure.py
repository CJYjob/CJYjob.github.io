from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "content" / "portfolio"
DST = ROOT / "content" / "ko" / "portfolio"

MAPPINGS = {
    "HowToStudy/7timesReading/index.md":
        "seven-times-reading.md",
    "english/grammar/gangseongtae-grammar/chapter-1/index.md":
        "english-grammar-chapter-01.md",
    "english/grammar/gangseongtae-grammar/chapter-2/index.md":
        "english-grammar-chapter-02.md",

    "investing/stock/theory/part-01-products-and-accounts/index.md":
        "investment-theory-01-products-and-accounts.md",
    "investing/stock/theory/part-02-market-structure/index.md":
        "investment-theory-02-market-structure.md",
    "investing/stock/theory/part-03-financial-statements/index.md":
        "investment-theory-03-financial-statements.md",
    "investing/stock/theory/part-04-company-analysis/index.md":
        "investment-theory-04-company-analysis.md",
    "investing/stock/theory/part-05-technical-indicators/index.md":
        "investment-theory-05-technical-indicators.md",
    "investing/stock/theory/part-06-derivatives-etf-mechanism/index.md":
        "investment-theory-06-derivatives-etf-mechanism.md",
    "investing/stock/theory/part-07-strategy-planning/index.md":
        "investment-theory-07-strategy-planning.md",
    "investing/stock/theory/part-08-rule-encoding/index.md":
        "investment-theory-08-rule-encoding.md",
    "investing/stock/theory/part-09-implementation-validation/index.md":
        "investment-theory-09-implementation-validation.md",
    "investing/stock/theory/part-10-automated-trading/index.md":
        "investment-theory-10-automated-trading.md",

    "investing/stock/strategy/part-01-foundation-and-edge/index.md":
        "investment-strategy-01-foundation-and-edge.md",
    "investing/stock/strategy/part-02-market-regimes/index.md":
        "investment-strategy-02-market-regimes.md",
    "investing/stock/strategy/part-03-regime-indicators/index.md":
        "investment-strategy-03-regime-indicators.md",
    "investing/stock/strategy/part-04-supply-demand/index.md":
        "investment-strategy-04-supply-demand.md",
    "investing/stock/strategy/part-05-etf-futures-cost/index.md":
        "investment-strategy-05-etf-futures-cost.md",
    "investing/stock/strategy/part-06-position-and-metrics/index.md":
        "investment-strategy-06-position-and-metrics.md",
    "investing/stock/strategy/part-07-risk-and-exceptions/index.md":
        "investment-strategy-07-risk-and-exceptions.md",
    "investing/stock/strategy/part-08-backtest-design/index.md":
        "investment-strategy-08-backtest-design.md",
    "investing/stock/strategy/appendix-summary/index.md":
        "investment-strategy-summary.md",
    "investing/stock/strategy/appendix-glossary/index.md":
        "investment-strategy-glossary.md",

    "investing/stock/practice/part-09-implementation/index.md":
        "investment-practice-09-implementation.md",
    "investing/stock/practice/part-10-backtest-engine/index.md":
        "investment-practice-10-backtest-engine.md",
    "investing/stock/practice/part-11-automation/index.md":
        "investment-practice-11-automation.md",
    "investing/stock/practice/part-12-live-and-review/index.md":
        "investment-practice-12-live-and-review.md",
}

OLD_TO_NEW = {
    f"/portfolio/{source[:-len('index.md')]}":
        f"/ko/portfolio/{target[:-3]}/"
    for source, target in MAPPINGS.items()
}

def split_front_matter(text):
    if not text.startswith("---\n"):
        raise ValueError("Front Matter not found")
    _, fm, body = text.split("---", 2)
    return fm.strip("\n"), body.lstrip("\n")

def replace_block(fm, key, lines):
    pattern = rf"(?ms)^{re.escape(key)}:\s*(?:\[[^\n]*\]|.*?(?=^[A-Za-z_][A-Za-z0-9_]*:|\Z))"
    replacement = key + ":\n" + "\n".join(f"  - {line}" for line in lines)
    if re.search(pattern, fm):
        return re.sub(pattern, replacement + "\n", fm).rstrip()
    return fm.rstrip() + "\n" + replacement

def set_scalar(fm, key, value):
    pattern = rf"(?m)^{re.escape(key)}:.*$"
    line = f"{key}: {value}"
    if re.search(pattern, fm):
        return re.sub(pattern, line, fm)
    return fm.rstrip() + "\n" + line

def remove_block(fm, key):
    pattern = rf"(?ms)^{re.escape(key)}:\s*(?:\[[^\n]*\]|.*?(?=^[A-Za-z_][A-Za-z0-9_]*:|\Z))"
    return re.sub(pattern, "", fm).strip()

def extract_existing_tags(fm):
    m = re.search(r"(?ms)^tags:\s*(\[[^\n]*\]|.*?(?=^[A-Za-z_][A-Za-z0-9_]*:|\Z))", fm)
    if not m:
        return []
    block = m.group(1).strip()

    if block.startswith("["):
        return [
            x.strip().strip("'\"")
            for x in block[1:-1].split(",")
            if x.strip()
        ]

    return [
        line.strip()[1:].strip().strip("'\"")
        for line in block.splitlines()
        if line.strip().startswith("-")
    ]

def unique(values):
    result = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result

def old_url(source):
    return f"/portfolio/{source[:-len('index.md')]}"

def normalized_metadata(source, fm):
    tags = extract_existing_tags(fm)

    tags = [t for t in tags if t != "Portfolio"]

    if source.startswith("HowToStudy/"):
        categories = ['"Learning Methods"']
        tags = unique(["Learning Methods", "Reading", "7 Times Reading"] + tags)
        series = None

    elif source.startswith("english/"):
        categories = ['"English"']
        tags = [
            "Gangseongtae" if t == "강성태 영문법" else t
            for t in tags
            if t != "Portfolio"
        ]
        tags = unique(["English", "Grammar", "Gangseongtae"] + tags)
        series = "English Grammar"

    elif source.startswith("investing/stock/theory/"):
        categories = ['"Investment"']
        tags = unique(["Investment", "Theory", "Stock"] + tags)
        series = "Investment Theory"

    elif source.startswith("investing/stock/strategy/"):
        categories = ['"Investment"']
        tags = unique(["Investment", "Strategy", "Stock"] + tags)
        series = "Investment Strategy"

    elif source.startswith("investing/stock/practice/"):
        categories = ['"Investment"']
        tags = unique(["Investment", "Practice", "Stock"] + tags)
        series = "Investment Practice"

    else:
        raise ValueError(f"Unclassified source: {source}")

    return categories, tags, series

def migrate_one(source, target):
    source_path = SRC / source
    target_path = DST / target

    text = source_path.read_text(encoding="utf-8")
    fm, body = split_front_matter(text)

    categories, tags, series = normalized_metadata(source, fm)

    fm = replace_block(fm, "categories", categories)
    fm = replace_block(fm, "tags", [f'"{x}"' for x in tags])

    if series:
        fm = replace_block(fm, "series", [f'"{series}"'])
    else:
        fm = remove_block(fm, "series")

    fm = replace_block(fm, "aliases", [old_url(source)])

    body = body.replace(
        " 교재 예문 전체를 그대로 전재하지 않고, "
        "학습 과정에서 확인한 ",
        " 학습 과정에서 확인한 "
    )

    for old, new in OLD_TO_NEW.items():
        body = body.replace(old, new)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(
        f"---\n{fm.strip()}\n---\n\n{body}",
        encoding="utf-8",
        newline="\n",
    )

def copy_special_pages():
    source = SRC / "investing" / "_index.md"
    target = DST / "investment-overview.md"
    text = source.read_text(encoding="utf-8")
    fm, body = split_front_matter(text)
    fm = replace_block(fm, "categories", ['"Investment"'])
    tags = unique(["Investment", "Overview"] + extract_existing_tags(fm))
    fm = replace_block(fm, "tags", [f'"{x}"' for x in tags if x != "Portfolio"])
    fm = replace_block(fm, "aliases", ["/portfolio/investing/"])

    for old, new in OLD_TO_NEW.items():
        body = body.replace(old, new)

    target.write_text(
        f"---\n{fm.strip()}\n---\n\n{body}",
        encoding="utf-8",
        newline="\n",
    )

    source = SRC / "workout" / "index.md"
    target = DST / "workout.md"
    text = source.read_text(encoding="utf-8")
    fm, body = split_front_matter(text)
    fm = replace_block(fm, "categories", ['"Workout"'])
    tags = unique(["Workout"] + extract_existing_tags(fm))
    fm = replace_block(fm, "tags", [f'"{x}"' for x in tags if x != "Portfolio"])
    fm = replace_block(fm, "aliases", ["/portfolio/workout/"])
    target.write_text(
        f"---\n{fm.strip()}\n---\n\n{body}",
        encoding="utf-8",
        newline="\n",
    )

def main():
    DST.mkdir(parents=True, exist_ok=True)

    for source, target in MAPPINGS.items():
        migrate_one(source, target)

    copy_special_pages()

    print(f"Migrated {len(MAPPINGS) + 2} Portfolio content files.")

if __name__ == "__main__":
    main()
