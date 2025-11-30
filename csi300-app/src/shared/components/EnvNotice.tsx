type EnvNoticeProps = {
  label?: string;
};

export function EnvNotice({ label = 'API Base' }: EnvNoticeProps) {
  const apiBase = import.meta.env.VITE_API_BASE || 'not set';
  const appName = import.meta.env.VITE_APP_NAME || 'CSI300 React Shell';

  return (
    <div className="mt-4 rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-700">
      <div className="font-semibold text-slate-900">{appName}</div>
      <div className="flex items-center gap-2">
        <span className="text-slate-600">{label}:</span>
        <code className="rounded bg-white px-2 py-1 text-xs text-slate-900 shadow-sm">
          {apiBase}
        </code>
      </div>
    </div>
  );
}
