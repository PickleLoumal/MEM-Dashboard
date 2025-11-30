import type { PropsWithChildren, ReactNode } from 'react';

type AppShellProps = PropsWithChildren<{
  title?: ReactNode;
  subtitle?: ReactNode;
}>;

export function AppShell({ title, subtitle, children }: AppShellProps) {
  return (
    <div className="app-shell">
      {(title || subtitle) && (
        <header className="mb-6">
          {title ? (
            <h1 className="text-3xl font-bold text-slate-900 leading-tight">{title}</h1>
          ) : null}
          {subtitle ? (
            <p className="text-sm text-slate-600 mt-2 max-w-3xl">{subtitle}</p>
          ) : null}
        </header>
      )}

      <div className="app-card border border-slate-200/80 bg-white p-6 shadow-sm">
        {children}
      </div>
    </div>
  );
}
