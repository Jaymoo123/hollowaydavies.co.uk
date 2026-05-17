"use client";

import { useState } from "react";

export function Section24Calculator() {
  const [rentalIncome, setRentalIncome] = useState(50000);
  const [mortgageInterest, setMortgageInterest] = useState(20000);
  const [otherExpenses, setOtherExpenses] = useState(8000);
  const [taxBand, setTaxBand] = useState<"basic" | "higher" | "additional">("higher");

  const taxRates = {
    basic: 0.20,
    higher: 0.40,
    additional: 0.45,
  };

  const netProfit = rentalIncome - otherExpenses;
  const taxableProfit = netProfit - mortgageInterest;
  
  const oldSystemTax = taxableProfit * taxRates[taxBand];
  
  const section24TaxableProfit = netProfit;
  const section24TaxBeforeCredit = section24TaxableProfit * taxRates[taxBand];
  const section24TaxCredit = mortgageInterest * 0.20;
  const section24Tax = section24TaxBeforeCredit - section24TaxCredit;
  
  const extraTax = section24Tax - oldSystemTax;
  const extraTaxPerMonth = extraTax / 12;

  return (
    <div className="bg-white border-l-4 border-emerald-600 p-6 sm:p-8 lg:p-10">
      <div className="mb-6 sm:mb-8">
        <div className="inline-block bg-slate-900 px-3 py-1 text-xs font-bold text-white uppercase tracking-wider mb-2 sm:mb-3">
          Calculator
        </div>
        <h3 className="text-xl sm:text-2xl lg:text-3xl font-bold text-slate-900">Section 24 Tax Calculator</h3>
        <p className="mt-2 text-sm sm:text-base text-slate-600">
          Calculate how much extra tax you&apos;re paying due to Section 24 mortgage interest restriction.
        </p>
      </div>

      <div className="grid gap-6 sm:gap-8 lg:grid-cols-[1fr_1.2fr]">
        <div className="space-y-5 sm:space-y-6">
          <div>
            <label htmlFor="rental-income" className="block text-xs sm:text-sm font-bold text-slate-900 uppercase tracking-wider mb-2">
              Annual rental income
            </label>
            <div className="flex items-center gap-2">
              <span className="text-xl sm:text-2xl font-bold text-slate-900">£</span>
              <input
                id="rental-income"
                type="number"
                inputMode="numeric"
                min="0"
                step="1000"
                value={rentalIncome}
                onChange={(e) => setRentalIncome(Number(e.target.value))}
                className="flex-1 border-b-2 border-slate-300 bg-transparent px-2 py-2 sm:py-3 text-xl sm:text-2xl font-bold text-slate-900 focus:border-emerald-600 focus:outline-none transition-colors min-h-[44px]"
              />
            </div>
          </div>

          <div>
            <label htmlFor="mortgage-interest" className="block text-xs sm:text-sm font-bold text-slate-900 uppercase tracking-wider mb-2">
              Annual mortgage interest
            </label>
            <div className="flex items-center gap-2">
              <span className="text-xl sm:text-2xl font-bold text-slate-900">£</span>
              <input
                id="mortgage-interest"
                type="number"
                inputMode="numeric"
                min="0"
                step="1000"
                value={mortgageInterest}
                onChange={(e) => setMortgageInterest(Number(e.target.value))}
                className="flex-1 border-b-2 border-slate-300 bg-transparent px-2 py-2 sm:py-3 text-xl sm:text-2xl font-bold text-slate-900 focus:border-emerald-600 focus:outline-none transition-colors min-h-[44px]"
              />
            </div>
          </div>

          <div>
            <label htmlFor="other-expenses" className="block text-xs sm:text-sm font-bold text-slate-900 uppercase tracking-wider mb-2">
              Other expenses
            </label>
            <div className="flex items-center gap-2">
              <span className="text-xl sm:text-2xl font-bold text-slate-900">£</span>
              <input
                id="other-expenses"
                type="number"
                inputMode="numeric"
                min="0"
                step="1000"
                value={otherExpenses}
                onChange={(e) => setOtherExpenses(Number(e.target.value))}
                className="flex-1 border-b-2 border-slate-300 bg-transparent px-2 py-2 sm:py-3 text-xl sm:text-2xl font-bold text-slate-900 focus:border-emerald-600 focus:outline-none transition-colors min-h-[44px]"
              />
            </div>
          </div>

          <div>
            <label htmlFor="tax-band" className="block text-xs sm:text-sm font-bold text-slate-900 uppercase tracking-wider mb-2">
              Your income tax band
            </label>
            <select
              id="tax-band"
              value={taxBand}
              onChange={(e) => setTaxBand(e.target.value as typeof taxBand)}
              className="w-full border-2 border-slate-300 bg-white px-3 sm:px-4 py-3 text-sm sm:text-base font-semibold text-slate-900 focus:border-emerald-600 focus:outline-none transition-colors min-h-[44px]"
            >
              <option value="basic">Basic rate (20%)</option>
              <option value="higher">Higher rate (40%)</option>
              <option value="additional">Additional rate (45%)</option>
            </select>
          </div>
        </div>

        <div className="bg-slate-900 p-6 sm:p-8 text-white">
          <div className="mb-4 sm:mb-6">
            <div className="text-xs sm:text-sm font-bold text-emerald-400 uppercase tracking-wider mb-2">Your result</div>
            <div className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white font-mono">
              £{extraTax.toLocaleString("en-GB", { maximumFractionDigits: 0 })}
            </div>
            <div className="mt-2 text-xs sm:text-sm text-slate-300 uppercase tracking-wider">Extra tax per year</div>
          </div>

          <div className="border-t border-slate-700 pt-4 sm:pt-6 space-y-3 sm:space-y-4">
            <div className="flex justify-between items-baseline">
              <span className="text-xs sm:text-sm text-slate-300">Per month</span>
              <span className="text-xl sm:text-2xl font-bold text-white">
                £{extraTaxPerMonth.toLocaleString("en-GB", { maximumFractionDigits: 0 })}
              </span>
            </div>
            <div className="flex justify-between items-baseline">
              <span className="text-xs sm:text-sm text-slate-300">Old system tax</span>
              <span className="text-base sm:text-lg font-semibold text-slate-400">
                £{oldSystemTax.toLocaleString("en-GB", { maximumFractionDigits: 0 })}
              </span>
            </div>
            <div className="flex justify-between items-baseline">
              <span className="text-xs sm:text-sm text-slate-300">Section 24 tax</span>
              <span className="text-base sm:text-lg font-semibold text-slate-400">
                £{section24Tax.toLocaleString("en-GB", { maximumFractionDigits: 0 })}
              </span>
            </div>
          </div>

          <div className="mt-6 sm:mt-8 border-t border-slate-700 pt-4 sm:pt-6">
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              This calculator shows the extra tax you pay under Section 24 compared to the old system where full mortgage interest was deductible.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
