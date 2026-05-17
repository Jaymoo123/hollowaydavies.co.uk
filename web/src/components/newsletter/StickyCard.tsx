"use client";

import { useEffect, useState } from "react";
import { SignupForm } from "./SignupForm";

const DISMISS_KEY = "aff:newsletter:dismissed";
const DISMISS_DAYS = 30;

/**
 * Bottom-right sticky card prompting newsletter signup.
 * Auto-shows after 20s on page or 50% scroll, whichever comes first.
 * Dismissal remembered for 30 days via localStorage.
 */
export function StickyCard() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const raw = window.localStorage.getItem(DISMISS_KEY);
      if (raw) {
        const ts = parseInt(raw, 10);
        if (!Number.isNaN(ts) && Date.now() - ts < DISMISS_DAYS * 86400 * 1000) {
          return;
        }
      }
    } catch {
      /* ignore */
    }

    let triggered = false;
    const trigger = () => {
      if (triggered) return;
      triggered = true;
      setOpen(true);
    };

    const t = window.setTimeout(trigger, 20000);
    const onScroll = () => {
      const pct =
        (window.scrollY + window.innerHeight) /
        document.documentElement.scrollHeight;
      if (pct > 0.5) trigger();
    };
    window.addEventListener("scroll", onScroll, { passive: true });

    return () => {
      window.clearTimeout(t);
      window.removeEventListener("scroll", onScroll);
    };
  }, []);

  function dismiss() {
    setOpen(false);
    try {
      window.localStorage.setItem(DISMISS_KEY, String(Date.now()));
    } catch {
      /* ignore */
    }
  }

  if (!open) return null;

  return (
    <div
      role="complementary"
      aria-label="Subscribe to The Director's Brief"
      className="fixed bottom-4 right-4 z-40 w-[360px] max-w-[calc(100vw-2rem)]"
    >
      <div className="relative">
        <button
          type="button"
          aria-label="Close"
          onClick={dismiss}
          className="absolute right-2 top-2 z-10 rounded-md bg-white p-1 text-slate-500 hover:bg-slate-100"
        >
          <svg viewBox="0 0 20 20" width="16" height="16" fill="currentColor">
            <path d="M6.293 6.293a1 1 0 011.414 0L10 8.586l2.293-2.293a1 1 0 111.414 1.414L11.414 10l2.293 2.293a1 1 0 01-1.414 1.414L10 11.414l-2.293 2.293a1 1 0 01-1.414-1.414L8.586 10 6.293 7.707a1 1 0 010-1.414z" />
          </svg>
        </button>
        <SignupForm
          variant="card"
          source="sticky-card"
          heading="The Director's Brief"
          body="Weekly UK tax for businesses of every shape."
          ctaLabel="Subscribe"
          showAgencyType={false}
        />
      </div>
    </div>
  );
}
