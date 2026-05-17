import { NextResponse, type NextRequest } from "next/server";
import crypto from "crypto";

export const runtime = "nodejs";

/**
 * Resend webhook handler.
 *
 * Receives email lifecycle events from Resend (delivered, bounced, complained,
 * etc) and updates newsletter_subscribers status so we stop sending to
 * addresses that bounce or mark us as spam. This protects sender reputation.
 *
 * Configure in Resend dashboard:
 *   - Endpoint URL: https://www.hollowaydavies.co.uk/api/resend/webhook
 *   - Events: email.delivered, email.bounced, email.complained, email.delivery_delayed
 *   - Copy the signing secret (starts with `whsec_`) into
 *     RESEND_WEBHOOK_SECRET in Vercel env vars.
 *
 * Resend uses Svix to sign webhooks. We verify the signature here using
 * standard HMAC SHA-256, no `svix` npm package needed.
 */

type ResendEvent =
  | "email.sent"
  | "email.delivered"
  | "email.delivery_delayed"
  | "email.complained"
  | "email.bounced"
  | "email.opened"
  | "email.clicked";

interface ResendPayload {
  type: ResendEvent;
  created_at?: string;
  data?: {
    email_id?: string;
    from?: string;
    to?: string | string[];
    subject?: string;
    [key: string]: unknown;
  };
}

function verifySvixSignature(
  secret: string,
  headers: Headers,
  body: string,
): boolean {
  const id = headers.get("svix-id");
  const ts = headers.get("svix-timestamp");
  const sig = headers.get("svix-signature");

  if (!id || !ts || !sig) return false;

  // Reject events older than 5 minutes to prevent replay
  const now = Math.floor(Date.now() / 1000);
  const tsNum = parseInt(ts, 10);
  if (!Number.isFinite(tsNum) || Math.abs(now - tsNum) > 5 * 60) return false;

  // Svix secrets start with "whsec_" followed by base64-encoded key bytes
  const cleanSecret = secret.startsWith("whsec_") ? secret.slice(6) : secret;
  let secretBytes: Buffer;
  try {
    secretBytes = Buffer.from(cleanSecret, "base64");
  } catch {
    return false;
  }

  const signedPayload = `${id}.${ts}.${body}`;
  const expectedSig = crypto
    .createHmac("sha256", secretBytes)
    .update(signedPayload)
    .digest("base64");

  // Header may contain multiple comma- or space-separated signatures (versioned)
  // e.g. "v1,sig1 v1,sig2"
  const candidates = sig
    .split(/\s+/)
    .map((s) => s.replace(/^v\d+,/, ""))
    .filter(Boolean);

  for (const candidate of candidates) {
    const candBuf = Buffer.from(candidate, "base64");
    const expBuf = Buffer.from(expectedSig, "base64");
    if (
      candBuf.length === expBuf.length &&
      crypto.timingSafeEqual(candBuf, expBuf)
    ) {
      return true;
    }
  }
  return false;
}

async function updateSubscriberStatus(
  email: string,
  status: "bounced" | "complained",
): Promise<void> {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) {
    console.error("resend/webhook: Supabase env not set");
    return;
  }
  const res = await fetch(
    `${url.replace(/\/$/, "")}/rest/v1/newsletter_subscribers?email=eq.${encodeURIComponent(email.toLowerCase())}`,
    {
      method: "PATCH",
      headers: {
        apikey: key,
        Authorization: `Bearer ${key}`,
        "Content-Type": "application/json",
        Prefer: "return=minimal",
      },
      body: JSON.stringify({
        status,
        ...(status === "bounced" ? { unsubscribed_at: new Date().toISOString() } : {}),
      }),
    },
  );
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    console.error(`resend/webhook: Supabase update ${res.status}: ${text}`);
  }
}

function emailsFromPayload(payload: ResendPayload): string[] {
  const to = payload.data?.to;
  if (!to) return [];
  if (typeof to === "string") return [to];
  if (Array.isArray(to)) return to;
  return [];
}

export async function POST(req: NextRequest) {
  const secret = process.env.RESEND_WEBHOOK_SECRET;
  if (!secret) {
    console.error("resend/webhook: RESEND_WEBHOOK_SECRET not set");
    return NextResponse.json({ ok: false }, { status: 500 });
  }

  // Read raw body for signature verification
  const body = await req.text();

  if (!verifySvixSignature(secret, req.headers, body)) {
    return NextResponse.json({ ok: false, error: "Invalid signature" }, { status: 401 });
  }

  let payload: ResendPayload;
  try {
    payload = JSON.parse(body);
  } catch {
    return NextResponse.json({ ok: false, error: "Invalid JSON" }, { status: 400 });
  }

  switch (payload.type) {
    case "email.bounced": {
      for (const email of emailsFromPayload(payload)) {
        await updateSubscriberStatus(email, "bounced").catch((err) =>
          console.error(`resend/webhook bounced for ${email}`, err),
        );
      }
      break;
    }
    case "email.complained": {
      for (const email of emailsFromPayload(payload)) {
        await updateSubscriberStatus(email, "complained").catch((err) =>
          console.error(`resend/webhook complained for ${email}`, err),
        );
      }
      break;
    }
    // Other events are logged-only / ignored. Add cases here if you want
    // to track delivered/opened/clicked into your own analytics.
    default:
      break;
  }

  return NextResponse.json({ ok: true });
}
