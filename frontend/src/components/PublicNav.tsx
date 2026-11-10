import Link from "next/link";

export function PublicNav() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 lg:px-8">
        <Link href="/" className="flex items-center gap-2">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-600 text-white">
            ⚖
          </span>
          <span className="text-sm font-bold text-slate-800 sm:text-base">
            Legal IR System
          </span>
        </Link>

        <nav className="flex items-center gap-2">
          <Link href="/search" className="btn-secondary">
            Search laws
          </Link>
          <Link href="/chat" className="btn-primary">
            Open AI chatbot
          </Link>
        </nav>
      </div>
    </header>
  );
}
