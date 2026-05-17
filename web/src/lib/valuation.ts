/**
 * Agency valuation math, shared between the client calculator and the
 * server-side OG image endpoint so both produce identical numbers.
 */

export type ValuationType = "generalist" | "specialist" | "premium";

export interface ValuationInputs {
  revenue: number;
  ebitdaPct: number;
  type: ValuationType;
  retainerPct: number;
  topClientPct: number;
  keyPersonDependent: boolean;
}

export interface ValuationResult {
  ebitda: number;
  baseMultiple: number;
  retainerUplift: number;
  concentrationDiscount: number;
  keyPersonDiscount: number;
  adjustedMultiple: number;
  low: number;
  mid: number;
  high: number;
}

const BASE_MULTIPLE: Record<ValuationType, number> = {
  generalist: 4,
  specialist: 6,
  premium: 8,
};

const VALUATION_TYPES = new Set<ValuationType>(["generalist", "specialist", "premium"]);

export function clampType(v: string | null | undefined): ValuationType {
  return v && VALUATION_TYPES.has(v as ValuationType) ? (v as ValuationType) : "generalist";
}

export function clampInt(v: string | null | undefined, fallback: number, min = 0, max = Number.POSITIVE_INFINITY): number {
  if (v == null) return fallback;
  const n = Number(v);
  if (!Number.isFinite(n)) return fallback;
  return Math.min(max, Math.max(min, Math.round(n)));
}

export function calculate(inputs: ValuationInputs): ValuationResult {
  const ebitda = inputs.revenue * (inputs.ebitdaPct / 100);
  const baseMultiple = BASE_MULTIPLE[inputs.type];
  const retainerUplift = inputs.retainerPct >= 70 ? 1.0 : inputs.retainerPct >= 50 ? 0.5 : 0;
  const concentrationDiscount = inputs.topClientPct >= 50 ? -1.5 : inputs.topClientPct >= 30 ? -0.5 : 0;
  const keyPersonDiscount = inputs.keyPersonDependent ? -1.0 : 0;
  const adjustedMultiple = Math.max(
    1,
    baseMultiple + retainerUplift + concentrationDiscount + keyPersonDiscount,
  );
  return {
    ebitda,
    baseMultiple,
    retainerUplift,
    concentrationDiscount,
    keyPersonDiscount,
    adjustedMultiple,
    low: ebitda * Math.max(1, adjustedMultiple - 0.5),
    mid: ebitda * adjustedMultiple,
    high: ebitda * (adjustedMultiple + 0.5),
  };
}

export function fromSearchParams(sp: URLSearchParams | Record<string, string | undefined>): ValuationInputs {
  const get = (k: string): string | null => {
    if (sp instanceof URLSearchParams) return sp.get(k);
    const v = sp[k];
    return v === undefined ? null : v;
  };
  return {
    revenue: clampInt(get("revenue"), 1200000, 0, 50_000_000),
    ebitdaPct: clampInt(get("ebitda"), 18, 0, 60),
    type: clampType(get("type")),
    retainerPct: clampInt(get("retainer"), 50, 0, 100),
    topClientPct: clampInt(get("concentration"), 20, 0, 100),
    keyPersonDependent: get("keyperson") === "1",
  };
}

export function toSearchParams(inputs: ValuationInputs): URLSearchParams {
  const sp = new URLSearchParams();
  sp.set("revenue", String(inputs.revenue));
  sp.set("ebitda", String(inputs.ebitdaPct));
  sp.set("type", inputs.type);
  sp.set("retainer", String(inputs.retainerPct));
  sp.set("concentration", String(inputs.topClientPct));
  sp.set("keyperson", inputs.keyPersonDependent ? "1" : "0");
  return sp;
}

export function formatGbp(n: number): string {
  return `£${Math.round(n).toLocaleString("en-GB")}`;
}

export function formatGbpCompact(n: number): string {
  if (n >= 1_000_000) {
    const m = n / 1_000_000;
    return `£${m >= 10 ? Math.round(m) : m.toFixed(1)}m`;
  }
  if (n >= 1000) return `£${Math.round(n / 1000)}k`;
  return `£${Math.round(n)}`;
}

export function typeLabel(type: ValuationType): string {
  switch (type) {
    case "generalist":
      return "Generalist service business";
    case "specialist":
      return "Specialist service business";
    case "premium":
      return "Premium / boutique business";
  }
}
