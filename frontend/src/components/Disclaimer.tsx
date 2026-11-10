export function Disclaimer({ compact = false }: { compact?: boolean }) {
  if (compact) {
    return (
      <p className="text-xs text-slate-400">
        Legal information only — not professional legal advice.
      </p>
    );
  }

  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      <span className="font-semibold">Disclaimer: </span>
      This platform provides <strong>legal information, not professional legal
      advice</strong>. Always consult a qualified lawyer for advice on your
      specific situation.
    </div>
  );
}
