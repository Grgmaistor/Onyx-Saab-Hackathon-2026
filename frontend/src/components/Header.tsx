"use client";

export function Header({ batchStatus }: { batchStatus?: string }) {
  return (
    <header className="border-b border-slate-800 bg-[#0d1321] px-6 py-3 flex items-center justify-between">
      <div>
        <h1 className="text-lg font-bold tracking-wider text-cyan-400">
          BOREAL PASSAGE
          <span className="text-slate-500 font-normal ml-2 text-sm tracking-normal">
            Simulation Engine
          </span>
        </h1>
      </div>
      <div className="flex items-center gap-4">
        {batchStatus && (
          <span className="badge-running text-xs">{batchStatus}</span>
        )}
        <span className="text-xs text-slate-600 font-mono">v0.1.0</span>
      </div>
    </header>
  );
}
