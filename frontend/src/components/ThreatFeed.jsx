import React from 'react';
import { AlertTriangle, RadioReceiver } from 'lucide-react';

// Define the scenarios as requested in the roadmap
const CRISIS_SCENARIOS = [
  {
    id: "hormuz_kinetic",
    tag: "Kinetic Threat",
    label: "Vessel struck by uncrewed aerial system near Strait of Hormuz.",
    desc: "Target: Crude oil tanker en route to Jamnagar. Operations suspended.",
    payload: {
      corridor: "strait_of_hormuz",
      supplier: "saudi_arabia",
      event_type: "kinetic_incident",
      headline: "Vessel attacked near Hormuz, major delays expected"
    }
  },
  {
    id: "red_sea_blockade",
    tag: "Maritime Blockade",
    label: "Sustained Houthi attacks on Red Sea shipping lanes.",
    desc: "Target: Commercial shipping diverted. Severe congestion expected.",
    payload: {
      corridor: "bab_el_mandeb",
      supplier: "iraq",
      event_type: "kinetic_incident",
      headline: "Sustained drone and missile attacks on commercial shipping in the Red Sea"
    }
  },
  {
    id: "iran_sanctions",
    tag: "Geopolitical",
    label: "Renewed US sanctions pressure on Iranian oil exports.",
    desc: "Target: Regional stability. Compliance protocols activated.",
    payload: {
      corridor: "strait_of_hormuz",
      supplier: "uae",
      event_type: "sanctions_announcement",
      headline: "Renewed US sanctions pressure on Iranian oil exports"
    }
  }
];

export default function ThreatFeed({ onTriggerCrisis, isSimulating, hasSimulated }) {
  return (
    <div className={`
      fixed left-6 top-[200px] w-[320px] z-20 
      backdrop-blur-md bg-panel/80 border border-borderline/50 rounded shadow-2xl overflow-hidden
      transition-all duration-1000 ease-cinematic max-h-[60vh] flex flex-col
    `}>
      {/* Header - Tighter Padding */}
      <div className="px-3 py-2 bg-console/50 border-b border-borderline/50 flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-2 text-tactical-cyan">
          <RadioReceiver className="w-3.5 h-3.5" />
          <h2 className="text-[10px] font-mono font-bold tracking-widest uppercase">Global Signals</h2>
        </div>
        <div className="w-1.5 h-1.5 bg-tactical-cyan rounded-full animate-pulse" />
      </div>

      {/* Incident Cards - Scrollable if needed */}
      <div className="p-3 overflow-y-auto space-y-3 custom-scrollbar">
        {CRISIS_SCENARIOS.map((scenario) => (
          <div key={scenario.id} className={`
            p-2.5 rounded border transition-all duration-500 
            ${hasSimulated ? 'bg-tactical-red/5 border-tactical-red/30' : 'bg-console/30 border-borderline'}
          `}>
            <div className="flex justify-between items-center mb-1.5">
              <span className="text-[9px] font-mono text-slate-500">SEC-7 // LIVE</span>
              <span className="text-[8px] font-mono px-1.5 py-0.5 bg-tactical-red/20 text-tactical-red rounded uppercase tracking-wider font-bold">
                {scenario.tag}
              </span>
            </div>
            <h3 className="text-[11px] font-bold text-slate-200 mb-1 leading-snug">
              {scenario.label}
            </h3>
            <p className="text-[9px] text-slate-500 mb-3 leading-snug">
              {scenario.desc}
            </p>
            
            <button 
              // Pass the dynamic payload up to the parent component
              onClick={() => onTriggerCrisis(scenario.payload)}
              disabled={isSimulating || hasSimulated}
              className={`
                w-full py-1.5 font-mono text-[9px] font-bold tracking-wider rounded transition-all flex items-center justify-center space-x-2 border
                ${hasSimulated 
                  ? 'bg-tactical-red/10 border-tactical-red/20 text-tactical-red opacity-50 cursor-not-allowed' 
                  : 'bg-tactical-red/10 hover:bg-tactical-red/20 border-tactical-red/50 text-tactical-red'}
                ${isSimulating ? 'opacity-70 animate-pulse cursor-wait' : ''}
              `}
            >
              <AlertTriangle className="w-3 h-3" />
              <span>
                {isSimulating ? 'EXECUTING PIPELINE...' : hasSimulated ? 'SCENARIO ACTIVE' : 'INITIALIZE SIMULATION'}
              </span>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}