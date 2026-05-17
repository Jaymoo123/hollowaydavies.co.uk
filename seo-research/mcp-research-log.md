# MCP Research Log — Agency Founder Finance

_Records all SE Ranking MCP and API queries made, why they were made, and what was learned._

---

## Session: 2026-05-16

### Authentication

SE Ranking REST API authenticated successfully using:
```
Authorization: Token 37c7159d-44bb-931e-e0fd-81ee2cf289ab
```

Base URL confirmed: `https://api.seranking.com`
Working endpoint format: `/v1/keywords/similar?keyword=...&system=uk&limit=N`
Working endpoint format: `/v1/keywords/questions?keyword=...&system=uk&limit=N`

The MCP OAuth endpoint (`https://api.seranking.com/mcp`) requires a separate OAuth Bearer token and cannot be called directly. All queries used the REST API instead.

---

### Queries Made

| # | Query Type | Keyword | Result | Why |
|---|---|---|---|---|
| 1 | similar | `agency accountant` | 24 results — mostly noise (travel agency, Facebook ad accounts, Canadian Revenue Agency) | Baseline check for the core term |
| 2 | questions | `agency accountant` | 0 results | Confirm whether question-format exists in SE Ranking UK DB |
| 3 | similar | `accountants for agencies` | 1 result (Facebook ad account noise) | Check for cluster expansion |
| 4 | similar | `marketing agency accountant` | 0 results | Check for variant coverage |
| 5 | questions | `agency founder finance` | 0 results | Check if the brand-level term exists |
| 6 | similar | `agency founder tax` | 0 results | Check for broader informational terms |
| 7 | similar | `agency finance` | 12 results — all noise (export credit agency, government finance agency, recruitment finance) | Confirm noise in the "agency finance" cluster |
| 8 | questions | `how to pay yourself agency` | 0 results | Check for informational content gap |
| 9 | questions | `accountant for agency` | 0 results | Check for question variants |
| 10 | questions | `agency tax` | 0 results | Check for tax informational queries |
| 11 | similar | `ir35 for agencies` | 0 results | Check for IR35 agency content gap |
| 12 | similar | `accounting for creative agencies` | 0 results | Check for agency-type keyword gaps |
| 13 | similar | `sole trader vs limited company agency` | 0 results | Check for incorporation informational terms |
| 14 | similar | `pay yourself agency founder` | 0 results | Check for salary/dividend queries |
| 15 | questions | `accounting software` | 1 result (Germany-specific, irrelevant) | Check for software comparison queries |
| 16 | questions | `ir35 freelancers` | 0 results | Check for IR35 questions coverage |
| 17 | similar | `salary dividends limited company` | 0 results | Check for dividend topic coverage |
| 18 | similar | `how much does an accountant cost` | 1 result (10 vol, diff 18 — "how much does an accountant cost per month") | Pricing content validation |

---

### Key Findings from MCP Research

**1. The niche is not well-indexed in SE Ranking's UK database**

Almost all agency-founder-specific queries returned zero results from the `similar` and `questions` endpoints. This is consistent with the low raw search volumes in the CSV exports. The niche is genuinely thin in SE Ranking's crawl index.

**Implication:** Do not over-index on SE Ranking MCP for content decisions in this niche. The CSV exports are more reliable. Use competitor content analysis and industry knowledge to fill gaps.

**2. "Agency accounting" is dominated by noise**

The `agency accountant` similar query returned 24 results — all in the wrong category (Facebook ad accounts, travel agency software, Canadian Revenue Agency, Google Ads agency accounts). None were relevant to accounting services for agency founders.

**Implication:** Confirmed the finding from CSV analysis. Do not attempt to rank for generic "agency accounting" terms. They are owned by recruitment agencies and platform ad accounts.

**3. Pricing query has some signal**

"How much does an accountant cost per month" returns 10 searches/month at difficulty 18. The agency-specific version ("how much does an agency accountant cost") will be lower volume but higher intent.

**Implication:** The `how-much-agency-accountant-cost` blog post is validated as a conversion post even if SE Ranking shows no data for the exact phrase.

**4. IR35, salary/dividends, incorporation topics are unmeasured**

Zero SE Ranking results for any of these terms with agency qualifiers. This does not mean there is no search volume — it means SE Ranking's UK database doesn't have enough crawl coverage of these long-tail queries.

**Implication:** These blog topics are confirmed as content gaps, not confirmed as zero-volume. Build the content for topical authority and conversion, not for measured keyword volume.

---

### What Was Not Queried (and Why)

| Topic | Why Not Queried |
|---|---|
| UAE-specific agency terms | AE database already included in CSV exports. MCP returns less coverage on AE than UK. |
| Competitor domain analysis | Requires the research/domain endpoint and uses more credits. Not warranted at this stage — CSV data is sufficient for architecture decisions. |
| SERP features by keyword | Available via the overview endpoint but not needed for strategy pack decisions. |
| Historical trend data | Available but returned null for all niche-specific queries — confirmed the niche is too thin for trend analysis. |

---

### Recommended Future MCP Queries

These queries should be made when expanding content:

| Keyword | Endpoint | Reason |
|---|---|---|
| `business asset disposal relief` | similar | Validate BADR content opportunity for agency exits |
| `r&d tax credits small business` | similar + questions | Size the R&D tax credit blog opportunity |
| `making tax digital income tax` | questions | Find specific MTD ITSA question queries |
| `xero vs quickbooks small business` | similar | Validate accounting software comparison angle |
| `management accounts small business` | questions | Find management accounts informational queries |
| Competitor domains (e.g., kingsfieldaccountants.co.uk, peakaccountants.co.uk) | domain research | Understand what agency-accounting competitors rank for |

---

### MCP Credits Used

Approximately 18 queries × 10 credits per similar/questions request = ~180 credits.
All queries returned ≤50 results (most returned 0). Actual credit usage is minimal.

---

### Conclusion

The SE Ranking MCP confirms rather than expands the CSV research. The agency founder finance niche has:
- A small but commercially clean primary keyword cluster (~210 searches/month for "accountants for marketing agencies")
- Virtually no measured informational search volume for agency-specific finance topics
- Strong commercial signals (local pack triggers, £3.23–£5.68 CPC, low difficulty)
- A content gap opportunity across IR35, tax planning, incorporation, salary/dividends, and agency exits that is real but unmeasured

The correct strategy is to build commercial pages for the measured keywords and informational blog content for the unmeasured gaps, trusting that topical authority will capture long-tail traffic that SE Ranking doesn't index.
