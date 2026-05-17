"""
Mine the SE Ranking keyword CSVs for new blog-topic candidates.

Outputs seo-research/keyword-candidates.csv with scored, categorised candidates
that are not already in blog-ideas.csv.

Run:
    python pipeline/mine_keywords.py
"""
import csv
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from seed_topics import load_rows

ROOT = Path(__file__).resolve().parents[1]


NOISE_TOKENS = [
    "recruit", "employment agenc", "jobs", "job ", "careers", "temp ",
    "temping", "staffing", "temps", "staff agenc", "hiring agenc",
    "placement agenc", "personnel agenc", "temporary agenc", "accounting temp",
    "canada", "canadian", "cra ", " cra", "cra-", "cra.", "irs ",
    "sign in", "login", "logon", "helpline", "phone number",
    "agency theory", "theory in accounting", "theory in management",
    "agency research", "agency dilemma",
    "agency fund", "governmental accounting", "government agencies",
    "agency accounting identifier", "standard accounting system",
    "accounting treatment for agency",
    "accountancy agenc", "accounting agenc",
    "credit agenc", "collection agenc", "debt collect", "estate agenc",
    "real estate", "rental agenc", "lettings agenc", "travel agenc", "tour agenc",
    "insurance agenc", "care agenc",
    "account manager", "account executive", "account director", "account planner",
    "account handler", "account-based", "account based marketing", "account based",
    "b2b account", "role of account", "what does an account", "what is an account manager",
    "manager do at", "manager at an", "account manager salary", "executive salary",
    "account planning", "account servicing", "account team",
    "account number", "account login", "account access",
    "how to become", "interview question", "degree", "university", "course",
    "career path", "salary survey", "wage", "pay rate",
    "media buying", "programmatic",
    "merchant account", "escrow", "bank account", "savings account", "current account",
]


RELEVANT_TOKENS = [
    "accountant", "accountancy", "accounting", "tax", "vat", "ir35",
    "r&d ", "r and d ", "rd tax", "sdlt",
    "corporation tax", "self assessment", "self-assessment",
    "self employed", "self-employed",
    "making tax digital", "mtd", "dividend", "salary", "paye", "badr",
    "entrepreneur", "incorporat", "limited compan", "sole trader", "holding company",
    "cash flow", "profit", "margin", "p&l", "financ", "bookkeep", "payroll",
    "exit ", "selling", "buy out", "buyout", "mbo ", "m&a", "goodwill",
    "cis ", "p11d", "p60", "p45", "national insurance", "pension",
    "capital allowance", "capital gains", "cgt", "seis", "eis", "annual investment",
    "invoic", "retainer", "utilisation", "utilization", "billable", "revenue per",
]


AGENCY_CTX_TOKENS = [
    "agenc", "founder", "marketing", "creative", "advertising", "digital",
    "pr ", "public relations", "web design", "web dev", "seo ", "ppc ",
    "social media", "branding", "design", "production", "media ",
    "communications", "ad ", "ads ", "adv ",
    "ltd", "self employed",
]


CATEGORY_RULES = [
    ("Tax and Compliance", ["vat", "corporation tax", "self assessment",
                            "self-assessment", "hmrc", "paye", "p11d", "p60",
                            "national insurance", "cis"]),
    ("Salary and Dividends", ["salary", "dividend", "pension", "remuneration"]),
    ("Incorporation and Structure", ["incorporat", "limited compan",
                                     "sole trader", "holding company", "ltd "]),
    ("Growth and Exit", ["exit", "selling", "buy out", "buyout", "mbo",
                         "m&a", "goodwill", "badr", "entrepreneur",
                         "seis", "eis"]),
    ("Contractors and IR35", ["ir35", "contractor", "freelancer",
                              "off-payroll", "off payroll"]),
    ("Making Tax Digital", ["mtd", "making tax digital"]),
    ("International Agencies", ["dubai", "uae", "overseas", "offshore",
                                "non-dom", "non resident", "non-resident",
                                "international"]),
    ("Agency Accountant Services", ["accountant for", "specialist accountant",
                                    "choose an accountant", "find an accountant",
                                    "agency accountant", "agency accountants"]),
    ("Agency Finance Essentials", ["cash flow", "margin", "profit", "p&l",
                                   "bookkeep", "accounting software", "financ",
                                   "invoic", "retainer", "utilisation",
                                   "billable", "revenue per", "payroll"]),
]


def is_noise(kw):
    return any(t in kw for t in NOISE_TOKENS)


def is_relevant(kw):
    return any(t in kw for t in RELEVANT_TOKENS)


def is_agency_ctx(kw):
    return any(t in kw for t in AGENCY_CTX_TOKENS)


def categorise(kw):
    for cat, tokens in CATEGORY_RULES:
        if any(t in kw for t in tokens):
            return cat
    return "Agency Finance Essentials"


def score(d):
    s = d["vol"] or 0
    if d["diff"] is not None:
        s += max(0, 30 - d["diff"]) * 5
    if d["intent"]:
        if "C" in d["intent"]:
            s += 30
        if "I" in d["intent"]:
            s += 10
        if "L" in d["intent"]:
            s += 5
    return s


def load_all_keywords():
    out = {}
    for f in sorted(os.listdir(ROOT)):
        if not f.startswith("export_research_") or not f.endswith(".csv"):
            continue
        market = "uk" if "_uk_" in f else "ae"
        with (ROOT / f).open(encoding="utf-8-sig") as h:
            for row in csv.DictReader(h):
                kw = (row.get("Keyword") or "").strip().lower()
                if not kw:
                    continue
                try:
                    vol = int(row.get("Search vol.", "").strip())
                except ValueError:
                    vol = 0
                try:
                    diff = int(row.get("Difficulty", "").strip())
                except ValueError:
                    diff = None
                d = {
                    "vol": vol,
                    "diff": diff,
                    "intent": (row.get("Search intent") or "").strip(),
                    "cpc": (row.get("CPC") or "").strip(),
                    "market": market,
                    "keyword": kw,
                }
                if kw not in out or vol > out[kw]["vol"]:
                    out[kw] = d
    return out


def main():
    all_kw = load_all_keywords()
    print(f"Total unique keywords in CSVs: {len(all_kw)}")

    relevant = {k: v for k, v in all_kw.items()
                if not is_noise(k) and is_relevant(k) and is_agency_ctx(k)}
    print(f"After filter (noise + audience + agency ctx): {len(relevant)}")

    rows, _ = load_rows(ROOT / "seo-research" / "blog-ideas.csv")
    existing = set((r.get("primary_keyword") or "").lower().strip() for r in rows)
    print(f"Existing primary keywords: {len(existing)}")

    candidates = [v for k, v in relevant.items()
                  if k not in existing
                  and (v["diff"] is None or v["diff"] <= 40)]
    for c in candidates:
        c["suggested_category"] = categorise(c["keyword"])
    candidates.sort(key=score, reverse=True)

    print(f"\nFinal candidates: {len(candidates)}\n")

    dist = Counter(c["suggested_category"] for c in candidates[:80])
    print("Top 80 by suggested category:")
    for cat in sorted(dist.keys()):
        print(f"  {dist[cat]:>3}  {cat}")
    print()
    print("Top 25:")
    print(f"{'score':>6} {'vol':>5} {'diff':>4} {'intent':<10} {'category':<32} keyword")
    print("-" * 120)
    for d in candidates[:25]:
        diff = d["diff"] if d["diff"] is not None else "?"
        print(f"{score(d):>6} {d['vol']:>5} {diff:>4} {d['intent'][:10]:<10} "
              f"{d['suggested_category']:<32} {d['keyword']}")

    out_path = ROOT / "seo-research" / "keyword-candidates.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["score", "keyword", "suggested_category", "volume",
                    "difficulty", "intent", "cpc", "market"])
        for d in candidates:
            w.writerow([score(d), d["keyword"], d["suggested_category"],
                        d["vol"], d["diff"] or "", d["intent"], d["cpc"], d["market"]])
    print(f"\nWritten {len(candidates)} candidates to {out_path}")


if __name__ == "__main__":
    main()
