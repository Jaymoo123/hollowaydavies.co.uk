import type { ReactNode } from "react";
import { SiteFooter } from "./SiteFooter";
import { SiteHeader } from "./SiteHeader";
import { StickyCTA } from "@/components/ui/StickyCTA";
import { ExitIntentModal } from "@/components/newsletter/ExitIntentModal";

type PageShellProps = {
  children: ReactNode;
};

export function PageShell({ children }: PageShellProps) {
  return (
    <div className="flex min-h-dvh min-w-0 flex-col overflow-x-clip bg-white">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded focus:bg-orange-600 focus:px-3 focus:py-2 focus:text-white"
      >
        Skip to content
      </a>
      <SiteHeader />
      <main id="main" className="flex-1">
        {children}
      </main>
      <SiteFooter />
      <StickyCTA />
      <ExitIntentModal />
    </div>
  );
}
