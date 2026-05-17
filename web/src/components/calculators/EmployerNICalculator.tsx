"use client";

import { useMemo, useState } from "react";
import { UK_TAX_RATES as T } from "@/lib/uk-tax-rates";

// All employer NI rates and thresholds pulled from lib/uk-tax-rates.ts
// (canonical source, updated annually). Annotated as `number` to widen the
// literal types `as const` infers in the source file.
const SECONDARY_THRESHOLD: number = T.nationalInsurance.employer.secondaryThreshold;
const EMPLOYER_NI_RATE: number = T.nationalInsurance.employer.rate;
const EMPLOYMENT_ALLOWANCE: number = T.nationalInsurance.employer.employmentAllowance;
// Auto-enrolment minimum pension qualifying earnings band lower limit
// (stable since 2014; review annually with The Pensions Regulator).
const PENSION_MIN_QUALIFYING = 6240;
const PENSION_EMPLOYER_MIN_RATE = 0.03;

type Employee = {
  id: number;
  role: string;
  salary: number;
};

const seedEmployees: Employee[] = [
  { id: 1, role: "Office manager", salary: 38000 },
  { id: 2, role: "Senior bookkeeper", salary: 32000 },
];

const fmt = (n: number) => `£${Math.round(n).toLocaleString("en-GB")}`;

function calcEmployerNi(salary: number): number {
  if (salary <= SECONDARY_THRESHOLD) return 0;
  return (salary - SECONDARY_THRESHOLD) * EMPLOYER_NI_RATE;
}

function calcMinPensionEmployer(salary: number): number {
  if (salary <= PENSION_MIN_QUALIFYING) return 0;
  return (salary - PENSION_MIN_QUALIFYING) * PENSION_EMPLOYER_MIN_RATE;
}

export function EmployerNICalculator() {
  const [employees, setEmployees] = useState<Employee[]>(seedEmployees);
  const [useEA, setUseEA] = useState(true);
  const [includePension, setIncludePension] = useState(true);

  const summary = useMemo(() => {
    const grossSalaryTotal = employees.reduce((sum, e) => sum + e.salary, 0);
    const niPerEmployee = employees.map((e) => calcEmployerNi(e.salary));
    const niTotal = niPerEmployee.reduce((a, b) => a + b, 0);
    const eaApplied = useEA && employees.length >= 2 ? Math.min(EMPLOYMENT_ALLOWANCE, niTotal) : 0;
    const niAfterEA = Math.max(0, niTotal - eaApplied);
    const pensionTotal = includePension
      ? employees.reduce((sum, e) => sum + calcMinPensionEmployer(e.salary), 0)
      : 0;
    const totalEmploymentCost = grossSalaryTotal + niAfterEA + pensionTotal;
    return {
      grossSalaryTotal,
      niTotal,
      eaApplied,
      niAfterEA,
      pensionTotal,
      totalEmploymentCost,
      monthlyTotal: totalEmploymentCost / 12,
      eaEligibleWarning: useEA && employees.length < 2,
    };
  }, [employees, useEA, includePension]);

  function updateEmployee(id: number, patch: Partial<Employee>) {
    setEmployees((prev) => prev.map((e) => (e.id === id ? { ...e, ...patch } : e)));
  }

  function addEmployee() {
    const nextId = (employees.at(-1)?.id ?? 0) + 1;
    setEmployees([...employees, { id: nextId, role: "New role", salary: 35000 }]);
  }

  function removeEmployee(id: number) {
    setEmployees((prev) => prev.filter((e) => e.id !== id));
  }

  return (
    <div className="space-y-8">
      <div className="bg-slate-50 border border-slate-200 p-6 sm:p-8">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-slate-900">Your team</h2>
          <button
            type="button"
            onClick={addEmployee}
            className="bg-orange-600 px-4 py-2 text-sm font-bold text-white border-b-2 border-orange-800 hover:bg-orange-700 transition-colors"
          >
            + Add employee
          </button>
        </div>

        <div className="mt-6 space-y-3">
          {employees.map((e) => (
            <div key={e.id} className="grid grid-cols-1 sm:grid-cols-[2fr_1fr_auto] gap-3 items-end bg-white p-4 border border-slate-200">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Role</label>
                <input
                  type="text"
                  value={e.role}
                  onChange={(ev) => updateEmployee(e.id, { role: ev.target.value })}
                  className="w-full border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:outline-none focus:border-orange-600"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Gross salary</label>
                <div className="flex items-center gap-1">
                  <span className="text-slate-500 text-sm">£</span>
                  <input
                    type="number"
                    value={e.salary}
                    onChange={(ev) => updateEmployee(e.id, { salary: Math.max(0, Number(ev.target.value) || 0) })}
                    min={0}
                    step={500}
                    className="w-full border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:outline-none focus:border-orange-600"
                  />
                </div>
              </div>
              <button
                type="button"
                onClick={() => removeEmployee(e.id)}
                className="text-rose-700 text-sm hover:underline disabled:opacity-30 disabled:no-underline"
                disabled={employees.length <= 1}
              >
                Remove
              </button>
            </div>
          ))}
        </div>

        <div className="mt-6 space-y-3">
          <label className="flex items-start gap-3">
            <input
              type="checkbox"
              checked={useEA}
              onChange={(e) => setUseEA(e.target.checked)}
              className="mt-1 h-4 w-4 accent-orange-600"
            />
            <span className="text-sm text-slate-700">
              <span className="font-semibold text-slate-900">Apply Employment Allowance</span> (£5,000 off employer NI). Requires at least two employees on the payroll, single-director-only companies do not qualify.
            </span>
          </label>
          <label className="flex items-start gap-3">
            <input
              type="checkbox"
              checked={includePension}
              onChange={(e) => setIncludePension(e.target.checked)}
              className="mt-1 h-4 w-4 accent-orange-600"
            />
            <span className="text-sm text-slate-700">
              <span className="font-semibold text-slate-900">Include minimum auto-enrolment pension</span> (3% employer contribution on qualifying earnings)
            </span>
          </label>
        </div>

        {summary.eaEligibleWarning && (
          <p className="mt-4 text-sm text-amber-800 bg-amber-50 border-l-4 border-amber-500 p-3">
            With only one employee, Employment Allowance has not been applied. Add a second employee or untick the box to remove this warning.
          </p>
        )}
      </div>

      <div className="bg-orange-700 text-white p-6 sm:p-8">
        <p className="text-sm font-bold uppercase tracking-wider text-orange-200">Total annual employment cost</p>
        <p className="text-4xl sm:text-5xl font-bold font-mono mt-1">{fmt(summary.totalEmploymentCost)}</p>
        <p className="mt-2 text-sm text-orange-200">
          That is {fmt(summary.monthlyTotal)} per month across the team.
        </p>
      </div>

      <div className="bg-white border border-slate-200">
        <h3 className="px-6 py-4 text-lg font-bold text-slate-900 border-b border-slate-200">
          The cost breakdown
        </h3>
        <dl className="divide-y divide-slate-200">
          <Row label="Gross salaries" value={fmt(summary.grossSalaryTotal)} />
          <Row label="Employer NI (gross)" value={fmt(summary.niTotal)} />
          {summary.eaApplied > 0 && <Row label="Less Employment Allowance" value={`-${fmt(summary.eaApplied)}`} />}
          <Row label="Employer NI (net)" value={fmt(summary.niAfterEA)} />
          {includePension && <Row label="Pension (minimum 3% employer)" value={fmt(summary.pensionTotal)} />}
          <Row label="Total employment cost" value={fmt(summary.totalEmploymentCost)} highlight />
        </dl>
        <p className="px-6 py-4 text-xs text-slate-500 border-t border-slate-200">
          Does not include employee benefits, software per seat, equipment, training, or recruitment fees. Real all-in cost per hire typically adds 10-20% on top of the figures above.
        </p>
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
