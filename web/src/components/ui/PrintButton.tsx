"use client";

import { Printer } from "lucide-react";

export function PrintButton() {
  return (
    <button
      type="button"
      onClick={() => {
        if (typeof window !== "undefined") window.print();
      }}
      className="inline-flex items-center gap-2 bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 text-sm font-bold transition-colors flex-shrink-0"
    >
      <Printer className="h-4 w-4" />
      Print / Save as PDF
    </button>
  );
}
