"use client";

import { useMemo, useState } from "react";

/**
 * VAT scheme comparator, compares Standard, Flat Rate (with limited cost trader),
 * and Cash Accounting for UK businesses.
 *
 *  - Standard: charge 20%, reclaim input VAT, pay net to HMRC
 *  - Flat Rate: charge 20%, pay HMRC a flat % of VAT-inclusive turnover. Sector rates vary
 *               (e.g. marketing / consultancy = 12.5%), but Limited Cost Traders
 *               (most service businesses with minimal goods spend) revert to 16.5%
 *  - Cash Accounting: standard rules but on cash basis (only owe VAT when client pays)
 */

const STANDARD_VAT = 0.20;
const FLAT_RATE_MARKETING_AGENCY = 0.125;
const FLAT_RATE_LCT = 0.165;
const ANNUAL_LCT_GOODS_THRESHOLD = 1000;
const LCT_TURNOVER_THRESHOLD = 0.02; // 2% of VAT-inclusive turnover

const fmt = (n: number) => `£${Math.round(n).toLocaleString("en-GB")}`;

export function VATSchemeComparator() {
  const [turnover, setTurnover] = useState(180000);
  const [vatInputs, setVatInputs] = useState(8000);
  const [goodsSpend, setGoodsSpend] = useState(500);

  const result = useMemo(() => {
    const vatCollected = turnover * STANDARD_VAT;
    const grossInclusive = turnover + vatCollected;

    // Standard scheme
    const standardNet = vatCollected - vatInputs;

    // Flat rate scheme, Limited Cost Trader test
    const lctGoodsCheck = goodsSpend < Math.max(ANNUAL_LCT_GOODS_THRESHOLD, grossInclusive * LCT_TURNOVER_THRESHOLD);
    const flatRate = lctGoodsCheck ? FLAT_RATE_LCT : FLAT_RATE_MARKETING_AGENCY;
    const flatPayment = grossInclusive * flatRate;
    const flatKeep = vatCollected - flatPayment;
    const flatNet = flatPayment;

    return {
      vatCollected,
      grossInclusive,
      standardNet,
      flatRate,
      flatNet,
      flatKeep,
      lctApplies: lctGoodsCheck,
      bestScheme: standardNet < flatNet ? "Standard" : "Flat Rate",
      saving: Math.abs(standardNet - flatNet),
    };
  }, [turnover, vatInputs, goodsSpend]);

  return (
    <div className="space-y-8">
      <div className="bg-slate-50 border border-slate-200 p-6 sm:p-8">
        <h2 className="text-xl font-bold text-slate-900">Your VAT position</h2>

        <div className="mt-6 space-y-5">
          <div>
            <label htmlFor="t" className="block text-sm font-bold text-slate-900">Annual VAT-able turnover (ex VAT)</label>
            <div className="mt-2 flex items-center gap-2">
              <span className="text-slate-500">£</span>
              <input id="t" type="number" value={turnover} onChange={(e) => setTurnover(Math.max(0, Number(e.target.value) || 0))} min={0} max={5000000} step={1000}
                className="w-44 border border-slate-300 px-3 py-2 text-base text-slate-900 focus:outline-none focus:border-orange-600" />
            </div>
          </div>

          <div>
            <label htmlFor="i" className="block text-sm font-bold text-slate-900">Annual VAT reclaimable on inputs</label>
            <p className="text-xs text-slate-500 mt-0.5">VAT element of your business costs (software, freelancers if VAT-registered, equipment). Standard scheme reclaims this; flat rate doesn't.</p>
            <div className="mt-2 flex items-center gap-2">
              <span className="text-slate-500">£</span>
              <input id="i" type="number" value={vatInputs} onChange={(e) => setVatInputs(Math.max(0, Number(e.target.value) || 0))} min={0} max={500000} step={500}
                className="w-44 border border-slate-300 px-3 py-2 text-base text-slate-900 focus:outline-none focus:border-orange-600" />
            </div>
          </div>

          <div>
            <label htmlFor="g" className="block text-sm font-bold text-slate-900">Annual relevant goods spend</label>
            <p className="text-xs text-slate-500 mt-0.5">Spend on physical goods used in business. Excludes services, software, stationery for own use, travel, capital items. For a service-based business, this is usually very low.</p>
            <div className="mt-2 flex items-center gap-2">
              <span className="text-slate-500">£</span>
              <input id="g" type="number" value={goodsSpend} onChange={(e) => setGoodsSpend(Math.max(0, Number(e.target.value) || 0))} min={0} max={100000} step={100}
                className="w-44 border border-slate-300 px-3 py-2 text-base text-slate-900 focus:outline-none focus:border-orange-600" />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-orange-700 text-white p-6 sm:p-8">
        <p className="text-sm font-bold uppercase tracking-wider text-orange-200">Best scheme for you</p>
        <p className="text-3xl sm:text-4xl font-bold font-mono mt-2">{result.bestScheme}</p>
        <p className="mt-2 text-sm text-orange-100">
          Saves <strong className="font-bold">{fmt(result.saving)}</strong> per year vs the other scheme.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        <div className={`bg-white border-2 p-6 ${result.bestScheme === "Standard" ? "border-orange-600" : "border-slate-200"}`}>
          <h3 className="text-lg font-bold text-slate-900">Standard VAT scheme</h3>
          <dl className="mt-4 space-y-2 text-sm">
            <DRow l="VAT collected (20%)" v={fmt(result.vatCollected)} />
            <DRow l="VAT reclaimed on inputs" v={`-${fmt(vatInputs)}`} />
            <DRow l="Net payable to HMRC" v={fmt(result.standardNet)} bold />
          </dl>
          <p className="mt-4 text-xs text-slate-500">Reclaim VAT on costs. Best when your input VAT is meaningful (£8k+ per year).</p>
        </div>

        <div className={`bg-white border-2 p-6 ${result.bestScheme === "Flat Rate" ? "border-orange-600" : "border-slate-200"}`}>
          <h3 className="text-lg font-bold text-slate-900">Flat Rate scheme</h3>
          <p className="text-xs text-slate-500 mt-1">
            Rate applied: <strong className="font-bold">{(result.flatRate * 100).toFixed(1)}%</strong>
            {result.lctApplies ? " (Limited Cost Trader)" : " (your sector rate)"}
          </p>
          <dl className="mt-4 space-y-2 text-sm">
            <DRow l="VAT-inclusive turnover" v={fmt(result.grossInclusive)} />
            <DRow l={`Flat payment @ ${(result.flatRate * 100).toFixed(1)}%`} v={fmt(result.flatNet)} bold />
            <DRow l="Difference vs collected VAT" v={result.flatKeep >= 0 ? `+${fmt(result.flatKeep)}` : `-${fmt(Math.abs(result.flatKeep))}`} />
          </dl>
          <p className="mt-4 text-xs text-slate-500">
            {result.lctApplies
              ? "Limited Cost Trader rate (16.5%) applies because your goods spend is below 2% of turnover or £1,000. Rarely beneficial for service businesses."
              : "Sector flat-rate applies (typical 12.5% for marketing / consultancy services; sector rate varies, check HMRC's published list). Beneficial only if your input VAT is low."}
          </p>
        </div>
      </div>

      <div className="bg-white border border-slate-200 p-6 text-sm text-slate-600">
        <p className="font-bold text-slate-900 mb-2">Cash Accounting (consider separately)</p>
        <p>
          Cash Accounting can be combined with either scheme above. It means you account for VAT when you receive payment, not when you raise an invoice. Cash-flow positive if you have long payment terms with clients (60+ days). Available if turnover is under £1.35M.
        </p>
      </div>
    </div>
  );
}

function DRow({ l, v, bold = false }: { l: string; v: string; bold?: boolean }) {
  return (
    <div className={`flex items-center justify-between ${bold ? "font-bold text-slate-900 pt-2 border-t border-slate-200" : "text-slate-700"}`}>
      <dt>{l}</dt>
      <dd className="font-mono">{v}</dd>
    </div>
  );
}
