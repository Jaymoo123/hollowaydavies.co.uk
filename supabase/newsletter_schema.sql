-- Newsletter subscriber storage for Agency Founder Finance.
-- Run once in the Supabase SQL editor (or via supabase db push).

create extension if not exists pgcrypto;

create table if not exists public.newsletter_subscribers (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  agency_type text,
  status text not null default 'pending'
    check (status in ('pending', 'confirmed', 'unsubscribed', 'complained', 'bounced')),
  source text,
  source_url text,
  subscribed_at timestamptz not null default now(),
  confirmed_at timestamptz,
  unsubscribed_at timestamptz,
  welcome_step_sent int not null default 0,
  last_step_at timestamptz,
  resend_contact_id text,
  metadata jsonb
);

create index if not exists newsletter_subscribers_status_idx
  on public.newsletter_subscribers (status);

create index if not exists newsletter_subscribers_drip_idx
  on public.newsletter_subscribers (welcome_step_sent, last_step_at)
  where status = 'confirmed';

-- Row-level security: lock the table down. All writes happen via the
-- service-role key from the Next.js API routes; the public anon key
-- gets no access.
alter table public.newsletter_subscribers enable row level security;

revoke all on public.newsletter_subscribers from anon, authenticated;

-- Helpful view for the welcome drip cron (optional).
create or replace view public.newsletter_drip_queue as
  select id, email, welcome_step_sent, confirmed_at, last_step_at
  from public.newsletter_subscribers
  where status = 'confirmed'
  order by confirmed_at;
