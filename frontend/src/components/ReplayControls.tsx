"use client";

interface Props {
  totalTicks: number;
  currentTick: number;
  isPlaying: boolean;
  onTickChange: (tick: number) => void;
  onTogglePlay: () => void;
}

export function ReplayControls({ totalTicks, currentTick, isPlaying, onTickChange, onTogglePlay }: Props) {
  if (totalTicks === 0) return null;

  return (
    <div className="card flex items-center gap-4">
      <button
        onClick={onTogglePlay}
        className="bg-slate-700 hover:bg-slate-600 text-white text-sm font-medium py-1 px-3 rounded transition min-w-[60px]"
      >
        {isPlaying ? "Pause" : "Play"}
      </button>
      <input
        type="range"
        min={0}
        max={totalTicks}
        value={currentTick}
        onChange={(e) => onTickChange(Number(e.target.value))}
        className="flex-1"
      />
      <span className="text-xs font-mono text-slate-400 min-w-[80px] text-right">
        {currentTick} / {totalTicks}
      </span>
    </div>
  );
}
