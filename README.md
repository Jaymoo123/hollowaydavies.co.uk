# Holloway Davies

UK generalist accountancy lead-gen site. ICAEW chartered accountants for limited companies, contractors, sole traders, partnerships and small businesses. National coverage, fixed fees.

Production: https://www.hollowaydavies.co.uk

## Structure

```
generalist/
├── web/                Next.js 15 App Router site (Vercel deploy root)
├── pipeline/           Python content + SEO automation (DeepSeek, Supabase, Pexels, IndexNow)
├── scripts/            One-off Node/Python helpers (brand assets, PDF templates, illustrations)
├── seo-research/       Keyword + competitor research outputs (CSVs, briefs)
├── supabase/           Per-niche SQL: newsletter_subscribers, blog_topics_generalist
└── niche.config.json   Brand, nav, footer, lead form schema (loaded at runtime by web/)
```

## Web app

```
cd web
npm install
npm run dev      # http://localhost:3000
npm run build    # production build
```

Required env vars in `web/.env.local`:

- `NEXT_PUBLIC_SITE_URL` — canonical domain (no trailing slash)
- `NEXT_PUBLIC_SUPABASE_URL` + `NEXT_PUBLIC_SUPABASE_ANON_KEY` — lead form writes
- `SUPABASE_SERVICE_ROLE_KEY` — newsletter subscriber writes (server-side only)
- `RESEND_*` — optional; if absent, newsletter signups are stored as `confirmed` directly

## Content pipeline

Bulk blog generation runs against Supabase queue (`blog_topics_generalist`):

```
python pipeline/bulk_generate.py
python pipeline/fix_cannibalisation.py
python pipeline/quality_spotcheck.py
```

City pages, glossary, guides, industry verticals and comparison pages each have their own generator under `pipeline/`.

## Editorial

- Author byline: Emma Carter (Editorial Lead)
- Technical reviewer byline: James Holloway, ICAEW Chartered Accountant
- Every published article carries the reviewer credit and an editorial-content disclosure
- Concrete tax advice is delivered via book-a-call with a qualified accountant on the partner team, never via published articles

## Lead form

Posts to Supabase `leads` table with `source: "general"`. The leads table has a CHECK constraint that must include `'general'` in its allowlist (see `supabase/` migrations).

## Deployment

Vercel project root: `web/`. Framework preset must be set to Next.js explicitly via API or all routes silently 404.
