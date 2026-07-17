import React from 'react';
import { UIProvider, useUI } from './context/UIProvider';
import { SimulationProvider, useSimulation } from './context/SimulationContext';
import MapView from './components/MapView';
import ThreatFeed from './components/ThreatFeed';
import DockContainer from './components/DockContainer';

function CommandCenter() {
  const { phase, isMonitoring, hasRecommendation, isRunning } = useUI();
  const { executeSimulation, telemetry } = useSimulation();
  
  // Dynamic Task Narrator
  const getTaskString = (currentPhase) => {
    switch(currentPhase) {
      case 'INCIDENT': return 'Ingesting Signals...';
      case 'EXECUTING': return 'Initializing Agents...';
      case 'ANALYZING': return 'Bayesian Inference';
      case 'SIMULATING': return 'Monte Carlo Stochastics';
      case 'OPTIMIZING': return 'Graph Route Optimization';
      case 'RECOMMENDING': return 'Pipeline Complete';
      default: return 'Monitoring Global Network';
    }
  };

  return (
    <div className="relative w-screen h-screen bg-[#090d16] font-mono overflow-hidden flex items-center justify-center">
      
      {/* MAP LAYER */}
      <div className="absolute inset-0 z-0">
        <MapView 
          isDisrupted={!isMonitoring} 
          showReroute={hasRecommendation || phase === 'OPTIMIZING'}
          isSimulating={isRunning}
        />
      </div>

      <div className="absolute inset-0 z-10 pointer-events-none bg-[radial-gradient(ellipse_at_center,_rgba(0,243,255,0.02),_transparent_60%)]" />

      {/* LEFT HUD: Threat Trigger */}
      <ThreatFeed 
        onTriggerCrisis={() => executeSimulation()}
        isSimulating={isRunning || phase === 'EXECUTING'}
        hasSimulated={hasRecommendation}
      />

      {/* RIGHT HUD: The Dockable Sidebar */}
      <DockContainer />

      {/* STATUS BAR */}
      <div className="fixed bottom-0 left-0 right-0 z-20 px-6 py-2 border-t border-[#1e293b]/50 bg-[#090d16]/80 backdrop-blur-md flex justify-between items-center text-[9px] uppercase tracking-widest text-slate-500">
        <div className="flex space-x-6 items-center">
          <span>NODE: <span className="text-slate-400">FRONTEND_PRIMARY</span></span>
          <div className="h-3 w-px bg-slate-700" />
          <span>
            STATUS: <span className={isMonitoring ? 'text-[#10b981]' : 'text-[#ffb700]'}>{phase}</span>
          </span>
          {/* Operator Layer Technical Readout */}
          {!isMonitoring && (
            <>
              <div className="h-3 w-px bg-slate-700" />
              <span className="text-slate-400">TASK: <span className="text-[#00f3ff] animate-pulse">{getTaskString(phase)}</span></span>
            </>
          )}
        </div>
        
        <div className="flex space-x-6">
          {/* Split Latency Metrics */}
          {telemetry.networkRtt && (
            <span>RTT: <span className="text-[#00f3ff]">{telemetry.networkRtt} MS</span></span>
          )}
          {telemetry.backendProcess && (
            <span>BACKEND: <span className="text-[#00f3ff]">{telemetry.backendProcess} MS</span></span>
          )}
          {!telemetry.networkRtt && (
            <span>ENGINE: <span className="text-slate-400">REACT/MAPBOX</span></span>
          )}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <UIProvider>
      <SimulationProvider>
        <CommandCenter />
      </SimulationProvider>
    </UIProvider>
  );
}