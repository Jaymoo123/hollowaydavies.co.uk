"use client";

import { useEffect, useState } from "react";
import { SignupForm } from "./SignupForm";

const SHOWN_KEY = "aff:newsletter:exit-shown";
const SHOWN_DAYS = 30;

/**
 * Exit-intent newsletter modal. Triggers on the first significant cursor-out-of-viewport
 * event (desktop) or after 60s of idle (mobile). Once per 30-day window per browser.
 */
export function ExitIntentModal() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const raw = window.localStorage.getItem(SHOWN_KEY);
      if (raw) {
        const ts = parseInt(raw, 10);
        if (!Number.isNaN(ts) && Date.now() - ts < SHOWN_DAYS * 86400 * 1000) {
          return;
        }
      }
    } catch {
      /* ignore */
    }

    let shown = false;
    const trigger = () => {
      if (shown) return;
      shown = true;
      setOpen(true);
      try {
        window.localStorage.setItem(SHOWN_KEY, String(Date.now()));
      } catch {
        /* ignore */
      }
    };

    function onMouseLeave(e: MouseEvent) {
      if (e.clientY <= 0) trigger();
    }
    const idle = window.setTimeout(trigger, 60000);
    document.addEventListener("mouseleave", onMouseLeave);
    return () => {
      document.removeEventListener("mouseleave", onMouseLeave);
      window.clearTimeout(idle);
    };
  }, []);

  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Subscribe to the newsletter"
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4"
      onClick={() => setOpen(false)}
    >
      <div
        className="w-full max-w-md"
        onClick={(e) => e.stopPropagation()}
      >
        <SignupForm
          variant="card"
          source="exit-intent"
          heading="Before you go"
          body="One short email a week on UK tax for limited companies, contractors and sole traders. Plain text, one CTA, unsubscribe one click. The first email lands today."
          ctaLabel="Subscribe to the Director's Brief"
        />
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="mx-auto mt-3 block text-sm text-white/80 hover:text-white"
        >
          No thanks
        </button>
      </div>
    </div>
  );
}
