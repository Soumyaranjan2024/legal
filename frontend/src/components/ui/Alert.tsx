const TONES: Record<string, string> = {
  info: "border-brand-200 bg-brand-50 text-brand-800",
  success: "border-emerald-200 bg-emerald-50 text-emerald-800",
  warning: "border-amber-200 bg-amber-50 text-amber-800",
  danger: "border-red-200 bg-red-50 text-red-800",
};

export function Alert({
  children,
  tone = "info",
  title,
}: {
  children: React.ReactNode;
  tone?: keyof typeof TONES | string;
  title?: string;
}) {
  return (
    <div
      className={`rounded-lg border px-4 py-3 text-sm ${
        TONES[tone] ?? TONES.info
      }`}
      role="alert"
    >
      {title ? <p className="font-semibold">{title}</p> : null}
      <div className={title ? "mt-1" : ""}>{children}</div>
    </div>
  );
}
