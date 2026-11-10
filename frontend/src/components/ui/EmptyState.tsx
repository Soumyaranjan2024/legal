export function EmptyState({
  title,
  description,
  icon = "📄",
}: {
  title: string;
  description?: string;
  icon?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-white/60 px-6 py-14 text-center">
      <div className="mb-3 text-3xl" aria-hidden>
        {icon}
      </div>
      <p className="text-base font-semibold text-slate-800">{title}</p>
      {description ? (
        <p className="mt-1 max-w-md text-sm text-slate-500">{description}</p>
      ) : null}
    </div>
  );
}
