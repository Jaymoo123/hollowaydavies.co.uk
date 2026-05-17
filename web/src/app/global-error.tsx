"use client";

import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.error('Global error boundary caught:', error);
    }
  }, [error]);

  return (
    <html>
      <body>
        <div style={{ 
          minHeight: '100vh', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          padding: '2rem',
          fontFamily: 'system-ui, sans-serif'
        }}>
          <div style={{ maxWidth: '600px', textAlign: 'center' }}>
            <div style={{
              width: '64px',
              height: '64px',
              margin: '0 auto 2rem',
              borderRadius: '50%',
              backgroundColor: '#fee2e2',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <svg style={{ width: '32px', height: '32px', color: '#dc2626' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            
            <h1 style={{ fontSize: '2rem', fontWeight: 'bold', color: '#0f172a', marginBottom: '1rem' }}>
              Application Error
            </h1>
            
            <p style={{ fontSize: '1.125rem', color: '#475569', marginBottom: '2rem' }}>
              A critical error occurred. Please refresh the page or contact support if the problem persists.
            </p>

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
              <button
                onClick={reset}
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: '#4f46e5',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.5rem',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                Try again
              </button>
              <button
                onClick={() => window.location.href = '/'}
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: 'white',
                  color: '#0f172a',
                  border: '2px solid #cbd5e1',
                  borderRadius: '0.5rem',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                Go home
              </button>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}
