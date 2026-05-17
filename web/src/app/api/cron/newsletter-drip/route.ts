import { NextResponse, type NextRequest } from "next/server";
import { advanceWelcomeStep, findReadyForNextStep } from "@/lib/newsletter/subscribers";
import { mintToken } from "@/lib/newsletter/tokens";
import { getResend, getFromAddress, getReplyTo } from "@/lib/resend";
import WelcomeEmail from "@/emails/WelcomeEmail";
import { WELCOME_SERIES } from "@/emails/content/welcome-series";
import { siteConfig } from "@/config/site";

export const runtime = "nodejs";
export const maxDuration = 60;

/**
 * Drip cron. Run hourly. For each subscriber confirmed at least delayHours ago
 * and currently at step N-1, send step N.
 *
 * Auth: Vercel Cron sets `Authorization: Bearer ${CRON_SECRET}` on invocations.
 */

function isAuthorized(req: NextRequest): boolean {
  const secret = process.env.CRON_SECRET;
  if (!secret) return false;
  const auth = req.headers.get("authorization");
  return auth === `Bearer ${secret}`;
}

export async function GET(req: NextRequest) {
  if (!isAuthorized(req)) {
    return NextResponse.json({ ok: false, error: "unauthorized" }, { status: 401 });
  }

  const base = siteConfig.url.replace(/\/$/, "");
  const stats: Record<string, number> = {};

  for (let i = 1; i < WELCOME_SERIES.length; i++) {
    const step = WELCOME_SERIES[i];
    const ready = await findReadyForNextStep(i, step.delayHours);
    let sent = 0;
    for (const sub of ready) {
      const unsubscribeUrl = `${base}/api/newsletter/unsubscribe/${encodeURIComponent(
        mintToken(sub.email, "unsubscribe"),
      )}`;
      try {
        await getResend().emails.send({
          from: getFromAddress(),
          replyTo: getReplyTo(),
          to: sub.email,
          subject: step.subject,
          react: WelcomeEmail({ step, unsubscribeUrl }),
          headers: {
            "List-Unsubscribe": `<${unsubscribeUrl}>, <mailto:${getReplyTo()}?subject=unsubscribe>`,
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
          },
        });
        await advanceWelcomeStep(sub.email, step.step);
        sent++;
      } catch (err) {
        console.error(`cron/welcome step ${step.step}`, err);
      }
    }
    stats[`step_${step.step}`] = sent;
  }

  return NextResponse.json({ ok: true, stats });
}
