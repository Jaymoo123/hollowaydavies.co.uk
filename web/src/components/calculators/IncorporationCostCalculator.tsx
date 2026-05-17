"use client";

import { useState } from "react";

export function IncorporationCostCalculator() {
  const [propertyValue, setPropertyValue] = useState(300000);
  const [purchasePrice, setPurchasePrice] = useState(200000);
  const [annualRentalIncome, setAnnualRentalIncome] = useState(24000);
  const [mortgageInterest, setMortgageInterest] = useState(9000);
  const [taxBand, setTaxBand] = useState<"basic" | "higher" | "additional">("higher");

  const capitalGain = Math.max(0, propertyValue - purchasePrice);
  const cgtRate = taxBand === "basic" ? 0.18 : 0.24;
  const cgtCost = capitalGain * cgtRate;
  
  const sdltRate = 0.05;
  const sdltCost = propertyValue * sdltRate;
  
  const totalUpfrontCost = cgtCost + sdltCost;
  
  const personalTaxableProfit = annualRentalIncome;
  const personalTaxRate = taxBand === "basic" ? 0.20 : taxBand === "higher" ? 0.40 : 0.45;
  const personalTaxBeforeCredit = personalTaxableProfit * personalTaxRate;
  const section24Credit = mortgageInterest * 0.20;
  const personalTax = personalTaxBeforeCredit - section24Credit;
  
  const companyProfit = Math.max(0, annualRentalIncome - mortgageInterest);
  const corporationTax = companyProfit * 0.19;
  const dividendAfterCorpTax = companyProfit - corporationTax;
  const dividendTaxRate = taxBand === "basic" ? 0.0875 : taxBand === "higher" ? 0.3375 : 0.3935;
  const dividendTax = dividendAfterCorpTax * dividendTaxRate;
  const totalCompanyTax = corporationTax + dividendTax;
  
  const annualSaving = personalTax - totalCompanyTax;
  const breakEvenYears = annualSaving > 0 ? totalUpfrontCost / annualSaving : 999;

  return (
    <div className="bg-white border-l-4 border-emerald-600 p-6 sm:p-8 lg:p-10">
      <div className="mb-6 sm:mb-8">
        <div className="inline-block bg-slate-900 px-3 py-1 text-xs font-bold text-white uppercase tracking-wider mb-2 sm:mb-3">
          Calculator
        </div>
        <h3 className="text-xl sm:text-2xl lg:text-3xl font-bold text-slate-900">Incorporation Cost Calculator</h3>
        <p className="mt-2 text-sm sm:text-base text-slate-600">
          Calculate the upfront cost (CGT + SDLT) and break-even timeline for incorporating your rental property.
        </p>
      </div>

      <div className="grid gap-6 sm:gap-8 lg:grid-cols-[1fr_1.2fr]">
        <div className="space-y-5 sm:space-y-6">
          <div>
            <label htmlFor="property-value" className="block text-xs sm:text-sm font-bold text-slate-900 uppercase tracking-wider mb-2">
              Current property value
            </label>
            <div className="flex items-center gap-2">
              <span className="text-xl sm:text-2xl font-bold text-slate-900">£</span>
              <input
                id="property-value"
                type="number"
                inputMode="numeric"
                min="0"
                step="10000"
                value={propertyValue}
                onChange={(e) => setPropertyValue(Number(e.target.value))}
                className="flex-1 border-b-2 border-slate-300 bg-transparent px-2 py-2 sm:py-3 text-xl sm:text-2xl font-bold text-slate-900 focus:border-emerald-600 focus:outline-none transition-colors min-h-[44px]"
              />
            </div>
          </div>

          <div>
            <label htmlFor="purchase-price" className="block text-xs sm:text-sm font-bold text-slate-900 uppercase tracking-wider mb-2">
              Original purchase price
            </label>
            <div className="flex items-center gap-2">
              <span className="text-xl sm:text-2xl font-bold text-slate-900">£</span>
              <input
                id="purchase-price"
                type="number"
                inputMode="numeric"
                min="0"
                step="10000"
                value={purchasePrice}
                onChange={(e) => setPurchasePrice(Number(e.target.value))}
                className="flex-1 border-b-2 border-slate-300 bg-transparent px-2 py-2 sm:py-3 text-xl sm:text-2xl font-bold text-slate-900 focus:border-emerald-600 focus:outline-none transition-colors min-h-[44px]"
              />
            </div>
          </div>

          <div>
            <label htmlFor="rental-income-inc" className="block text-xs sm:text-sm font-bold text-slate-900 uppercase tracking-wider mb-2">
              Annual rental income
            </label>
            <div className="flex items-center gap-2">
              <span className="text-xl sm:text-2xl font-bold text-slate-900">£</span>
              <input
                id="rental-income-inc"
                type="number"
                inputMode="numeric"
                min="0"
                step="1000"
                value={annualRentalIncome}
                onChange={(e) => setAnnualRentalIncome(Number(e.target.value))}
                className="flex-1 border-b-2 border-slate-300 bg-transparent px-2 py-2 sm:py-3 text-xl sm:text-2xl font-bold text-slate-900 focus:border-emerald-600 focus:outline-none transition-colors min-h-[44px]"
              />
            </div>
          </div>

          <div>
            <label htmlFor="mortgage-interest-inc" className="block text-xs sm:text-sm font-bold text-slate-900 uppercase tracking-wider mb-2">
              Annual mortgage interest
            </label>
            <div className="flex items-center gap-2">
              <span className="text-xl sm:text-2xl font-bold text-slate-900">£</span>
              <input
                id="mortgage-interest-inc"
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
            <label htmlFor="tax-band-inc" className="block text-xs sm:text-sm font-bold text-slate-900 uppercase tracking-wider mb-2">
              Your income tax band
            </label>
            <select
              id="tax-band-inc"
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

        <div className="bg-slate-900 p-6 sm:p-8 text-white space-y-6 sm:space-y-8">
          <div>
            <div className="text-xs sm:text-sm font-bold text-amber-400 uppercase tracking-wider mb-2">Upfront cost</div>
            <div className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white font-mono">
              £{totalUpfrontCost.toLocaleString("en-GB", { maximumFractionDigits: 0 })}
            </div>
            <div className="mt-3 sm:mt-4 space-y-2 text-xs sm:text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">CGT ({(cgtRate * 100).toFixed(0)}%)</span>
                <span className="font-semibold text-slate-300">£{cgtCost.toLocaleString("en-GB", { maximumFractionDigits: 0 })}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">SDLT (5%)</span>
                <span className="font-semibold text-slate-300">£{sdltCost.toLocaleString("en-GB", { maximumFractionDigits: 0 })}</span>
              </div>
            </div>
          </div>

          <div className="border-t border-slate-700 pt-4 sm:pt-6">
            <div className="text-xs sm:text-sm font-bold text-emerald-400 uppercase tracking-wider mb-2">Annual saving</div>
            <div className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white font-mono">
              £{annualSaving.toLocaleString("en-GB", { maximumFractionDigits: 0 })}
            </div>
            <div className="mt-2 text-xs sm:text-sm text-slate-300">per year after incorporating</div>
          </div>

          <div className="border-t border-slate-700 pt-4 sm:pt-6">
            <div className="text-xs sm:text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Break-even</div>
            <div className="text-2xl sm:text-3xl font-bold text-white font-mono">
              {breakEvenYears < 50 ? `${breakEvenYears.toFixed(1)} years` : "Never"}
            </div>
            <div className="mt-2 text-xs sm:text-sm text-slate-300">
              {breakEvenYears < 50 
                ? "Time to recover upfront costs"
                : "Annual saving too low to justify incorporation"}
            </div>
          </div>

          <div className="border-t border-slate-700 pt-4 sm:pt-6">
            <p className="text-xs text-slate-400 leading-relaxed">
              Simplified estimate. Actual costs depend on your specific circumstances and require full feasibility analysis.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
