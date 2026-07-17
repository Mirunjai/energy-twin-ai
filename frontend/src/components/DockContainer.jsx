import React, { useState, useEffect } from 'react';
import { ShieldAlert, Activity, Route } from 'lucide-react';
import { useUI } from '../context/UIProvider';
import { useSimulation } from '../context/SimulationContext';

export default function DockContainer() {
  const { phase, isMonitoring } = useUI();
  const { simulation } = useSimulation();
  
  // State for which tab is currently slid out (expanded)
  const [activeTab, setActiveTab] = useState(null);

  // Auto-expand logic based on the backend pipeline progression
  useEffect(() => {
    if (phase === 'ANALYZING') setActiveTab('bayes');
    else if (phase === 'SIMULATING') setActiveTab('mc');
    else if (phase === 'RECOMMENDING' || phase === 'OPTIMIZING') setActiveTab('route');
    else if (phase === 'MONITORING') setActiveTab(null);
  }, [phase]);

  if (isMonitoring && activeTab === null) return null;

  // Fallback values if backend is still processing or mocked
  const posteriorRisk = simulation.geo?.posterior_risk ? `${(simulation.geo.posterior_risk * 100).toFixed(1)}%` : '68.2%';
  const mcExpectedShortfall = simulation.monteCarlo?.expected_shortfall ? `${simulation.monteCarlo.expected_shortfall.toFixed(1)} MBD` : '2.4 MBD';
  const procCost = simulation.procurement?.cost_delta ? `₹${simulation.procurement.cost_delta}L / DAY` : '₹24.5L / DAY';

  return (
    <div className="fixed right-6 top-[100px] z-20 flex items-start space-x-2 font-mono h-[calc(100vh-140px)] pointer-events-none">
      
      {/* EXPANDED CONTENT AREA (Left of the tabs) */}
      <div className="w-[320px] relative pointer-events-auto">
        
        {/* BAYESIAN PANEL */}
        <div className={`absolute top-0 right-0 w-full transition-all duration-500 ease-cinematic origin-right
          ${activeTab === 'bayes' ? 'opacity-100 scale-100 translate-x-0' : 'opacity-0 scale-95 translate-x-4 pointer-events-none'}`}>
          <div className="backdrop-blur-md bg-panel/90 border border-borderline rounded shadow-2xl p-4">
            <div className="flex items-center space-x-2 mb-3 pb-2 border-b border-borderline">
              <ShieldAlert className="w-4 h-4 text-tactical-amber" />
              <h3 className="text-xs font-bold text-tactical-amber tracking-widest">BAYESIAN ANALYSIS</h3>
            </div>
            <div className="grid grid-cols-2 gap-2 mb-2">
              <div className="p-2 bg-console/50 rounded border border-borderline/50 text-center">
                <div className="text-[9px] text-slate-500 mb-1">PRIOR</div>
                <div className="text-sm text-slate-300">18.5%</div>
              </div>
              <div className="p-2 bg-tactical-red/10 rounded border border-tactical-red/30 text-center">
                <div className="text-[9px] text-tactical-red mb-1">POSTERIOR</div>
                <div className="text-sm font-bold text-tactical-red">{posteriorRisk}</div>
              </div>
            </div>
            <div className="text-[9px] text-slate-400 p-2 bg-console/50 rounded leading-relaxed border border-borderline/30">
              <span className="text-tactical-amber">INSIGHT:</span> Likelihood ratio exceeds threshold. Critical pathway disruption highly probable.
            </div>
          </div>
        </div>

        {/* MONTE CARLO PANEL */}
        <div className={`absolute top-[130px] right-0 w-full transition-all duration-500 ease-cinematic origin-right
          ${activeTab === 'mc' ? 'opacity-100 scale-100 translate-x-0' : 'opacity-0 scale-95 translate-x-4 pointer-events-none'}`}>
          <div className="backdrop-blur-md bg-panel/90 border border-borderline rounded shadow-2xl p-4">
            <div className="flex items-center space-x-2 mb-3 pb-2 border-b border-borderline">
              <Activity className="w-4 h-4 text-tactical-purple" />
              <h3 className="text-xs font-bold text-tactical-purple tracking-widest">MONTE CARLO</h3>
            </div>
            <div className="flex justify-between items-center mb-3">
              <div>
                <div className="text-[9px] text-slate-500">SHORTFALL</div>
                <div className="text-sm font-bold text-slate-200">{mcExpectedShortfall}</div>
              </div>
              <div className="text-right">
                <div className="text-[9px] text-slate-500">95% CI</div>
                <div className="text-sm font-bold text-tactical-green">3.1 - 8.2 D</div>
              </div>
            </div>
            {/* Visual Histogram */}
            <div className="h-16 w-full flex items-end justify-between space-x-[2px] opacity-80 border-b border-borderline pb-1">
              {[2, 4, 8, 15, 35, 65, 100, 85, 45, 20, 10, 5, 2, 1].map((val, idx) => (
                <div key={idx} style={{ height: `${val}%` }} className="w-full bg-tactical-purple/60 rounded-t-sm" />
              ))}
            </div>
          </div>
        </div>

        {/* PROCUREMENT PANEL */}
        <div className={`absolute top-[280px] right-0 w-full transition-all duration-500 ease-cinematic origin-right
          ${activeTab === 'route' ? 'opacity-100 scale-100 translate-x-0' : 'opacity-0 scale-95 translate-x-4 pointer-events-none'}`}>
          <div className="backdrop-blur-md bg-tactical-green/10 border border-tactical-green/30 rounded shadow-2xl p-4">
            <div className="flex items-center space-x-2 mb-3 pb-2 border-b border-tactical-green/20">
              <Route className="w-4 h-4 text-tactical-green" />
              <h3 className="text-xs font-bold text-tactical-green tracking-widest">PROCUREMENT</h3>
            </div>
            <div className="bg-console/60 p-2 rounded border border-borderline/50 mb-2">
              <div className="text-[9px] text-slate-500 uppercase mb-0.5">Reroute</div>
              <div className="text-sm font-bold text-slate-200">CAPE OF GOOD HOPE</div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="p-2 bg-console/40 rounded border border-borderline/40">
                <div className="text-[8px] text-slate-500 uppercase">Delay</div>
                <div className="text-xs font-bold text-tactical-amber">+6.5 D</div>
              </div>
              <div className="p-2 bg-console/40 rounded border border-borderline/40">
                <div className="text-[8px] text-slate-500 uppercase">Delta</div>
                <div className="text-xs font-bold text-tactical-red">{procCost}</div>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* COLLAPSED TABS COLUMN (Right Edge) */}
      <div className="flex flex-col space-y-2 pointer-events-auto w-[60px]">
        {/* Bayes Tab */}
        <button 
          onClick={() => setActiveTab(activeTab === 'bayes' ? null : 'bayes')}
          className={`w-full flex flex-col items-center justify-center py-2 px-1 rounded border transition-colors ${activeTab === 'bayes' ? 'bg-tactical-amber/20 border-tactical-amber text-tactical-amber' : 'bg-panel/80 border-borderline text-slate-400 hover:border-tactical-amber/50'}`}>
          <span className="text-[8px] uppercase tracking-wider mb-1">POST</span>
          <span className="text-[10px] font-bold">{posteriorRisk}</span>
        </button>

        {/* MC Tab */}
        {['SIMULATING', 'OPTIMIZING', 'RECOMMENDING'].includes(phase) && (
          <button 
            onClick={() => setActiveTab(activeTab === 'mc' ? null : 'mc')}
            className={`w-full flex flex-col items-center justify-center py-2 px-1 rounded border transition-colors ${activeTab === 'mc' ? 'bg-tactical-purple/20 border-tactical-purple text-tactical-purple' : 'bg-panel/80 border-borderline text-slate-400 hover:border-tactical-purple/50'}`}>
            <span className="text-[8px] uppercase tracking-wider mb-1">MC</span>
            <span className="text-[10px] font-bold">6.1D</span>
          </button>
        )}

        {/* Route Tab */}
        {['OPTIMIZING', 'RECOMMENDING'].includes(phase) && (
          <button 
            onClick={() => setActiveTab(activeTab === 'route' ? null : 'route')}
            className={`w-full flex flex-col items-center justify-center py-2 px-1 rounded border transition-colors ${activeTab === 'route' ? 'bg-tactical-green/20 border-tactical-green text-tactical-green' : 'bg-panel/80 border-borderline text-slate-400 hover:border-tactical-green/50'}`}>
            <span className="text-[8px] uppercase tracking-wider mb-1">ROUTE</span>
            <span className="text-[10px] font-bold">CAPE</span>
          </button>
        )}
      </div>

    </div>
  );
}