"use client";

import { useRef, useEffect, useCallback } from "react";
import type { ReplayData, TickData } from "@/lib/api";

interface Props {
  replay: ReplayData | null;
  currentTick: number;
}

const THEATER_W = 1667;
const THEATER_H = 1300;

function scaleX(x: number, canvasW: number) { return (x / THEATER_W) * canvasW; }
function scaleY(y: number, canvasH: number) { return (y / THEATER_H) * canvasH; }

export function MapVisualization({ replay, currentTick }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const draw = useCallback((ctx: CanvasRenderingContext2D, tick: TickData | null, w: number, h: number) => {
    // Background - sea
    ctx.fillStyle = "#0f1e2e";
    ctx.fillRect(0, 0, w, h);

    // Grid
    ctx.strokeStyle = "rgba(255,255,255,0.03)";
    ctx.lineWidth = 0.5;
    for (let x = 0; x < w; x += 50) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke(); }
    for (let y = 0; y < h; y += 50) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }

    // North mainland (simplified)
    ctx.fillStyle = "#1a2e1a";
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(w, 0);
    ctx.lineTo(w, scaleY(300, h));
    ctx.quadraticCurveTo(w * 0.5, scaleY(380, h), 0, scaleY(350, h));
    ctx.closePath();
    ctx.fill();

    // South mainland (simplified)
    ctx.fillStyle = "#2e2a1a";
    ctx.beginPath();
    ctx.moveTo(0, h);
    ctx.lineTo(w, h);
    ctx.lineTo(w, scaleY(1050, h));
    ctx.quadraticCurveTo(w * 0.5, scaleY(1000, h), 0, scaleY(1060, h));
    ctx.closePath();
    ctx.fill();

    // Passage label
    ctx.fillStyle = "rgba(180,210,240,0.06)";
    ctx.font = "bold 20px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("THE BOREAL PASSAGE", w / 2, h / 2);

    if (!tick) {
      ctx.fillStyle = "rgba(255,255,255,0.15)";
      ctx.font = "14px sans-serif";
      ctx.fillText("Run a simulation to see replay", w / 2, h / 2 + 30);
      return;
    }

    // Draw bases
    for (const base of tick.bases) {
      const bx = scaleX(base.position[0], w);
      const by = scaleY(base.position[1], h);
      const color = base.side === "north" ? "#06b6d4" : "#f97316";
      // Triangle
      ctx.fillStyle = base.operational ? color : "#666";
      ctx.beginPath();
      ctx.moveTo(bx, by - 8);
      ctx.lineTo(bx - 7, by + 5);
      ctx.lineTo(bx + 7, by + 5);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = "#000";
      ctx.lineWidth = 1;
      ctx.stroke();
      // Label
      ctx.fillStyle = "rgba(255,255,255,0.5)";
      ctx.font = "9px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(base.name.split(" ")[0], bx, by + 16);
    }

    // Draw cities
    for (const city of tick.cities) {
      const cx = scaleX(city.position[0], w);
      const cy = scaleY(city.position[1], h);
      const isCapital = city.name.includes("Capital") || city.name.includes("Arktholm") || city.name.includes("Meridia");
      const size = isCapital ? 8 : 6;
      ctx.fillStyle = isCapital ? "#eab308" : "#ffffff";
      if (city.damage > 0.5) ctx.fillStyle = "#ef4444";
      ctx.fillRect(cx - size/2, cy - size/2, size, size);
      ctx.strokeStyle = "#000";
      ctx.lineWidth = 1;
      ctx.strokeRect(cx - size/2, cy - size/2, size, size);
      ctx.fillStyle = "rgba(255,255,255,0.4)";
      ctx.font = "8px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(city.name.replace(" (Capital X)", "").replace(" (Capital Y)", ""), cx, cy + size + 8);
    }

    // Draw aircraft
    for (const ac of tick.aircraft) {
      if (ac.state === "destroyed" || ac.state === "grounded" ||
          ac.state === "refueling" || ac.state === "rearming" || ac.state === "maintenance") continue;
      const ax = scaleX(ac.position[0], w);
      const ay = scaleY(ac.position[1], h);
      const color = ac.side === "north" ? "#22d3ee" : "#fb923c";
      // Dot for aircraft
      ctx.beginPath();
      ctx.arc(ax, ay, 3, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();
      // Fuel indicator
      if (ac.fuel < 0.3) {
        ctx.strokeStyle = "#ef4444";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(ax, ay, 5, 0, Math.PI * 2);
        ctx.stroke();
      }
    }

    // Draw battles
    for (const battle of (tick.battles || [])) {
      const pos = battle.position as [number, number];
      if (!pos) continue;
      const bx = scaleX(pos[0], w);
      const by = scaleY(pos[1], h);
      ctx.fillStyle = "rgba(234, 179, 8, 0.6)";
      ctx.beginPath();
      ctx.arc(bx, by, 8, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#eab308";
      ctx.font = "bold 10px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("\u26A1", bx, by + 4);
    }

    // Tick info
    ctx.fillStyle = "rgba(255,255,255,0.3)";
    ctx.font = "11px monospace";
    ctx.textAlign = "left";
    ctx.fillText(`Tick ${tick.tick}`, 8, h - 8);

  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.parentElement?.getBoundingClientRect();
    const w = rect?.width || 800;
    const h = (w / THEATER_W) * THEATER_H;
    canvas.width = w;
    canvas.height = h;

    const tick = replay?.ticks?.[currentTick] || null;
    draw(ctx, tick, w, h);
  }, [replay, currentTick, draw]);

  return (
    <div className="card p-0 overflow-hidden">
      <canvas ref={canvasRef} className="w-full" style={{ aspectRatio: `${THEATER_W}/${THEATER_H}` }} />
    </div>
  );
}
