"use client";

import { useRef, useEffect, useCallback } from "react";
import type { ReplayData, TickData } from "@/lib/api";

const THEATER_W = 1667;
const THEATER_H = 1300;

const sx = (x: number, w: number) => (x / THEATER_W) * w;
const sy = (y: number, h: number) => (y / THEATER_H) * h;

export function TacticalMap({ replay, currentTick }: { replay: ReplayData | null; currentTick: number }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const draw = useCallback((ctx: CanvasRenderingContext2D, tick: TickData | null, w: number, h: number) => {
    // Sea background
    ctx.fillStyle = "#05100a";
    ctx.fillRect(0, 0, w, h);

    // Grid
    ctx.strokeStyle = "rgba(74, 222, 128, 0.04)";
    ctx.lineWidth = 0.5;
    for (let x = 0; x < w; x += 40) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
    }
    for (let y = 0; y < h; y += 40) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
    }

    // Major grid lines
    ctx.strokeStyle = "rgba(74, 222, 128, 0.1)";
    for (let x = 0; x < w; x += 200) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
    }
    for (let y = 0; y < h; y += 200) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
    }

    // Crosshair center
    ctx.strokeStyle = "rgba(74, 222, 128, 0.2)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(w / 2 - 10, h / 2); ctx.lineTo(w / 2 + 10, h / 2);
    ctx.moveTo(w / 2, h / 2 - 10); ctx.lineTo(w / 2, h / 2 + 10);
    ctx.stroke();

    // North landmass
    ctx.fillStyle = "rgba(34, 80, 50, 0.25)";
    ctx.strokeStyle = "rgba(74, 222, 128, 0.4)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(w, 0);
    ctx.lineTo(w, sy(300, h));
    ctx.quadraticCurveTo(w * 0.6, sy(380, h), w * 0.3, sy(330, h));
    ctx.quadraticCurveTo(w * 0.1, sy(360, h), 0, sy(350, h));
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // South landmass
    ctx.fillStyle = "rgba(60, 40, 25, 0.25)";
    ctx.strokeStyle = "rgba(200, 130, 70, 0.4)";
    ctx.beginPath();
    ctx.moveTo(0, h);
    ctx.lineTo(w, h);
    ctx.lineTo(w, sy(1050, h));
    ctx.quadraticCurveTo(w * 0.5, sy(1010, h), w * 0.2, sy(1060, h));
    ctx.quadraticCurveTo(w * 0.05, sy(1080, h), 0, sy(1065, h));
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Passage label
    ctx.fillStyle = "rgba(74, 222, 128, 0.12)";
    ctx.font = "bold 18px monospace";
    ctx.textAlign = "center";
    ctx.letterSpacing = "4px";
    ctx.fillText("THE BOREAL PASSAGE", w / 2, h * 0.55);

    if (!tick) {
      ctx.fillStyle = "rgba(74, 222, 128, 0.4)";
      ctx.font = "11px monospace";
      ctx.fillText("[ NO REPLAY DATA ]", w / 2, h / 2 + 60);
      ctx.fillStyle = "rgba(74, 222, 128, 0.2)";
      ctx.font = "9px monospace";
      ctx.fillText("AWAITING SIMULATION", w / 2, h / 2 + 75);
      return;
    }

    // Bases — triangles
    for (const base of tick.bases) {
      const bx = sx(base.position[0], w);
      const by = sy(base.position[1], h);
      const isNorth = base.side === "north";
      const color = isNorth ? "#4ade80" : "#fb923c";

      if (!base.operational) {
        ctx.fillStyle = "rgba(100, 100, 100, 0.4)";
      } else {
        ctx.fillStyle = color;
      }
      ctx.strokeStyle = "rgba(0, 0, 0, 0.8)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(bx, by - 9);
      ctx.lineTo(bx - 8, by + 6);
      ctx.lineTo(bx + 8, by + 6);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();

      // Base label
      ctx.fillStyle = "rgba(184, 230, 198, 0.5)";
      ctx.font = "8px monospace";
      ctx.textAlign = "center";
      ctx.fillText(base.name.toUpperCase().split(" ")[0], bx, by + 18);
    }

    // Cities — squares
    for (const city of tick.cities) {
      const cx = sx(city.position[0], w);
      const cy = sy(city.position[1], h);
      const isCapital = city.name.includes("Capital") || city.name.includes("Arktholm") || city.name.includes("Meridia");
      const size = isCapital ? 10 : 7;

      let color = isCapital ? "#fbbf24" : "#b8e6c6";
      if (city.damage > 0.3) color = "#f59e0b";
      if (city.damage > 0.7) color = "#ef4444";

      ctx.fillStyle = color;
      ctx.strokeStyle = "rgba(0, 0, 0, 0.8)";
      ctx.fillRect(cx - size / 2, cy - size / 2, size, size);
      ctx.strokeRect(cx - size / 2, cy - size / 2, size, size);

      if (isCapital) {
        ctx.strokeStyle = color;
        ctx.beginPath();
        ctx.arc(cx, cy, size + 3, 0, Math.PI * 2);
        ctx.stroke();
      }

      ctx.fillStyle = "rgba(184, 230, 198, 0.6)";
      ctx.font = isCapital ? "bold 9px monospace" : "8px monospace";
      ctx.textAlign = "center";
      ctx.fillText(
        city.name.replace(" (Capital X)", "").replace(" (Capital Y)", "").toUpperCase(),
        cx, cy + size / 2 + 10,
      );
    }

    // Aircraft
    for (const ac of tick.aircraft) {
      if (["destroyed", "grounded", "refueling", "rearming", "maintenance"].includes(ac.state)) continue;
      const ax = sx(ac.position[0], w);
      const ay = sy(ac.position[1], h);
      const color = ac.side === "north" ? "#4ade80" : "#fb923c";

      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(ax, ay, 3, 0, Math.PI * 2);
      ctx.fill();

      // Direction indicator for bombers
      if (ac.type === "bomber") {
        ctx.strokeStyle = color;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(ax, ay, 5, 0, Math.PI * 2);
        ctx.stroke();
      }

      if (ac.fuel < 0.3) {
        ctx.strokeStyle = "#ef4444";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(ax, ay, 6, 0, Math.PI * 2);
        ctx.stroke();
      }
    }

    // Battles — flash indicator
    for (const battle of (tick.battles || [])) {
      const pos = battle.position as [number, number];
      if (!pos) continue;
      const bx = sx(pos[0], w);
      const by = sy(pos[1], h);
      ctx.strokeStyle = "#fbbf24";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(bx, by, 10, 0, Math.PI * 2);
      ctx.stroke();
      ctx.strokeStyle = "rgba(251, 191, 36, 0.4)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(bx, by, 16, 0, Math.PI * 2);
      ctx.stroke();
    }

    // HUD corner info
    ctx.fillStyle = "rgba(74, 222, 128, 0.6)";
    ctx.font = "9px monospace";
    ctx.textAlign = "left";
    ctx.fillText(`T+${String(tick.tick).padStart(4, "0")}`, 8, 14);
    ctx.textAlign = "right";
    ctx.fillText(`UNITS: ${tick.aircraft.filter(a => a.state !== "destroyed").length}`, w - 8, 14);
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
    <div className="relative">
      <canvas ref={canvasRef} className="block w-full" style={{ aspectRatio: `${THEATER_W}/${THEATER_H}` }} />
    </div>
  );
}
