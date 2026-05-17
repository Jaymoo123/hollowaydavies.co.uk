import { NextResponse, type NextRequest } from "next/server";
import { upsertPending, markConfirmed } from "@/lib/newsletter/subscribers";
import { mintToken } from "@/lib/newsletter/tokens";
import { getResend, getFromAddress, getReplyTo } from "@/lib/resend";
import ConfirmEmail from "@/emails/ConfirmEmail";
import { siteConfig } from "@/config/site";

export const runtime = "nodejs";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export async function POST(req: NextRequest) {
  let payload: { email?: unknown; agencyType?: unknown; source?: unknown; sourceUrl?: unknown };
  try {
    payload = await req.json();
  } catch {
    return NextResponse.json({ ok: false, error: "Invalid JSON" }, { status: 400 });
  }

  const email = typeof payload.email === "string" ? payload.email.trim().toLowerCase() : "";
  if (!email || !EMAIL_RE.test(email) || email.length > 254) {
    return NextResponse.json({ ok: false, error: "Invalid email" }, { status: 400 });
  }
  const agencyType =
    typeof payload.agencyType === "string" && payload.agencyType.length < 80
      ? payload.agencyType
      : undefined;
  const source =
    typeof payload.source === "string" && payload.source.length < 80
      ? payload.source
      : undefined;
  const sourceUrl =
    typeof payload.sourceUrl === "string" && payload.sourceUrl.length < 500
      ? payload.sourceUrl
      : undefined;

  try {
    await upsertPending({ email, agencyType, source, sourceUrl });
  } catch (err) {
    console.error("subscribe/upsertPending", err);
    return NextResponse.json(
      { ok: false, error: "Could not record subscription" },
      { status: 500 },
    );
  }

  // If Resend isn't configured (e.g. free-tier limit means we can't add a new
  // sending domain for this site), we still want to capture the email. Skip
  // the confirmation flow entirely and mark the row confirmed directly so the
  // list is ready to email later once Resend is wired up.
  const resendConfigured = Boolean(process.env.RESEND_API_KEY);

  if (!resendConfigured) {
    try {
      await markConfirmed(email);
    } catch (err) {
      console.error("subscribe/markConfirmed (no-resend mode)", err);
    }
    return NextResponse.json({ ok: true, mode: "collect-only" });
  }

  const token = mintToken(email, "confirm");
  const base = siteConfig.url.replace(/\/$/, "");
  const confirmUrl = `${base}/api/newsletter/confirm/${encodeURIComponent(token)}`;

  try {
    await getResend().emails.send({
      from: getFromAddress(),
      replyTo: getReplyTo(),
      to: email,
      subject: "Confirm your subscription to The Director's Brief",
      react: ConfirmEmail({ confirmUrl }),
      headers: {
        "List-Unsubscribe": `<${base}/newsletter>`,
      },
    });
  } catch (err) {
    console.error("subscribe/resend.send", err);
    // Still 200, record exists, user can retry
  }

  return NextResponse.json({ ok: true, mode: "confirm-required" });
}
