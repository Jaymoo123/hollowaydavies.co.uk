"use client";

import { useState, useRef } from "react";

interface Property {
  id: string;
  name: string;
  rentalIncome: number;
  mortgageInterest: number;
  otherExpenses: number;
}

export function PortfolioProfitabilityCalculator() {
  const nextId = useRef(3);
  const [properties, setProperties] = useState<Property[]>([
    { id: "1", name: "Property 1", rentalIncome: 18000, mortgageInterest: 7200, otherExpenses: 3000 },
    { id: "2", name: "Property 2", rentalIncome: 24000, mortgageInterest: 9600, otherExpenses: 4000 },
  ]);

  const addProperty = () => {
    const newId = String(nextId.current++);
    setProperties([
      ...properties,
      { id: newId, name: `Property ${properties.length + 1}`, rentalIncome: 18000, mortgageInterest: 7200, otherExpenses: 3000 },
    ]);
  };

  const removeProperty = (id: string) => {
    if (properties.length > 1) {
      setProperties(properties.filter((p) => p.id !== id));
    }
  };

  const updateProperty = (id: string, field: keyof Property, value: string | number) => {
    setProperties(properties.map((p) => (p.id === id ? { ...p, [field]: value } : p)));
  };

  const calculateMetrics = (prop: Property) => {
    const netProfit = prop.rentalIncome - prop.mortgageInterest - prop.otherExpenses;
    const grossYield = (prop.rentalIncome / 250000) * 100;
    const netYield = (netProfit / 250000) * 100;
    return { netProfit, grossYield, netYield };
  };

  const totalRentalIncome = properties.reduce((sum, p) => sum + p.rentalIncome, 0);
  const totalMortgageInterest = properties.reduce((sum, p) => sum + p.mortgageInterest, 0);
  const totalOtherExpenses = properties.reduce((sum, p) => sum + p.otherExpenses, 0);
  const totalNetProfit = totalRentalIncome - totalMortgageInterest - totalOtherExpenses;
  const averageGrossYield = (totalRentalIncome / (properties.length * 250000)) * 100;
  const averageNetYield = (totalNetProfit / (properties.length * 250000)) * 100;

  return (
    <div className="bg-white border-l-4 border-emerald-600 p-6 sm:p-8 lg:p-10">
      <div className="mb-6 sm:mb-8">
        <div className="inline-block bg-slate-900 px-3 py-1 text-xs font-bold text-white uppercase tracking-wider mb-2 sm:mb-3">
          Calculator
        </div>
        <h3 className="text-xl sm:text-2xl lg:text-3xl font-bold text-slate-900">Portfolio Profitability Calculator</h3>
        <p className="mt-2 text-sm sm:text-base text-slate-600">
          Analyse property-level profitability across your portfolio. Assumes £250k property value for yield calculations.
        </p>
      </div>

      <div className="space-y-5 sm:space-y-6">
        {properties.map((prop, idx) => {
          const metrics = calculateMetrics(prop);
          return (
            <div key={prop.id} className="border-2 border-slate-200 bg-slate-50 p-6">
              <div className="flex items-center justify-between mb-4">
                <input
                  type="text"
                  value={prop.name}
                  onChange={(e) => updateProperty(prop.id, "name", e.target.value)}
                  className="border-0 bg-transparent text-xl font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:ring-offset-2 rounded px-1"
                  aria-label={`Property ${idx + 1} name`}
                />
                {properties.length > 1 && (
                  <button
                    onClick={() => removeProperty(prop.id)}
                    className="text-xs font-bold text-red-600 hover:text-red-700 focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2 rounded px-2 py-1 uppercase tracking-wider"
                    aria-label={`Remove ${prop.name}`}
                  >
                    Remove
                  </button>
                )}
              </div>

              <div className="grid gap-4 sm:grid-cols-3 mb-4">
                <div>
                  <label htmlFor={`rental-${prop.id}`} className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                    Rental income
                  </label>
                  <div className="flex items-center gap-2">
                    <span className="text-base sm:text-lg font-bold text-slate-900">£</span>
                    <input
                      id={`rental-${prop.id}`}
                      type="number"
                      min="0"
                      step="1000"
                      value={prop.rentalIncome}
                      onChange={(e) => updateProperty(prop.id, "rentalIncome", Number(e.target.value))}
                      className="flex-1 border-b-2 border-slate-300 bg-transparent px-2 py-2 text-base sm:text-lg font-bold text-slate-900 focus:border-emerald-600 focus:outline-none transition-colors min-h-[44px]"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor={`mortgage-${prop.id}`} className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                    Mortgage interest
                  </label>
                  <div className="flex items-center gap-2">
                    <span className="text-base sm:text-lg font-bold text-slate-900">£</span>
                    <input
                      id={`mortgage-${prop.id}`}
                      type="number"
                      min="0"
                      step="1000"
                      value={prop.mortgageInterest}
                      onChange={(e) => updateProperty(prop.id, "mortgageInterest", Number(e.target.value))}
                      className="flex-1 border-b-2 border-slate-300 bg-transparent px-2 py-2 text-base sm:text-lg font-bold text-slate-900 focus:border-emerald-600 focus:outline-none transition-colors min-h-[44px]"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor={`expenses-${prop.id}`} className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                    Other expenses
                  </label>
                  <div className="flex items-center gap-2">
                    <span className="text-base sm:text-lg font-bold text-slate-900">£</span>
                    <input
                      id={`expenses-${prop.id}`}
                      type="number"
                      min="0"
                      step="1000"
                      value={prop.otherExpenses}
                      onChange={(e) => updateProperty(prop.id, "otherExpenses", Number(e.target.value))}
                      className="flex-1 border-b-2 border-slate-300 bg-transparent px-2 py-2 text-base sm:text-lg font-bold text-slate-900 focus:border-emerald-600 focus:outline-none transition-colors min-h-[44px]"
                    />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 sm:gap-4 bg-white p-3 sm:p-4 text-center border-l-4 border-slate-300">
                <div>
                  <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Net profit</div>
                  <div
                    className={`mt-1 font-mono text-base sm:text-xl font-bold ${
                      metrics.netProfit >= 0 ? "text-emerald-600" : "text-red-600"
                    }`}
                  >
                    £{metrics.netProfit.toLocaleString("en-GB", { maximumFractionDigits: 0 })}
                  </div>
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Gross yield</div>
                  <div className="mt-1 font-mono text-base sm:text-xl font-bold text-slate-900">
                    {metrics.grossYield.toFixed(1)}%
                  </div>
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Net yield</div>
                  <div
                    className={`mt-1 font-mono text-base sm:text-xl font-bold ${
                      metrics.netYield >= 0 ? "text-emerald-600" : "text-red-600"
                    }`}
                  >
                    {metrics.netYield.toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          );
        })}

        <button
          onClick={addProperty}
          className="w-full border-2 border-dashed border-slate-300 bg-slate-50 py-3 sm:py-4 text-sm sm:text-base font-bold text-slate-700 transition-colors hover:border-emerald-600 hover:bg-emerald-50 hover:text-emerald-700 min-h-[44px]"
        >
          + Add another property
        </button>
      </div>

      <div className="mt-8 sm:mt-10 bg-slate-900 p-6 sm:p-8 text-white">
        <h4 className="text-base sm:text-lg font-bold text-white mb-4 sm:mb-6 uppercase tracking-wider">Portfolio summary</h4>
        <div className="grid gap-4 sm:gap-6 grid-cols-2 lg:grid-cols-4">
          <div>
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Total income</div>
            <div className="font-mono text-lg sm:text-2xl font-bold text-white">
              £{totalRentalIncome.toLocaleString("en-GB", { maximumFractionDigits: 0 })}
            </div>
          </div>
          <div>
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Total profit</div>
            <div
              className={`font-mono text-lg sm:text-2xl font-bold ${
                totalNetProfit >= 0 ? "text-emerald-400" : "text-red-400"
              }`}
            >
              £{totalNetProfit.toLocaleString("en-GB", { maximumFractionDigits: 0 })}
            </div>
          </div>
          <div>
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Avg gross yield</div>
            <div className="font-mono text-lg sm:text-2xl font-bold text-white">{averageGrossYield.toFixed(1)}%</div>
          </div>
          <div>
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Avg net yield</div>
            <div
              className={`font-mono text-lg sm:text-2xl font-bold ${
                averageNetYield >= 0 ? "text-emerald-400" : "text-red-400"
              }`}
            >
              {averageNetYield.toFixed(1)}%
            </div>
          </div>
        </div>
        <div className="mt-6 border-t border-slate-700 pt-6">
          <p className="text-xs text-slate-400 leading-relaxed">
            Simplified analysis. Actual profitability depends on property valuations, void periods, maintenance costs, and your personal tax position.
          </p>
        </div>
      </div>
    </div>
  );
}
