import React from 'react';
import { ShieldAlert, Activity, Route } from 'lucide-react';

export default function AnalyticsPanel({ pipelineState }) {
  // Map pipeline states to an integer for easy comparative logic
  const stateLevel = {
    'MONITORING': 0,
    'INCIDENT_DETECTED': 1,
    'ANALYZING': 2,
    'SIMULATING': 3,
    'OPTIMIZING': 4,
    'RECOMMENDING': 5
  }[pipelineState] || 0;

  if (stateLevel < 2) return null; // Hide completely until analysis begins

  return (
    <div className="fixed right-6 top-[100px] w-[380px] z-20 flex flex-col space-y-4 max-h-[calc(100vh-140px)] overflow-y-auto custom-scrollbar pr-2">
      
      {/* 1. BAYESIAN ANALYSIS BLOCK */}
      <div className="backdrop-blur-md bg-panel/85 border border-borderline rounded-lg p-4 shadow-xl animate-fade-in-up">
        <div className="flex items-center justify-between mb-3 pb-2 border-b border-borderline">
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-4 h-4 text-tactical-amber" />
            <h3 className="text-xs font-mono font-bold text-tactical-amber tracking-widest">BAYESIAN ANALYSIS</h3>
          </div>
          <span className="text-[9px] font-mono bg-tactical-amber/10 text-tactical-amber px-1.5 py-0.5 rounded border border-tactical-amber/20 uppercase">
            Posterior Updated
          </span>
        </div>
        
        <div className="grid grid-cols-2 gap-3 mb-3 font-mono">
          <div className="p-2 bg-console/50 rounded border border-borderline/50 text-center">
            <div className="text-[10px] text-slate-500 mb-1">PRIOR RISK</div>
            <div className="text-lg text-slate-300">18.5%</div>
          </div>
          <div className="p-2 bg-tactical-red/10 rounded border border-tactical-red/30 text-center relative overflow-hidden">
            <div className="absolute inset-0 bg-tactical-red/5 animate-pulse" />
            <div className="text-[10px] text-tactical-red mb-1 relative z-10">POSTERIOR</div>
            <div className="text-lg font-bold text-tactical-red relative z-10">68.2%</div>
          </div>
        </div>
        
        <div className="text-[10px] font-mono text-slate-400 p-2 bg-console/50 rounded leading-relaxed border border-borderline/30">
          <span className="text-tactical-amber font-bold">INSIGHT: </span> 
          Kinetic threat classification generates a high likelihood ratio, triggering immediate critical pathway review.
        </div>
      </div>

      {/* 2. MONTE CARLO STOCHASTICS BLOCK */}
      {stateLevel >= 3 && (
        <div className="backdrop-blur-md bg-panel/85 border border-borderline rounded-lg p-4 shadow-xl animate-fade-in-up">
          <div className="flex items-center space-x-2 mb-3 pb-2 border-b border-borderline">
            <Activity className="w-4 h-4 text-tactical-purple" />
            <h3 className="text-xs font-mono font-bold text-tactical-purple tracking-widest">MONTE CARLO ENGINE</h3>
          </div>
          
          <div className="flex justify-between items-center mb-4 font-mono">
            <div>
              <div className="text-[10px] text-slate-500">EXPECTED SHORTFALL</div>
              <div className="text-sm font-bold text-slate-200">2.4 MBD</div>
            </div>
            <div className="text-right">
              <div className="text-[10px] text-slate-500">95% CONFIDENCE INTERVAL</div>
              <div className="text-sm font-bold text-tactical-green">3.1 TO 8.2 DAYS</div>
            </div>
          </div>

          {/* Simulated UI Histogram */}
          <div className="h-24 w-full flex items-end justify-between space-x-[2px] opacity-90 mb-2">
            {[2, 4, 8, 15, 35, 65, 100, 85, 45, 20, 10, 5, 2, 1].map((val, idx) => (
              <div 
                key={idx} 
                style={{ height: `${val}%` }} 
                className="w-full bg-tactical-purple/60 hover:bg-tactical-purple transition-all rounded-t-sm"
              />
            ))}
          </div>
          
          <div className="flex justify-between text-[9px] font-mono text-slate-500">
            <span>DEPLETED (0 DAYS)</span>
            <span>MEAN: 6.1 DAYS</span>
            <span>FULL (9.5 DAYS)</span>
          </div>
        </div>
      )}

      {/* 3. PROCUREMENT OPTIMIZATION BLOCK */}
      {stateLevel >= 5 && (
        <div className="backdrop-blur-md bg-tactical-green/10 border border-tactical-green/40 rounded-lg p-4 shadow-[0_0_30px_rgba(16,185,129,0.05)] animate-fade-in-up">
          <div className="flex items-center space-x-2 mb-3 pb-2 border-b border-tactical-green/30">
            <Route className="w-4 h-4 text-tactical-green" />
            <h3 className="text-xs font-mono font-bold text-tactical-green tracking-widest">PROCUREMENT DIRECTIVE</h3>
          </div>
          
          <div className="bg-console/60 p-3 rounded border border-borderline/50 mb-3">
            <div className="text-[10px] text-slate-500 uppercase mb-1 font-mono">Recommended Reroute</div>
            <div className="text-lg font-bold text-slate-200 font-mono tracking-wide">CAPE OF GOOD HOPE</div>
          </div>

          <div className="grid grid-cols-2 gap-3 font-mono">
            <div className="p-2 bg-console/40 rounded border border-borderline/40">
              <div className="text-[9px] text-slate-500 uppercase">Transit Delay</div>
              <div className="text-sm font-bold text-tactical-amber">+6.5 DAYS</div>
            </div>
            <div className="p-2 bg-console/40 rounded border border-borderline/40">
              <div className="text-[9px] text-slate-500 uppercase">Cost Delta</div>
              <div className="text-sm font-bold text-tactical-red">₹24.5L / DAY</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}