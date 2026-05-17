import crypto from "crypto";

/**
 * Stateless HMAC-signed tokens for double opt-in confirmation and
 * one-click unsubscribe. Token format: base64url(payload).base64url(sig)
 *
 * The payload is JSON: { e, i, x } where
 *   e = email (lowercased)
 *   i = intent ("confirm" | "unsubscribe")
 *   x = expiry (unix seconds)
 *
 * Anyone with NEWSLETTER_TOKEN_SECRET can mint/verify tokens. Keep it
 * server-side only. Rotating the secret invalidates all in-flight tokens
 * (acceptable for newsletter intents).
 */

type Intent = "confirm" | "unsubscribe";

type Payload = {
  e: string;
  i: Intent;
  x: number;
};

function getSecret(): string {
  const s = process.env.NEWSLETTER_TOKEN_SECRET;
  if (!s || s.length < 32) {
    throw new Error("NEWSLETTER_TOKEN_SECRET must be set to a 32+ char secret");
  }
  return s;
}

function base64url(buf: Buffer): string {
  return buf
    .toString("base64")
    .replace(/=+$/g, "")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");
}

function base64urlDecode(s: string): Buffer {
  const pad = s.length % 4 === 0 ? "" : "=".repeat(4 - (s.length % 4));
  return Buffer.from(s.replace(/-/g, "+").replace(/_/g, "/") + pad, "base64");
}

function sign(payload: Buffer): Buffer {
  return crypto.createHmac("sha256", getSecret()).update(payload).digest();
}

const CONFIRM_TTL_SECONDS = 7 * 24 * 60 * 60; // 7 days
const UNSUB_TTL_SECONDS = 365 * 24 * 60 * 60; // 1 year (email links must work long after sending)

export function mintToken(email: string, intent: Intent): string {
  const ttl = intent === "confirm" ? CONFIRM_TTL_SECONDS : UNSUB_TTL_SECONDS;
  const payload: Payload = {
    e: email.trim().toLowerCase(),
    i: intent,
    x: Math.floor(Date.now() / 1000) + ttl,
  };
  const body = Buffer.from(JSON.stringify(payload));
  const sig = sign(body);
  return `${base64url(body)}.${base64url(sig)}`;
}

export type VerifyResult =
  | { ok: true; email: string; intent: Intent }
  | { ok: false; reason: "malformed" | "bad-signature" | "expired" | "wrong-intent" };

export function verifyToken(token: string, expectedIntent: Intent): VerifyResult {
  if (!token || typeof token !== "string" || !token.includes(".")) {
    return { ok: false, reason: "malformed" };
  }
  const [bodyB64, sigB64] = token.split(".", 2);
  let body: Buffer;
  let sig: Buffer;
  try {
    body = base64urlDecode(bodyB64);
    sig = base64urlDecode(sigB64);
  } catch {
    return { ok: false, reason: "malformed" };
  }
  const expectedSig = sign(body);
  if (sig.length !== expectedSig.length || !crypto.timingSafeEqual(sig, expectedSig)) {
    return { ok: false, reason: "bad-signature" };
  }
  let payload: Payload;
  try {
    payload = JSON.parse(body.toString("utf8")) as Payload;
  } catch {
    return { ok: false, reason: "malformed" };
  }
  if (payload.i !== expectedIntent) {
    return { ok: false, reason: "wrong-intent" };
  }
  if (typeof payload.x !== "number" || payload.x < Math.floor(Date.now() / 1000)) {
    return { ok: false, reason: "expired" };
  }
  return { ok: true, email: payload.e, intent: payload.i };
}
