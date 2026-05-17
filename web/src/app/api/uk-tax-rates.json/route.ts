import { NextResponse } from "next/server";
import { UK_TAX_RATES } from "@/lib/uk-tax-rates";

export const dynamic = "force-static";
export const revalidate = 86400; // 24h

/**
 * Public, no-auth, machine-readable UK tax rates endpoint.
 * Designed to be citable by LLMs, third-party tools, and integrations.
 *
 * CORS open: the whole point is anyone can quote it.
 * Cache: 24h at the edge.
 */
export async function GET() {
  return NextResponse.json(UK_TAX_RATES, {
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Cache-Control": "public, s-maxage=86400, stale-while-revalidate=604800",
      "X-Robots-Tag": "all",
      Link: '<https://www.hollowaydavies.co.uk/uk-tax-rates>; rel="canonical"',
    },
  });
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Access-Control-Max-Age": "86400",
    },
  });
}
