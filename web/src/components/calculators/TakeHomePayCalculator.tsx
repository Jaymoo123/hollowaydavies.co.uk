"use client";

import { useMemo, useState } from "react";

const PERSONAL_ALLOWANCE = 12570;
const BASIC_RATE_LIMIT = 50270;
const HIGHER_RATE_LIMIT = 125140;
const NI_PRIMARY = 12570;
const NI_UPPER = 50270;
const NI_BASIC = 0.08;
const NI_UPPER_RATE = 0.02;
const INCOME_BASIC = 0.20;
const INCOME_HIGHER = 0.40;
const INCOME_ADDITIONAL = 0.45;

type StudentLoanPlan = "none" | "plan1" | "plan2" | "plan4" | "plan5" | "pg";

const SL_THRESHOLDS: Record<StudentLoanPlan, { threshold: number; rate: number }> = {
  none: { threshold: 0, rate: 0 },
  plan1: { threshold: 24990, rate: 0.09 },
  plan2: { threshold: 27295, rate: 0.09 },
  plan4: { threshold: 31395, rate: 0.09 },
  plan5: { threshold: 25000, rate: 0.09 },
  pg: { threshold: 21000, rate: 0.06 },
};

function calcIncomeTax(salary: number): { tax: number; pa: number } {
  let pa = PERSONAL_ALLOWANCE;
  if (salary > 100000) pa = Math.max(0, PERSONAL_ALLOWANCE - (salary - 100000) / 2);
  const taxable = Math.max(0, salary - pa);
  const basic = Math.min(taxable, BASIC_RATE_LIMIT - PERSONAL_ALLOWANCE);
  const higher = Math.max(0, Math.min(taxable - basic, HIGHER_RATE_LIMIT - BASIC_RATE_LIMIT));
  const additional = Math.max(0, taxable - basic - higher);
  return { tax: basic * INCOME_BASIC + higher * INCOME_HIGHER + additional * INCOME_ADDITIONAL, pa };
}

function calcEmployeeNi(salary: number): number {
  if (salary <= NI_PRIMARY) return 0;
  const inBand = Math.min(salary, NI_UPPER) - NI_PRIMARY;
  const above = Math.max(0, salary - NI_UPPER);
  return inBand * NI_BASIC + above * NI_UPPER_RATE;
}

function calcStudentLoan(salary: number, plan: StudentLoanPlan): number {
  const cfg = SL_THRESHOLDS[plan];
  if (cfg.rate === 0) return 0;
  return Math.max(0, salary - cfg.threshold) * cfg.rate;
}

const fmt = (n: number) => `£${Math.round(n).toLocaleString("en-GB")}`;

export function TakeHomePayCalculator() {
  const [salary, setSalary] = useState(45000);
  const [pensionPercent, setPensionPercent] = useState(0);
  const [plan, setPlan] = useState<StudentLoanPlan>("none");

  const result = useMemo(() => {
    const pension = salary * (pensionPercent / 100);
    const salaryAfterPension = salary - pension;
    const incomeTaxObj = calcIncomeTax(salaryAfterPension);
    const ni = calcEmployeeNi(salary);
    const studentLoan = calcStudentLoan(salary, plan);
    const net = salaryAfterPension - incomeTaxObj.tax - ni - studentLoan;
    const totalDeductions = incomeTaxObj.tax + ni + studentLoan + pension;
    const effectiveRate = salary > 0 ? (incomeTaxObj.tax + ni) / salary : 0;
    return {
      pension,
      incomeTax: incomeTaxObj.tax,
      personalAllowance: incomeTaxObj.pa,
      ni,
      studentLoan,
      net,
      totalDeductions,
      effectiveRate,
      monthly: net / 12,
      weekly: net / 52,
    };
  }, [salary, pensionPercent, plan]);

  return (
    <div className="space-y-8">
      <div className="bg-slate-50 border border-slate-200 p-6 sm:p-8">
        <h2 className="text-xl font-bold text-slate-900">Your inputs</h2>

        <div className="mt-6">
          <label htmlFor="salary" className="block text-sm font-bold text-slate-900 mb-2">
            Gross annual salary
          </label>
          <div className="flex items-center gap-3">
            <span className="text-slate-500">£</span>
            <input
              id="salary"
              type="number"
              value={salary}
              onChange={(e) => setSalary(Math.max(0, Number(e.target.value) || 0))}
              min={0}
              max={1000000}
              step={500}
              className="w-48 border border-slate-300 px-3 py-2 text-base text-slate-900 focus:outline-none focus:border-orange-600"
            />
          </div>
          <input
            type="range"
            value={salary}
            onChange={(e) => setSalary(Number(e.target.value))}
            min={10000}
            max={250000}
            step={500}
            className="w-full mt-4 accent-orange-600"
          />
        </div>

        <div className="mt-6 grid sm:grid-cols-2 gap-6">
          <div>
            <label htmlFor="pension" className="block text-sm font-bold text-slate-900 mb-2">
              Pension contribution (salary sacrifice)
            </label>
            <div className="flex items-center gap-2">
              <input
                id="pension"
                type="number"
                value={pensionPercent}
                onChange={(e) => setPensionPercent(Math.max(0, Math.min(50, Number(e.target.value) || 0)))}
                min={0}
                max={50}
                step={0.5}
                className="w-24 border border-slate-300 px-3 py-2 text-base text-slate-900 focus:outline-none focus:border-orange-600"
              />
              <span className="text-slate-500">% of gross</span>
            </div>
          </div>

          <div>
            <label htmlFor="plan" className="block text-sm font-bold text-slate-900 mb-2">
              Student loan plan
            </label>
            <select
              id="plan"
              value={plan}
              onChange={(e) => setPlan(e.target.value as StudentLoanPlan)}
              className="w-full border border-slate-300 px-3 py-2 text-base text-slate-900 focus:outline-none focus:border-orange-600 bg-white"
            >
              <option value="none">None</option>
              <option value="plan1">Plan 1 (pre-2012 England/Wales)</option>
              <option value="plan2">Plan 2 (2012-2023 England/Wales)</option>
              <option value="plan4">Plan 4 (Scotland)</option>
              <option value="plan5">Plan 5 (from Aug 2023)</option>
              <option value="pg">Postgraduate loan</option>
            </select>
          </div>
        </div>
      </div>

      <div className="bg-orange-700 text-white p-6 sm:p-8">
        <p className="text-sm font-bold uppercase tracking-wider text-orange-200">Take-home pay</p>
        <p className="text-4xl sm:text-5xl font-bold font-mono mt-1">{fmt(result.net)}</p>
        <div className="mt-4 grid grid-cols-2 gap-4 pt-4 border-t border-orange-500">
          <div>
            <p className="text-xs text-orange-200 uppercase tracking-wider">Monthly</p>
            <p className="text-2xl font-bold font-mono">{fmt(result.monthly)}</p>
          </div>
          <div>
            <p className="text-xs text-orange-200 uppercase tracking-wider">Weekly</p>
            <p className="text-2xl font-bold font-mono">{fmt(result.weekly)}</p>
          </div>
        </div>
      </div>

      <div className="bg-white border border-slate-200">
        <h3 className="px-6 py-4 text-lg font-bold text-slate-900 border-b border-slate-200">
          The deductions
        </h3>
        <dl className="divide-y divide-slate-200">
          <Row label="Personal allowance" value={fmt(result.personalAllowance)} />
          <Row label="Pension (salary sacrifice)" value={fmt(result.pension)} />
          <Row label="Income tax" value={fmt(result.incomeTax)} />
          <Row label="National Insurance" value={fmt(result.ni)} />
          {result.studentLoan > 0 && <Row label="Student loan" value={fmt(result.studentLoan)} />}
          <Row label="Total deductions" value={fmt(result.totalDeductions)} highlight />
          <Row label="Effective tax rate (income tax + NI)" value={`${(result.effectiveRate * 100).toFixed(1)}%`} />
        </dl>
      </div>
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
