"use client";

import { useMemo, useState } from "react";

const PERSONAL_ALLOWANCE = 12570;
const BASIC_RATE_LIMIT = 50270;
const HIGHER_RATE_LIMIT = 125140;
const DIVIDEND_ALLOWANCE = 500;
const DIVIDEND_BASIC = 0.0875;
const DIVIDEND_HIGHER = 0.3375;
const DIVIDEND_ADDITIONAL = 0.3935;
const CT_SMALL_THRESHOLD = 50000;
const CT_MAIN_THRESHOLD = 250000;
const CT_SMALL_RATE = 0.19;
const CT_MAIN_RATE = 0.25;
const CT_MARGINAL_RATE = 0.265;
const ANNUAL_ALLOWANCE = 60000;
const ANNUAL_ALLOWANCE_TAPER_FLOOR = 10000;

function corporationTax(profit: number): number {
  if (profit <= 0) return 0;
  if (profit <= CT_SMALL_THRESHOLD) return profit * CT_SMALL_RATE;
  if (profit >= CT_MAIN_THRESHOLD) return profit * CT_MAIN_RATE;
  return CT_SMALL_THRESHOLD * CT_SMALL_RATE + (profit - CT_SMALL_THRESHOLD) * CT_MARGINAL_RATE;
}

function marginalCorpRate(profit: number): number {
  if (profit <= 0) return 0;
  if (profit <= CT_SMALL_THRESHOLD) return CT_SMALL_RATE;
  if (profit >= CT_MAIN_THRESHOLD) return CT_MAIN_RATE;
  return CT_MARGINAL_RATE;
}

function dividendTaxOnAmount(salary: number, dividend: number): number {
  let pa = PERSONAL_ALLOWANCE;
  if (salary + dividend > 100000) {
    pa = Math.max(0, PERSONAL_ALLOWANCE - (salary + dividend - 100000) / 2);
  }
  const paUsedBySalary = Math.min(salary, pa);
  const paLeftForDividend = Math.max(0, pa - paUsedBySalary);
  const taxableDividend = Math.max(0, dividend - paLeftForDividend - DIVIDEND_ALLOWANCE);
  if (taxableDividend === 0) return 0;

  const basicBandCapacity = BASIC_RATE_LIMIT - PERSONAL_ALLOWANCE;
  const higherBandCapacity = HIGHER_RATE_LIMIT - BASIC_RATE_LIMIT;
  const salaryInBasic = Math.min(Math.max(0, salary - pa), basicBandCapacity);
  const salaryInHigher = Math.min(
    Math.max(0, salary - pa - salaryInBasic),
    higherBandCapacity,
  );
  const remainingBasic = basicBandCapacity - salaryInBasic;
  const remainingHigher = higherBandCapacity - salaryInHigher;

  let div = taxableDividend;
  let tax = 0;
  const inBasic = Math.min(div, Math.max(0, remainingBasic));
  tax += inBasic * DIVIDEND_BASIC;
  div -= inBasic;
  const inHigher = Math.min(div, Math.max(0, remainingHigher));
  tax += inHigher * DIVIDEND_HIGHER;
  div -= inHigher;
  tax += div * DIVIDEND_ADDITIONAL;
  return tax;
}

function taperedAnnualAllowance(adjustedIncome: number): number {
  if (adjustedIncome <= 260000) return ANNUAL_ALLOWANCE;
  const reduction = Math.floor((adjustedIncome - 260000) / 2);
  return Math.max(ANNUAL_ALLOWANCE_TAPER_FLOOR, ANNUAL_ALLOWANCE - reduction);
}

const fmt = (n: number) => `£${Math.round(n).toLocaleString("en-GB")}`;

export function PensionContributionOptimiser() {
  const [profit, setProfit] = useState(150000);
  const [salary, setSalary] = useState(12570);
  const [contribution, setContribution] = useState(30000);
  const [adjustedIncome, setAdjustedIncome] = useState(150000);

  const result = useMemo(() => {
    const allowance = taperedAnnualAllowance(adjustedIncome);
    const c = Math.min(contribution, allowance);
    const profitAfter = Math.max(0, profit - salary - c);
    const ctWithPension = corporationTax(profitAfter);

    const profitNoPension = Math.max(0, profit - salary);
    const ctNoPension = corporationTax(profitNoPension);
    const ctSaved = ctNoPension - ctWithPension;

    const marginal = marginalCorpRate(profitNoPension);
    const realCostToCompany = c - ctSaved;

    const dividendIfTakenInstead = Math.max(0, c - (c * marginal));
    const dividendTaxIfTakenInstead = dividendTaxOnAmount(salary, dividendIfTakenInstead);
    const netDividendIfTakenInstead = dividendIfTakenInstead - dividendTaxIfTakenInstead;
    const pensionAdvantage = c - netDividendIfTakenInstead;

    return {
      allowance,
      contribution: c,
      capped: contribution > allowance,
      ctWithPension,
      ctNoPension,
      ctSaved,
      marginal,
      realCostToCompany,
      pensionAdvantage,
      netDividendIfTakenInstead,
      profitAfter,
    };
  }, [profit, salary, contribution, adjustedIncome]);

  return (
    <div className="space-y-8">
      <div className="bg-slate-50 border border-slate-200 p-6 sm:p-8">
        <h2 className="text-xl font-bold text-slate-900">Your inputs</h2>

        <div className="mt-6 grid sm:grid-cols-2 gap-6">
          <Field label="Company profit before extraction" value={profit} onChange={setProfit} max={2000000} />
          <Field label="Director salary (already taken)" value={salary} onChange={setSalary} max={250000} />
          <Field label="Proposed employer pension contribution" value={contribution} onChange={setContribution} max={ANNUAL_ALLOWANCE} />
          <Field label="Your adjusted income (for taper test)" value={adjustedIncome} onChange={setAdjustedIncome} max={500000} hint="Salary + dividends + employer pension contributions" />
        </div>

        {result.capped && (
          <p className="mt-4 text-sm text-amber-800 bg-amber-50 border-l-4 border-amber-500 p-3">
            Your contribution exceeded your tapered annual allowance of {fmt(result.allowance)}. Calculation uses {fmt(result.contribution)}.
            You may still be able to use carry-forward from the previous three tax years.
          </p>
        )}
      </div>

      <div className="bg-orange-700 text-white p-6 sm:p-8">
        <p className="text-sm font-bold uppercase tracking-wider text-orange-200">In your pension</p>
        <p className="text-4xl sm:text-5xl font-bold font-mono mt-1">{fmt(result.contribution)}</p>
        <p className="mt-2 text-sm text-orange-200">
          Real cost to the company after corp tax saving: <span className="font-bold text-white">{fmt(result.realCostToCompany)}</span>
        </p>
      </div>

      <div className="bg-white border border-slate-200">
        <h3 className="px-6 py-4 text-lg font-bold text-slate-900 border-b border-slate-200">
          The tax effect
        </h3>
        <dl className="divide-y divide-slate-200">
          <Row label="Corp tax without pension" value={fmt(result.ctNoPension)} />
          <Row label="Corp tax with pension" value={fmt(result.ctWithPension)} />
          <Row label="Corp tax saved" value={fmt(result.ctSaved)} highlight />
          <Row label="Marginal corp tax rate at this profit" value={`${(result.marginal * 100).toFixed(1)}%`} />
        </dl>
      </div>

      <div className="bg-white border border-slate-200">
        <h3 className="px-6 py-4 text-lg font-bold text-slate-900 border-b border-slate-200">
          Versus taking the same money as dividend
        </h3>
        <dl className="divide-y divide-slate-200">
          <Row label="Net dividend if taken instead" value={fmt(result.netDividendIfTakenInstead)} />
          <Row label="In pension via employer contribution" value={fmt(result.contribution)} />
          <Row
            label="Pension advantage"
            value={`+${fmt(result.pensionAdvantage)}`}
            highlight
            positive={result.pensionAdvantage > 0}
          />
        </dl>
        <p className="px-6 py-4 text-xs text-slate-500 border-t border-slate-200">
          The pension money is locked until age 55 (rising to 57 in 2028). 25% can be taken tax-free at retirement; the rest is taxed as income.
        </p>
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  max,
  hint,
}: {
  label: string;
  value: number;
  onChange: (n: number) => void;
  max: number;
  hint?: string;
}) {
  return (
    <div>
      <label className="block text-sm font-bold text-slate-900 mb-2">{label}</label>
      <div className="flex items-center gap-2">
        <span className="text-slate-500">£</span>
        <input
          type="number"
          value={value}
          onChange={(e) => onChange(Math.max(0, Math.min(max, Number(e.target.value) || 0)))}
          min={0}
          max={max}
          step={500}
          className="w-full border border-slate-300 px-3 py-2 text-base text-slate-900 focus:outline-none focus:border-orange-600"
        />
      </div>
      {hint && <p className="mt-1 text-xs text-slate-500">{hint}</p>}
    </div>
  );
}

function Row({
  label,
  value,
  highlight = false,
  positive,
}: {
  label: string;
  value: string;
  highlight?: boolean;
  positive?: boolean;
}) {
  const valueColor = highlight
    ? positive === true
      ? "text-emerald-700"
      : positive === false
      ? "text-rose-700"
      : "text-slate-900"
    : "text-slate-900";
  return (
    <div className={`flex items-center justify-between px-6 py-3 ${highlight ? "bg-slate-50 font-bold" : ""}`}>
      <dt className="text-sm text-slate-700">{label}</dt>
      <dd className={`font-mono text-sm ${valueColor}`}>{value}</dd>
    </div>
  );
}
