import React from 'react';

export default function Legend() {
  return (
    <div className="absolute bottom-12 left-6 z-10 flex flex-col space-y-1.5 p-3 backdrop-blur-md bg-panel/40 border border-borderline/50 rounded pointer-events-none font-mono text-[9px] uppercase tracking-widest text-slate-400">
      <div className="flex items-center space-x-2">
        <span className="text-tactical-cyan text-xs">◉</span>
        <span>Supplier Node</span>
      </div>
      <div className="flex items-center space-x-2">
        <span className="text-slate-400 text-xs">◎</span>
        <span>Maritime Corridor</span>
      </div>
      <div className="flex items-center space-x-2">
        <span className="text-tactical-green text-xs">⬢</span>
        <span>Refinery / Port</span>
      </div>
      <div className="flex items-center space-x-2 mt-1 pt-1 border-t border-borderline/50">
        <div className="w-3 h-0.5 bg-tactical-cyan" />
        <span>Active Logistics</span>
      </div>
    </div>
  );
}