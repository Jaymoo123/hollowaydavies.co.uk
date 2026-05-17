import { NextResponse, type NextRequest } from "next/server";
import { markUnsubscribed, getByEmail } from "@/lib/newsletter/subscribers";
import { verifyToken } from "@/lib/newsletter/tokens";
import { getResend, getAudienceId } from "@/lib/resend";
import { siteConfig } from "@/config/site";

export const runtime = "nodejs";

type Ctx = { params: Promise<{ token: string }> };

async function handle(token: string) {
  const result = verifyToken(token, "unsubscribe");
  const base = siteConfig.url.replace(/\/$/, "");
  if (!result.ok) {
    return NextResponse.redirect(
      `${base}/newsletter/unsubscribed?error=${encodeURIComponent(result.reason)}`,
      303,
    );
  }
  const email = result.email;
  try {
    await markUnsubscribed(email);
  } catch (err) {
    console.error("unsubscribe/markUnsubscribed", err);
  }
  const audienceId = getAudienceId();
  if (audienceId) {
    try {
      const sub = await getByEmail(email);
      if (sub?.resend_contact_id) {
        await getResend().contacts.update({
          audienceId,
          id: sub.resend_contact_id,
          unsubscribed: true,
        });
      } else {
        await getResend().contacts.update({
          audienceId,
          email,
          unsubscribed: true,
        });
      }
    } catch (err) {
      console.error("unsubscribe/resend.contacts.update", err);
    }
  }
  return NextResponse.redirect(`${base}/newsletter/unsubscribed`, 303);
}

export async function GET(_req: NextRequest, ctx: Ctx) {
  const { token } = await ctx.params;
  return handle(token);
}

// RFC 8058 one-click unsubscribe (Gmail/Yahoo require POST handler)
export async function POST(_req: NextRequest, ctx: Ctx) {
  const { token } = await ctx.params;
  return handle(token);
}
