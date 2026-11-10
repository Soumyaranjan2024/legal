export function StatCard({
  label,
  value,
  hint,
  tone = "brand",
}: {
  label: string;
  value: string | number;
  hint?: string;
  tone?: "brand" | "emerald" | "amber" | "violet";
}) {
  const tones: Record<string, string> = {
    brand: "text-brand-600",
    emerald: "text-emerald-600",
    amber: "text-amber-600",
    violet: "text-violet-600",
  };

  return (
    <div className="card p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className={`mt-2 text-2xl font-bold ${tones[tone]}`}>{value}</p>
      {hint ? <p className="mt-1 text-xs text-slate-400">{hint}</p> : null}
    </div>
  );
}
