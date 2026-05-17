/**
 * Newsletter subscriber storage (Supabase via REST, server-side only).
 *
 * Table schema (run once in Supabase SQL editor, see supabase/newsletter_schema.sql):
 *
 *   create table public.newsletter_subscribers (
 *     id uuid primary key default gen_random_uuid(),
 *     email text not null unique,
 *     agency_type text,
 *     status text not null default 'pending'
 *       check (status in ('pending','confirmed','unsubscribed','complained','bounced')),
 *     source text,
 *     source_url text,
 *     subscribed_at timestamptz not null default now(),
 *     confirmed_at timestamptz,
 *     unsubscribed_at timestamptz,
 *     welcome_step_sent int not null default 0,
 *     last_step_at timestamptz,
 *     resend_contact_id text,
 *     metadata jsonb
 *   );
 *   create index on public.newsletter_subscribers (status);
 *   create index on public.newsletter_subscribers (welcome_step_sent, last_step_at)
 *     where status = 'confirmed';
 *
 * All access in this module is via service-role key, never exposed to browser.
 */

export type SubscriberStatus =
  | "pending"
  | "confirmed"
  | "unsubscribed"
  | "complained"
  | "bounced";

export interface Subscriber {
  id: string;
  email: string;
  agency_type: string | null;
  status: SubscriberStatus;
  source: string | null;
  source_url: string | null;
  subscribed_at: string;
  confirmed_at: string | null;
  unsubscribed_at: string | null;
  welcome_step_sent: number;
  last_step_at: string | null;
  resend_contact_id: string | null;
}

function config() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) {
    throw new Error(
      "Supabase newsletter storage requires NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY",
    );
  }
  return { url: url.replace(/\/$/, ""), key };
}

async function req<T = unknown>(
  path: string,
  init: RequestInit & { prefer?: string } = {},
): Promise<T> {
  const { url, key } = config();
  const headers: Record<string, string> = {
    apikey: key,
    Authorization: `Bearer ${key}`,
    "Content-Type": "application/json",
  };
  if (init.prefer) headers["Prefer"] = init.prefer;
  const res = await fetch(`${url}/rest/v1${path}`, {
    ...init,
    headers: { ...headers, ...(init.headers as Record<string, string> | undefined) },
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Supabase ${res.status}: ${text}`);
  }
  if (res.status === 204) return undefined as unknown as T;
  return (await res.json()) as T;
}

export async function upsertPending(input: {
  email: string;
  agencyType?: string;
  source?: string;
  sourceUrl?: string;
}): Promise<void> {
  const payload = {
    email: input.email.trim().toLowerCase(),
    agency_type: input.agencyType ?? null,
    source: input.source ?? null,
    source_url: input.sourceUrl ?? null,
    status: "pending",
  };
  await req("/newsletter_subscribers?on_conflict=email", {
    method: "POST",
    body: JSON.stringify(payload),
    prefer: "resolution=merge-duplicates,return=minimal",
  });
}

export async function getByEmail(email: string): Promise<Subscriber | null> {
  const list = await req<Subscriber[]>(
    `/newsletter_subscribers?email=eq.${encodeURIComponent(email.toLowerCase())}&select=*&limit=1`,
  );
  return list[0] ?? null;
}

export async function markConfirmed(email: string, resendContactId?: string): Promise<void> {
  const body: Record<string, unknown> = {
    status: "confirmed",
    confirmed_at: new Date().toISOString(),
  };
  if (resendContactId) body.resend_contact_id = resendContactId;
  await req(
    `/newsletter_subscribers?email=eq.${encodeURIComponent(email.toLowerCase())}`,
    {
      method: "PATCH",
      body: JSON.stringify(body),
      prefer: "return=minimal",
    },
  );
}

export async function markUnsubscribed(email: string): Promise<void> {
  await req(
    `/newsletter_subscribers?email=eq.${encodeURIComponent(email.toLowerCase())}`,
    {
      method: "PATCH",
      body: JSON.stringify({
        status: "unsubscribed",
        unsubscribed_at: new Date().toISOString(),
      }),
      prefer: "return=minimal",
    },
  );
}

export async function advanceWelcomeStep(email: string, step: number): Promise<void> {
  await req(
    `/newsletter_subscribers?email=eq.${encodeURIComponent(email.toLowerCase())}`,
    {
      method: "PATCH",
      body: JSON.stringify({
        welcome_step_sent: step,
        last_step_at: new Date().toISOString(),
      }),
      prefer: "return=minimal",
    },
  );
}

export async function findReadyForNextStep(currentStep: number, hoursSinceLast: number): Promise<Subscriber[]> {
  const cutoff = new Date(Date.now() - hoursSinceLast * 60 * 60 * 1000).toISOString();
  const q = new URLSearchParams({
    status: "eq.confirmed",
    welcome_step_sent: `eq.${currentStep}`,
    or: `(last_step_at.lte.${cutoff},and(welcome_step_sent.eq.0,confirmed_at.lte.${cutoff}))`,
    select: "*",
    limit: "100",
  });
  return await req<Subscriber[]>(`/newsletter_subscribers?${q.toString()}`);
}
