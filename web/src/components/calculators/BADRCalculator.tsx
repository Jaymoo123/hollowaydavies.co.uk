"use client";

import { useMemo, useState } from "react";

/**
 * Business Asset Disposal Relief (BADR) calculator, 2025/26 rates.
 *
 *  - BADR rate: 14% for disposals on/after 6 April 2025 (rising to 18% from 6 April 2026)
 *  - Standard CGT rate (higher rate): 24% (assumed for comparison)
 *  - £1M lifetime allowance
 *  - Eligibility: 5%+ shareholding, officer/employee, held 2+ years
 */

const BADR_RATE_2025_26 = 0.14;
const BADR_RATE_2026_27 = 0.18;
const STANDARD_CGT_HIGHER = 0.24;
const BADR_LIFETIME_LIMIT = 1_000_000;

const fmt = (n: number) => `£${Math.round(n).toLocaleString("en-GB")}`;

type Year = "2025/26" | "2026/27";

export function BADRCalculator() {
  const [saleProceeds, setSaleProceeds] = useState(2500000);
  const [originalCost, setOriginalCost] = useState(100);
  const [previousBADRUsed, setPreviousBADRUsed] = useState(0);
  const [year, setYear] = useState<Year>("2025/26");
  const [meetsEligibility, setMeetsEligibility] = useState(true);

  const result = useMemo(() => {
    const gain = Math.max(0, saleProceeds - originalCost);
    const badrRate = year === "2025/26" ? BADR_RATE_2025_26 : BADR_RATE_2026_27;
    const availableBADR = Math.max(0, BADR_LIFETIME_LIMIT - previousBADRUsed);

    if (!meetsEligibility) {
      const standardTax = gain * STANDARD_CGT_HIGHER;
      return {
        gain,
        eligibleForBADR: 0,
        notEligible: gain,
        badrTax: 0,
        standardTax,
        totalTax: standardTax,
        netProceeds: saleProceeds - standardTax,
        effectiveRate: gain > 0 ? standardTax / gain : 0,
      };
    }

    const eligibleSlice = Math.min(gain, availableBADR);
    const overflowSlice = gain - eligibleSlice;
    const badrTax = eligibleSlice * badrRate;
    const standardTax = overflowSlice * STANDARD_CGT_HIGHER;
    const totalTax = badrTax + standardTax;

    return {
      gain,
      eligibleForBADR: eligibleSlice,
      notEligible: overflowSlice,
      badrTax,
      standardTax,
      totalTax,
      netProceeds: saleProceeds - totalTax,
      effectiveRate: gain > 0 ? totalTax / gain : 0,
    };
  }, [saleProceeds, originalCost, previousBADRUsed, year, meetsEligibility]);

  const withoutBADR = useMemo(() => result.gain * STANDARD_CGT_HIGHER, [result.gain]);
  const saving = withoutBADR - result.totalTax;

  return (
    <div className="space-y-8">
      <div className="bg-slate-50 border border-slate-200 p-6 sm:p-8">
        <h2 className="text-xl font-bold text-slate-900">Your sale</h2>

        <div className="mt-6 space-y-5">
          <div>
            <label htmlFor="proc" className="block text-sm font-bold text-slate-900">Sale proceeds (your share)</label>
            <div className="mt-2 flex items-center gap-2">
              <span className="text-slate-500">£</span>
              <input id="proc" type="number" value={saleProceeds} onChange={(e) => setSaleProceeds(Math.max(0, Number(e.target.value) || 0))} min={0} max={20000000} step={10000}
                className="w-44 border border-slate-300 px-3 py-2 text-base text-slate-900 focus:outline-none focus:border-orange-600" />
            </div>
          </div>

          <div>
            <label htmlFor="cost" className="block text-sm font-bold text-slate-900">Original cost of shares</label>
            <p className="text-xs text-slate-500 mt-0.5">What you paid for the shares originally. Often nominal (£1 or £100) for founders who incorporated their own business.</p>
            <div className="mt-2 flex items-center gap-2">
              <span className="text-slate-500">£</span>
              <input id="cost" type="number" value={originalCost} onChange={(e) => setOriginalCost(Math.max(0, Number(e.target.value) || 0))} min={0} max={5000000} step={100}
                className="w-44 border border-slate-300 px-3 py-2 text-base text-slate-900 focus:outline-none focus:border-orange-600" />
            </div>
          </div>

          <div>
            <label htmlFor="prev" className="block text-sm font-bold text-slate-900">BADR previously used (lifetime)</label>
            <p className="text-xs text-slate-500 mt-0.5">£1M lifetime limit applies across all your qualifying disposals ever. If this is your first disposal, enter 0.</p>
            <div className="mt-2 flex items-center gap-2">
              <span className="text-slate-500">£</span>
              <input id="prev" type="number" value={previousBADRUsed} onChange={(e) => setPreviousBADRUsed(Math.max(0, Number(e.target.value) || 0))} min={0} max={BADR_LIFETIME_LIMIT} step={10000}
                className="w-44 border border-slate-300 px-3 py-2 text-base text-slate-900 focus:outline-none focus:border-orange-600" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-900">Tax year of disposal</label>
            <div className="mt-2 flex gap-2">
              {(["2025/26", "2026/27"] as const).map((y) => (
                <button key={y} type="button" onClick={() => setYear(y)}
                  className={`px-4 py-2 border-2 text-sm font-semibold ${year === y ? "border-orange-600 bg-orange-50 text-orange-700" : "border-slate-200 bg-white text-slate-700 hover:border-slate-300"}`}>
                  {y} {y === "2025/26" ? "(14%)" : "(18%)"}
                </button>
              ))}
            </div>
            <p className="text-xs text-slate-500 mt-2">BADR rate rises from 14% to 18% on 6 April 2026.</p>
          </div>

          <div className="flex items-start gap-3">
            <input id="elig" type="checkbox" checked={meetsEligibility} onChange={(e) => setMeetsEligibility(e.target.checked)}
              className="mt-1 h-4 w-4 accent-orange-600" />
            <label htmlFor="elig" className="text-sm text-slate-700">
              <span className="font-semibold text-slate-900">Meets BADR eligibility</span>: I hold 5%+ of the shares, I'm an officer or employee, and I've held the shares for 2+ years before disposal.
            </label>
          </div>
        </div>
      </div>

      <div className="bg-orange-700 text-white p-6 sm:p-8">
        <p className="text-sm font-bold uppercase tracking-wider text-orange-200">Your CGT bill</p>
        <div className="mt-3 grid sm:grid-cols-2 gap-6">
          <div>
            <p className="text-xs text-orange-200 uppercase tracking-wider">Total CGT</p>
            <p className="text-3xl sm:text-4xl font-bold font-mono">{fmt(result.totalTax)}</p>
            <p className="text-xs text-orange-200 mt-1">Effective rate: {(result.effectiveRate * 100).toFixed(1)}%</p>
          </div>
          <div>
            <p className="text-xs text-orange-200 uppercase tracking-wider">Net proceeds (after CGT)</p>
            <p className="text-3xl sm:text-4xl font-bold font-mono">{fmt(result.netProceeds)}</p>
          </div>
        </div>
      </div>

      <div className="bg-white border border-slate-200">
        <h3 className="px-6 py-4 text-lg font-bold text-slate-900 border-b border-slate-200">The breakdown</h3>
        <dl className="divide-y divide-slate-200">
          <Row label="Capital gain" value={fmt(result.gain)} />
          {meetsEligibility && <Row label="Qualifies for BADR (capped at lifetime £1M)" value={fmt(result.eligibleForBADR)} />}
          {meetsEligibility && <Row label={`BADR tax @ ${(year === "2025/26" ? BADR_RATE_2025_26 : BADR_RATE_2026_27) * 100}%`} value={fmt(result.badrTax)} />}
          {result.notEligible > 0 && <Row label="Gain above BADR limit (standard CGT)" value={fmt(result.notEligible)} />}
          {result.standardTax > 0 && <Row label={`Standard CGT @ ${STANDARD_CGT_HIGHER * 100}%`} value={fmt(result.standardTax)} />}
          <Row label="Total CGT" value={fmt(result.totalTax)} highlight />
        </dl>
      </div>

      {meetsEligibility && saving > 0 && (
        <div className="bg-emerald-50 border border-emerald-300 p-6">
          <p className="text-sm font-bold uppercase tracking-wider text-emerald-800">BADR is saving you</p>
          <p className="text-3xl font-bold text-emerald-900 font-mono mt-1">{fmt(saving)}</p>
          <p className="mt-2 text-sm text-emerald-900">
            Without BADR, your CGT bill would be {fmt(withoutBADR)} at the standard 24% higher rate.
          </p>
        </div>
      )}
    </div>
  );
}

function Row({ label, value, highlight = false }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className={`flex items-center justify-between px-6 py-3 ${highlight ? "bg-slate-50 font-bold" : ""}`}>
      <dt className="text-sm text-slate-700">{label}</dt>
      <dd className="font-mono text-sm text-slate-900">{value}</dd>
    </div>
  );
}
