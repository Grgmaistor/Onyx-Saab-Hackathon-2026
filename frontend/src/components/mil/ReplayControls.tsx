"use client";

export const PLAYBACK_SPEEDS = [0.25, 0.5, 1, 2, 4, 8] as const;
export type PlaybackSpeed = typeof PLAYBACK_SPEEDS[number];

// Base playback: 1x = 500ms per tick. Each tick = tickMinutes of simulated time.
export const BASE_MS_PER_TICK = 500;
export const msPerTickFor = (speed: number) => Math.max(30, BASE_MS_PER_TICK / speed);

function formatSimTime(tick: number, tickMinutes: number): string {
  const totalMin = tick * tickMinutes;
  const h = Math.floor(totalMin / 60);
  const m = totalMin % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

export function ReplayControls({
  totalTicks,
  currentTick,
  isPlaying,
  speed,
  tickMinutes = 5,
  onTickChange,
  onTogglePlay,
  onSpeedChange,
}: {
  totalTicks: number;
  currentTick: number;
  isPlaying: boolean;
  speed: number;
  tickMinutes?: number;
  onTickChange: (tick: number) => void;
  onTogglePlay: () => void;
  onSpeedChange: (s: PlaybackSpeed) => void;
}) {
  if (totalTicks === 0) return null;

  const atEnd = currentTick >= totalTicks;
  const step = (delta: number) => {
    const next = Math.min(totalTicks, Math.max(0, currentTick + delta));
    onTickChange(next);
  };

  return (
    <div className="mil-panel-body border-t border-mil space-y-2">
      <div className="flex items-center gap-2">
        <button
          onClick={() => onTickChange(0)}
          className="mil-btn mil-btn-sm"
          title="Restart"
          aria-label="Restart"
        >
          ⏮
        </button>
        <button
          onClick={() => step(-1)}
          disabled={currentTick === 0}
          className="mil-btn mil-btn-sm"
          title="Step back"
          aria-label="Step back one tick"
        >
          ◀◀
        </button>
        <button onClick={onTogglePlay} className="mil-btn mil-btn-sm min-w-[70px]">
          {atEnd ? "↻ REPLAY" : isPlaying ? "■ PAUSE" : "▶ PLAY"}
        </button>
        <button
          onClick={() => step(1)}
          disabled={atEnd}
          className="mil-btn mil-btn-sm"
          title="Step forward"
          aria-label="Step forward one tick"
        >
          ▶▶
        </button>
        <input
          type="range"
          min={0}
          max={totalTicks}
          value={currentTick}
          onChange={(e) => onTickChange(Number(e.target.value))}
          className="flex-1 accent-green-400"
        />
        <span className="mil-value-accent text-xs font-mono min-w-[90px] text-right">
          T+{String(currentTick).padStart(4, "0")} / {String(totalTicks).padStart(4, "0")}
        </span>
      </div>
      <div className="flex items-center gap-2 text-[10px]">
        <span className="mil-label">SPEED</span>
        <div className="flex gap-1">
          {PLAYBACK_SPEEDS.map((s) => (
            <button
              key={s}
              onClick={() => onSpeedChange(s)}
              className={`mil-btn mil-btn-sm px-2 py-0.5 ${
                speed === s ? "mil-btn-primary" : ""
              }`}
              aria-pressed={speed === s}
            >
              {s}x
            </button>
          ))}
        </div>
        <div className="flex-1" />
        <span className="mil-label">SIM TIME</span>
        <span className="mil-value-accent font-mono">
          {formatSimTime(currentTick, tickMinutes)}
        </span>
        <span className="text-dim">
          ({tickMinutes}m/tick · {Math.round(msPerTickFor(speed))}ms/tick)
        </span>
      </div>
    </div>
  );
}
