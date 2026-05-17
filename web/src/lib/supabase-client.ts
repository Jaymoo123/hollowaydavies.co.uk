/**
 * Shared Supabase Client - Backend Logic Only
 * Used by all niches for lead submission and blog content fetching
 */

export interface LeadSubmission {
  full_name: string;
  email: string;
  phone: string;
  role: string;
  practice_name?: string;
  message: string;
  source: string;
  source_url: string;
  submitted_at: string;
}

export async function submitLead(
  payload: LeadSubmission,
  supabaseUrl: string,
  supabaseKey: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const res = await fetch(`${supabaseUrl}/rest/v1/leads`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "apikey": supabaseKey,
        "Authorization": `Bearer ${supabaseKey}`,
        "Prefer": "return=minimal"
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errorText = await res.text().catch(() => "");
      if (process.env.NODE_ENV === 'development') {
        console.error("Lead submission failed:", res.status, errorText);
      }
      return { success: false, error: `Request failed (${res.status})` };
    }

    if (process.env.NODE_ENV === 'development') {
      console.log("Lead submission success");
    }
    return { success: true };
  } catch (err) {
    if (process.env.NODE_ENV === 'development') {
      console.error("Lead submission error:", err);
    }
    return { success: false, error: err instanceof Error ? err.message : "Unknown error" };
  }
}

export function getSupabaseConfig() {
  const supabaseUrl = typeof process !== "undefined" ? process.env.NEXT_PUBLIC_SUPABASE_URL : undefined;
  const supabaseKey = typeof process !== "undefined" ? process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY : undefined;
  
  return { supabaseUrl, supabaseKey };
}
