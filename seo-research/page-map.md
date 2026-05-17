# Page Map — Agency Founder Finance

_agencyfounderfinance.co.uk_

---

## Architecture Overview

The site follows a three-tier structure:

1. **Commercial pages** — targeting founders at the point of hiring an accountant
2. **Blog category pages** — thematic hubs linking to blog posts
3. **Blog posts** — informational content targeting long-tail queries and building topical authority

The Property Tax Partners project is the structural reference for the blog system (category → post routing, schema, breadcrumbs, search, related posts).

---

## Tier 1 — Commercial Pages

### `/` — Homepage

- **Primary keyword:** accountants for marketing agencies (210/mo, diff 2, £3.23 CPC)
- **Supporting keywords:** accountants for agencies, accountant for marketing agency, accounting for marketing agencies
- **Purpose:** Primary lead generation page. Positions Agency Founder Finance as the specialist accountant for founders of any UK agency.
- **Key content:** Value proposition, agency types served, services overview, lead capture form, social proof/trust signals
- **Schema:** Organization, LocalBusiness (if applicable)

### `/services/` — Services Overview

- **Purpose:** Lists core services: bookkeeping, management accounts, tax planning, payroll, year-end accounts, VAT returns, R&D tax credits
- **Schema:** Service listing / ItemList

### `/services/accounting-for-agencies/` — Core Service Page

- **Primary keyword:** accounting for marketing agencies / accountants for marketing agencies
- **Purpose:** Deeper commercial page explaining what the service includes, who it is for, pricing signals, process
- **Schema:** Service

### `/services/tax-planning/` — Tax Planning for Agencies

- **Purpose:** Director salary/dividends, corporation tax, R&D, VAT — framed for agency founders
- **Schema:** Service

### `/services/management-accounts/` — Management Accounts

- **Purpose:** Monthly/quarterly reporting, KPI dashboards, cash flow forecasting for agencies
- **Schema:** Service

### `/services/r-and-d-tax-credits/` — R&D Tax Credits

- **Purpose:** Many digital/tech/AI agencies qualify. Underserved topic in the competitor landscape.
- **Schema:** Service

---

## Tier 1 — Agency Type Landing Pages

These pages target founders of specific agency types and map to the Cluster 2 keywords. Each page explains the specific accounting challenges and opportunities for that agency type.

| URL | Primary Target | Vol | Diff |
|---|---|---|---|
| `/agencies/marketing-agencies/` | accountants for marketing agencies | 210 | 2 |
| `/agencies/creative-agencies/` | accountants for creative agencies | 50 | 10 |
| `/agencies/advertising-agencies/` | accountants for advertising agencies | 50 | 5 |
| `/agencies/digital-agencies/` | accountants for digital agencies | 10 | 2 |
| `/agencies/pr-agencies/` | (gap — build proactively) | — | — |
| `/agencies/web-design-agencies/` | (gap — build proactively) | — | — |
| `/agencies/seo-agencies/` | (gap — build proactively) | — | — |
| `/agencies/recruitment-agencies/` | accountants for recruitment agencies (90/mo, diff 11, £4.77 CPC) | 90 | 11 |

**Notes:**
- Recruitment agencies accountants (90/mo, £4.77 CPC) is notably the highest-volume agency-type keyword after marketing. Worth a dedicated page.
- PR, branding, web design, SEO, social media, content — build proactively even without keyword data. Topical authority requires breadth.
- All agency type pages link back to the core `/services/accounting-for-agencies/` page and the blog.

---

## Tier 1 — Supporting Pages

| URL | Purpose |
|---|---|
| `/about/` | Team, credentials, who we are, why we specialise in agencies |
| `/contact/` | Contact form and lead capture |
| `/thank-you/` | Post-form-submission confirmation |
| `/privacy-policy/` | Legal |
| `/terms/` | Legal |
| `/cookie-policy/` | Legal |

---

## Tier 2 — Blog Category Pages

These are hub pages, each with an intro section and a grid of blog posts in that category. Following the Property Tax Partners pattern of hardcoded category pages with a dynamic fallback.

| URL | Category Name | Rationale |
|---|---|---|
| `/blog/` | Blog index | Search, sort, pagination across all posts |
| `/blog/agency-finance-essentials/` | Agency Finance Essentials | Core financial literacy for agency founders |
| `/blog/tax-and-compliance/` | Tax & Compliance | Corporation tax, VAT, self-assessment, deadlines |
| `/blog/salary-and-dividends/` | Salary, Dividends & Profit | Paying yourself optimally as a founder |
| `/blog/incorporation-and-structure/` | Incorporation & Business Structure | Ltd vs sole trader, holding companies, FIC for agencies |
| `/blog/growth-and-exit/` | Growing & Exiting Your Agency | Funding, selling, MBOs, tax on agency sale |
| `/blog/contractors-and-ir35/` | Contractors & IR35 | Staffing agencies, freelancer engagements, IR35 rules |
| `/blog/agency-accountant-services/` | Agency Accountant Services | What to look for, how we work, fees, comparisons |
| `/blog/making-tax-digital/` | Making Tax Digital | MTD ITSA, MTD VAT for agency businesses |
| `/blog/international-agencies/` | International & UAE Agencies | Cross-border, UAE, non-dom, dual-market agencies |

Full rationale in `blog-taxonomy.md`.

---

## Tier 3 — Blog Posts

Individual posts live at `/blog/[category]/[slug]/`.

Targeting approximately 40–60 posts at launch. See `blog-ideas.csv` for the full list.

Sample slugs:
- `/blog/agency-finance-essentials/agency-founder-finance-basics/`
- `/blog/tax-and-compliance/vat-for-marketing-agencies/`
- `/blog/salary-and-dividends/how-to-pay-yourself-as-agency-founder/`
- `/blog/incorporation-and-structure/sole-trader-vs-limited-company-agency/`
- `/blog/contractors-and-ir35/ir35-agency-contractors-uk/`

---

## URL Structure Rules

- All slugs lowercase, hyphenated, no trailing slash inconsistency
- Agency type pages use `/agencies/[type]/` not `/services/[type]/` to distinguish them from the services section
- Blog follows Property Tax Partners convention: `/blog/[category-slug]/[post-slug]/`
- No flat `/blog/[slug]/` routes at launch — use nested structure from day one to avoid the redirect debt that Property Tax Partners had to resolve
- Canonical URLs in frontmatter must match actual route

---

## Routing Notes (for implementation)

- Middleware: not needed at launch (no legacy slugs to redirect)
- Category slugs must match the `slugifyCategory()` output from `lib/blog.ts`
- 9 hardcoded category page files + dynamic `[slug]` fallback (mirrors Property Tax Partners pattern)
- niche.config.json to drive brand, nav, footer, CTA copy — allows future multi-niche reuse

---

## Internal Linking Priority

See `internal-link-map.md` for the full internal link strategy.
