import { NextResponse, type NextRequest } from "next/server";
import { markConfirmed } from "@/lib/newsletter/subscribers";
import { mintToken, verifyToken } from "@/lib/newsletter/tokens";
import { getResend, getFromAddress, getReplyTo, getAudienceId } from "@/lib/resend";
import WelcomeEmail from "@/emails/WelcomeEmail";
import { WELCOME_SERIES } from "@/emails/content/welcome-series";
import { siteConfig } from "@/config/site";

export const runtime = "nodejs";

type Ctx = { params: Promise<{ token: string }> };

export async function GET(_req: NextRequest, ctx: Ctx) {
  const { token } = await ctx.params;
  const result = verifyToken(token, "confirm");

  const base = siteConfig.url.replace(/\/$/, "");

  if (!result.ok) {
    const reason = encodeURIComponent(result.reason);
    return NextResponse.redirect(`${base}/newsletter/confirmed?error=${reason}`, 303);
  }

  const email = result.email;

  let resendContactId: string | undefined;
  const audienceId = getAudienceId();
  if (audienceId) {
    try {
      const created = await getResend().contacts.create({
        audienceId,
        email,
        unsubscribed: false,
      });
      resendContactId = created.data?.id;
    } catch (err) {
      console.error("confirm/resend.contacts.create", err);
    }
  }

  try {
    await markConfirmed(email, resendContactId);
  } catch (err) {
    console.error("confirm/markConfirmed", err);
    return NextResponse.redirect(`${base}/newsletter/confirmed?error=storage`, 303);
  }

  // Send Welcome 1 immediately
  const step1 = WELCOME_SERIES[0];
  const unsubscribeUrl = `${base}/api/newsletter/unsubscribe/${encodeURIComponent(
    mintToken(email, "unsubscribe"),
  )}`;

  try {
    await getResend().emails.send({
      from: getFromAddress(),
      replyTo: getReplyTo(),
      to: email,
      subject: step1.subject,
      react: WelcomeEmail({ step: step1, unsubscribeUrl }),
      headers: {
        "List-Unsubscribe": `<${unsubscribeUrl}>, <mailto:${getReplyTo()}?subject=unsubscribe>`,
        "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
      },
    });
    // Mark step 1 as sent so the cron drip picks up at step 2
    const { advanceWelcomeStep } = await import("@/lib/newsletter/subscribers");
    await advanceWelcomeStep(email, 1);
  } catch (err) {
    console.error("confirm/sendWelcome1", err);
  }

  return NextResponse.redirect(`${base}/newsletter/confirmed`, 303);
}
