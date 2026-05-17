# SEO Content Rules — Agency Founder Finance

_Applies to all pages, blog posts and landing page copy on agencyfounderfinance.co.uk_

---

## 1. Audience First

Every page is written for one person: a founder of a UK-based agency who is responsible for the financial decisions in their business. They may be:

- A freelancer growing into an agency
- A director of a 2–20 person agency with £200k–£5m turnover
- A growth-stage founder preparing for exit, acquisition or investment
- A UAE-based UK founder managing cross-border obligations

Write to that founder directly. Use "you" and "your agency". Avoid generic "businesses" framing. Avoid talking down to readers or over-explaining basics they already know.

---

## 2. Search Intent Hierarchy

Match content format to intent:

| Intent | Format | Example |
|---|---|---|
| Commercial (C) | Landing page with clear CTA, service detail, trust signals | "Accountants for marketing agencies" |
| Local + Commercial (L, C) | Landing page with geographic relevance noted | "Digital agency accountants" with UK-wide framing |
| Informational (I) | Blog post with structured guide, FAQs, related links | "How to pay yourself as an agency founder" |
| Navigational (N) | Not targetted — those searches find brand directly | — |

Do not write a blog post for a commercial keyword. Do not write a commercial landing page for an informational keyword.

---

## 3. Page Structure (Blog Posts)

Every blog post must include:

- **Frontmatter:** title, slug, canonical, date, author, category, metaTitle, metaDescription, altText, h1, summary, faqs (minimum 4)
- **H1:** matches `h1` frontmatter field. May differ from meta title. Conversational, not keyword-stuffed.
- **Opening paragraph:** states what the post covers and who it is for within the first 40 words. No preamble.
- **H2 sections:** 4–8 per post. Each H2 should answer a distinct sub-question.
- **H3s within H2s:** optional, for posts covering multiple sub-points under one heading.
- **FAQs section:** minimum 4, maximum 8. Written as real questions agency founders ask. Pull from Google's "People also ask" and common client questions.
- **Internal links:** minimum 2 per post (one to a related blog post, one to a commercial or service page).
- **CTA:** every post ends with a lead capture CTA block before the related posts section.
- **Word count:** 900–1,800 words for standard posts. Technical guides (IR35, corporation tax) may reach 2,500. Do not pad.

---

## 4. Metadata Rules

**metaTitle:**
- 50–60 characters
- Format: `[Topic] | Agency Founder Finance`
- Include the primary keyword naturally
- Do not repeat the brand name mid-title

**metaDescription:**
- 140–155 characters
- Must describe the value the reader gets from the post
- Include a soft call to action where natural ("Find out what agency founders need to know about...")
- Do not repeat the meta title word-for-word

**h1:**
- Can differ from metaTitle — more conversational, longer if needed
- Never keyword-stuffed
- Must clearly signal the topic

**canonical:**
- Always set to the full URL: `https://www.agencyfounderfinance.co.uk/blog/[category]/[slug]`
- Must match the actual route exactly

---

## 5. Keyword Rules

- **One primary keyword per page** — write for it but do not over-repeat it
- **Variants welcome** — use related terms naturally (e.g., "agency accountant", "accounting for your agency", "agency finances") without forcing them
- **Do not keyword stuff headings** — H2s and H3s should be questions or clear statements, not keyword fragments
- **LSI terms encouraged** — mention related concepts (cash flow, management accounts, VAT, corporation tax, R&D) where they arise naturally
- **Do not create multiple pages for the same keyword cluster** — consolidate

---

## 6. Schema Requirements

Every blog post must have:

- `BlogPosting` JSON-LD: headline, description, image, datePublished, dateModified, author, publisher, mainEntityOfPage, articleSection, inLanguage: "en-GB"
- `BreadcrumbList` JSON-LD: matches the visible breadcrumb trail
- `FAQPage` JSON-LD: generated from frontmatter `faqs` array when present

Category pages must have:
- `CollectionPage` JSON-LD
- `BreadcrumbList` JSON-LD

Commercial landing pages must have:
- `Organization` or `LocalBusiness` JSON-LD (homepage)
- `Service` JSON-LD (service pages)
- `BreadcrumbList` where the page is nested

---

## 7. Breadcrumb Rules

- All blog posts: Home → Blog → [Category] → [Post title]
- Category pages: Home → Blog → [Category name]
- Service pages: Home → Services → [Service name]
- Agency type pages: Home → Agencies → [Agency type]
- Breadcrumb must match BreadcrumbList JSON-LD exactly
- Last item in breadcrumb is never a link (current page)

---

## 8. Internal Linking Rules

Full map in `internal-link-map.md`. Core rules:

- Every blog post links to at least one other blog post in the same category
- Every blog post links to at least one commercial or service page
- Agency-type posts (e.g., IR35 for creative agencies) link to the corresponding agency type landing page
- Commercial pages link to 2–3 relevant blog posts
- Category pages link to all posts in that category
- Blog index links to all categories and surfaces recent posts
- No orphan pages — every page must be reachable from at least two other pages

---

## 9. Content Accuracy Rules

- **Tax figures must include the tax year they apply to** (e.g., "2025/26 tax year")
- **HMRC thresholds, rates and deadlines must be verified** before publishing — do not rely on training data
- **No guaranteed tax savings claims** — use language like "can help reduce", "may be able to claim", "subject to eligibility"
- **No invented testimonials, case studies, client logos or awards**
- **No aggressive or misleading tax mitigation claims**
- **UAE content must acknowledge** that UAE tax advice requires specialist advice and that we provide UK tax guidance only

---

## 10. Tone and Voice

- **Authoritative but accessible** — we know this deeply, we explain it clearly
- **No jargon without explanation** — define terms on first use (e.g., "BADR (Business Asset Disposal Relief)")
- **No waffle** — get to the point within the first paragraph
- **Not corporate, not chatty** — somewhere between a trusted advisor and a sharp trade publication
- **UK English throughout** — "practise" not "practice", "recognised" not "recognized", "tax year" not "fiscal year"
- **Agency-relevant examples** — use agency-specific scenarios (retainer model, project billing, contractor mix, agency sale)

---

## 11. Content Update Protocol

- Posts mentioning tax rates, thresholds or deadlines must be reviewed and updated at the start of each new UK tax year (6 April)
- `dateModified` in frontmatter must be updated when content is materially changed
- Outdated posts should be updated in place — do not create duplicate updated posts
- MCP research log should be updated when keyword data is refreshed

---

## 12. Image and Alt Text Rules

- Blog posts should have a feature image (generated via OG image API if no real image is provided)
- `altText` in frontmatter must be descriptive and relevant (e.g., "Agency founder reviewing financial reports on laptop")
- Never use decorative alt text like "image", "photo", or generic stock photo descriptions
- Do not use images of people without license confirmation

---

## 13. FAQ Writing Rules

- 4–8 FAQs per blog post; 2–4 per landing page
- Questions must be questions agency founders actually ask (not generic)
- Answers: 40–120 words each — enough to be useful, short enough to scan
- FAQs feed the `FAQPage` JSON-LD schema automatically
- Do not write FAQ answers that contradict the main body of the post
