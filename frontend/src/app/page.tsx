"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Header } from "@/components/Header";
import { SimulationControl } from "@/components/SimulationControl";
import { MapVisualization } from "@/components/MapVisualization";
import { ResultsDashboard } from "@/components/ResultsDashboard";
import { ReplayControls } from "@/components/ReplayControls";
import {
  getReplay,
  getBatchResults,
  type SimulationResponse,
  type BatchResponse,
  type BatchResults,
  type ReplayData,
} from "@/lib/api";

export default function Home() {
  const [simResult, setSimResult] = useState<SimulationResponse | null>(null);
  const [batchResults, setBatchResults] = useState<BatchResults | null>(null);
  const [replay, setReplay] = useState<ReplayData | null>(null);
  const [currentTick, setCurrentTick] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const handleSimResult = useCallback(async (result: SimulationResponse) => {
    setSimResult(result);
    setBatchResults(null);
    try {
      const replayData = await getReplay(result.simulation_id);
      setReplay(replayData);
      setCurrentTick(0);
      setIsPlaying(false);
    } catch {
      // replay not available
    }
  }, []);

  const handleBatchResult = useCallback(async (result: BatchResponse) => {
    setSimResult(null);
    setReplay(null);
    setCurrentTick(0);
    try {
      const results = await getBatchResults(result.batch_id);
      setBatchResults(results);
    } catch {
      // results not available
    }
  }, []);

  const togglePlay = useCallback(() => {
    setIsPlaying((prev) => !prev);
  }, []);

  useEffect(() => {
    if (isPlaying && replay) {
      intervalRef.current = setInterval(() => {
        setCurrentTick((prev) => {
          if (prev >= replay.ticks.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 100);
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isPlaying, replay]);

  return (
    <div className="flex flex-col h-screen">
      <Header batchStatus={batchResults ? `Batch: ${batchResults.total} sims` : undefined} />

      <div className="flex-1 grid grid-cols-[280px_1fr_320px] gap-4 p-4 overflow-hidden">
        {/* Left sidebar */}
        <div className="overflow-y-auto space-y-4">
          <SimulationControl onSimResult={handleSimResult} onBatchResult={handleBatchResult} />
        </div>

        {/* Center - Map */}
        <div className="overflow-y-auto space-y-2">
          <MapVisualization replay={replay} currentTick={currentTick} />
          <ReplayControls
            totalTicks={replay ? replay.ticks.length - 1 : 0}
            currentTick={currentTick}
            isPlaying={isPlaying}
            onTickChange={setCurrentTick}
            onTogglePlay={togglePlay}
          />
          {/* Events log */}
          {replay && replay.ticks[currentTick] && (
            <div className="card max-h-40 overflow-y-auto">
              <h3 className="text-xs font-semibold text-slate-500 mb-1">Events (Tick {currentTick})</h3>
              {replay.ticks[currentTick].events.length === 0 ? (
                <p className="text-xs text-slate-600">No events this tick.</p>
              ) : (
                <ul className="space-y-0.5">
                  {replay.ticks[currentTick].events.map((evt, i) => (
                    <li key={i} className="text-xs font-mono text-slate-400">{evt}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>

        {/* Right sidebar */}
        <div className="overflow-y-auto">
          <ResultsDashboard simResult={simResult} batchResults={batchResults} />
        </div>
      </div>
    </div>
  );
}
