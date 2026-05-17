-- Health check submissions for Agency Founder Finance.
-- Run once in the Supabase SQL editor.

create extension if not exists pgcrypto;

create table if not exists public.health_check_submissions (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  name text not null,
  company text,
  agency_type text not null,
  revenue_band text not null,
  entity text not null,
  profit_pretax bigint not null default 0,
  current_salary bigint not null default 0,
  current_dividend bigint not null default 0,
  rd_activity text not null,
  contractor_use text not null,
  international jsonb not null default '[]'::jsonb,
  exit_horizon text not null,
  top_concern text,
  opportunities jsonb not null default '[]'::jsonb,
  ip_hash text,
  user_agent text,
  submitted_at timestamptz not null default now()
);

create index if not exists health_check_submissions_email_idx
  on public.health_check_submissions (email);

create index if not exists health_check_submissions_submitted_idx
  on public.health_check_submissions (submitted_at desc);

alter table public.health_check_submissions enable row level security;
revoke all on public.health_check_submissions from anon, authenticated;
