"use client";

import { useMemo, useState } from "react";

/**
 * UK R&D Tax Credit estimator (SME scheme, post-April 2023 merged scheme).
 *
 * 2025/26 rules used here:
 *  - Merged R&D scheme: 20% above-the-line credit on qualifying expenditure
 *  - For "R&D intensive" SMEs (40%+ of total expenditure is R&D), enhanced 27% rate
 *  - This is a simplified directional estimate. Actual claims involve scoping,
 *    contractor restrictions (65% of subcontractor cost), PAYE-NI cap, and
 *    consumables / software / cloud apportionment rules we don't model here.
 */

const RDEC_RATE = 0.20;            // standard merged scheme
const RD_INTENSIVE_RATE = 0.27;    // R&D intensive SME rate
const RD_INTENSIVE_THRESHOLD = 0.40;
const SUBCONTRACTOR_HAIRCUT = 0.65; // claim 65% of subcontractor cost

const fmt = (n: number) => `£${Math.round(n).toLocaleString("en-GB")}`;

export function RDCreditEstimator() {
  const [totalExpenditure, setTotalExpenditure] = useState(800000);
  const [staffCost, setStaffCost] = useState(120000);
  const [subcontractorCost, setSubcontractorCost] = useState(40000);
  const [consumablesCost, setConsumablesCost] = useState(15000);
  const [softwareCost, setSoftwareCost] = useState(25000);

  const qualifying = useMemo(() => {
    return staffCost + (subcontractorCost * SUBCONTRACTOR_HAIRCUT) + consumablesCost + softwareCost;
  }, [staffCost, subcontractorCost, consumablesCost, softwareCost]);

  const intensityRatio = totalExpenditure > 0 ? qualifying / totalExpenditure : 0;
  const isIntensive = intensityRatio >= RD_INTENSIVE_THRESHOLD;
  const creditRate = isIntensive ? RD_INTENSIVE_RATE : RDEC_RATE;
  const grossCredit = qualifying * creditRate;

  // The above-the-line credit is taxable, so the net benefit depends on CT rate.
  // Most SMEs hit ~25% marginal rate above £50k profits; we'll use a simple
  // estimate of net = gross × (1 - 0.25) as a guide.
  const netBenefit = grossCredit * (1 - 0.25);

  return (
    <div className="space-y-8">
      <div className="bg-slate-50 border border-slate-200 p-6 sm:p-8">
        <h2 className="text-xl font-bold text-slate-900">Your R&D spend (2025/26)</h2>
        <p className="mt-2 text-sm text-slate-600">
          Enter the components of your R&D-qualifying expenditure. Only include staff time, subcontractor cost, consumables and software/cloud genuinely used for R&D activity.
        </p>

        <div className="mt-6 space-y-5">
          <FieldGroup
            id="total"
            label="Total business expenditure"
            help="All expenditure for the year. Used to test R&D intensity."
            value={totalExpenditure}
            setValue={setTotalExpenditure}
            max={5000000}
          />
          <FieldGroup
            id="staff"
            label="Staff time on R&D (gross cost)"
            help="Gross salary + employer NI + pension of staff doing qualifying R&D, apportioned."
            value={staffCost}
            setValue={setStaffCost}
            max={3000000}
          />
          <FieldGroup
            id="sub"
            label="Subcontractor R&D cost"
            help="UK subcontractor invoices for R&D work. HMRC caps claim at 65% of this."
            value={subcontractorCost}
            setValue={setSubcontractorCost}
            max={1000000}
          />
          <FieldGroup
            id="cons"
            label="Consumables for R&D"
            help="Materials, prototypes, items consumed in the R&D process."
            value={consumablesCost}
            setValue={setConsumablesCost}
            max={500000}
          />
          <FieldGroup
            id="sw"
            label="Software / cloud for R&D"
            help="SaaS licences, cloud compute (AWS, GCP), GPU rental used for R&D work."
            value={softwareCost}
            setValue={setSoftwareCost}
            max={500000}
          />
        </div>
      </div>

      <div className="bg-orange-700 text-white p-6 sm:p-8">
        <p className="text-sm font-bold uppercase tracking-wider text-orange-200">Estimated R&D credit</p>
        <div className="mt-3 grid sm:grid-cols-2 gap-6">
          <div>
            <p className="text-xs text-orange-200 uppercase tracking-wider">Gross credit (above-the-line)</p>
            <p className="text-3xl sm:text-4xl font-bold font-mono">{fmt(grossCredit)}</p>
          </div>
          <div>
            <p className="text-xs text-orange-200 uppercase tracking-wider">Net benefit (after CT)</p>
            <p className="text-3xl sm:text-4xl font-bold font-mono">{fmt(netBenefit)}</p>
          </div>
        </div>
        <div className="mt-6 pt-6 border-t border-orange-500 text-sm text-orange-100">
          <p>
            Rate applied: <strong className="font-bold">{(creditRate * 100).toFixed(0)}%</strong>
            {isIntensive ? " (R&D intensive: qualifying spend is 40%+ of total)" : " (standard merged scheme)"}
          </p>
          <p className="mt-2">
            Qualifying expenditure: <strong className="font-bold">{fmt(qualifying)}</strong> ({(intensityRatio * 100).toFixed(1)}% of total)
          </p>
        </div>
      </div>

      <div className="bg-white border border-slate-200 p-6">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700">How the calculation works</h3>
        <ol className="mt-3 space-y-2 text-sm text-slate-600">
          <li><strong>1. Qualifying expenditure</strong> = staff R&D + 65% of subcontractors + consumables + software</li>
          <li><strong>2. Credit rate</strong> = 20% standard, or 27% if R&D spend is 40%+ of total expenditure</li>
          <li><strong>3. Gross credit</strong> = qualifying expenditure × credit rate</li>
          <li><strong>4. Net benefit</strong> = gross credit × (1 - 25% corporation tax) = the cash impact</li>
        </ol>
        <p className="mt-4 text-xs text-slate-500">
          Directional estimate only. Actual claims involve scoping, PAYE/NI cap (where applicable), apportionment of staff time, and specific qualifying-activity tests. Book a free call for a tailored assessment.
        </p>
      </div>
    </div>
  );
}

type FieldProps = {
  id: string;
  label: string;
  help: string;
  value: number;
  setValue: (v: number) => void;
  max: number;
};

function FieldGroup({ id, label, help, value, setValue, max }: FieldProps) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-bold text-slate-900">{label}</label>
      <p className="text-xs text-slate-500 mt-0.5">{help}</p>
      <div className="mt-2 flex items-center gap-2">
        <span className="text-slate-500">£</span>
        <input
          id={id}
          type="number"
          value={value}
          onChange={(e) => setValue(Math.max(0, Number(e.target.value) || 0))}
          min={0}
          max={max}
          step={1000}
          className="w-40 border border-slate-300 px-3 py-2 text-base text-slate-900 focus:outline-none focus:border-orange-600"
        />
      </div>
    </div>
  );
}
