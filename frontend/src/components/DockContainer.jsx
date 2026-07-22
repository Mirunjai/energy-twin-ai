import React, { useState, useEffect } from 'react';
import { ShieldAlert, Activity, Route, BrainCircuit, Database } from 'lucide-react';
import AgentAnalysisPanel from './AgentAnalysisPanel';
import { useUI } from '../context/UIProvider';
import { useSimulation } from '../context/SimulationContext';

export default function DockContainer() {
  const { phase, isMonitoring } = useUI();
  const { simulation } = useSimulation();
  
  const [activeTab, setActiveTab] = useState(null);

  useEffect(() => {
    if (phase === 'ANALYZING') setActiveTab('bayes');
    else if (phase === 'SIMULATING') setActiveTab('mc');
    else if (phase === 'RECOMMENDING' || phase === 'OPTIMIZING') setActiveTab('route');
    else if (phase === 'MONITORING') setActiveTab(null);
  }, [phase]);

  // 1. GEO ALIGNMENT
  const threatScore = simulation?.geo?.metrics?.posterior_probability 
    ? (simulation.geo.metrics.posterior_probability * 100).toFixed(1) 
    : (simulation?.geo?.posterior_risk ? (simulation.geo.posterior_risk * 100).toFixed(1) : "68.2");

  // 2. MONTE CARLO ALIGNMENT
  const mc = simulation?.monteCarlo || simulation?.monte_carlo_results;
  const sprDays = mc?.spr_days_remaining_mean || "6.1";
  const mcExpectedShortfall = mc?.expected_shortfall_mbd ? `${mc.expected_shortfall_mbd.toFixed(1)} MBD` : '2.4 MBD';
  const mcCI = mc?.confidence_interval_str || "3.1 to 8.2 days";
  
  const rawHistogram = mc?.histogram_counts || [2, 4, 8, 15, 35, 65, 100, 85, 45, 20, 10, 5, 2, 1];
  const maxCount = Math.max(...rawHistogram, 1);
  const histogramHeights = rawHistogram.map(count => (count / maxCount) * 100);

  // 3. PROCUREMENT ALIGNMENT
  const altRoute = simulation?.procurement?.alternatives?.[0];
  const dailyCostRaw = altRoute?.estimated_cost_delta_per_day;
  const dailyCost = dailyCostRaw ? (dailyCostRaw / 100000).toFixed(1) : "24.5";
  
  const routeNodes = altRoute?.path_nodes || [];
  const routeName = routeNodes.length > 2 
    ? routeNodes.slice(1, -1).map(n => n.replace(/_/g, ' ').toUpperCase()).join(' → ') 
    : "CAPE OF GOOD HOPE";
    
  const delayDays = altRoute?.total_distance_nm 
    ? ((altRoute.total_distance_nm - 1200) / 350).toFixed(1) 
    : "6.5";
    
  const priorProb = simulation?.geo?.metrics?.prior_probability
    ? (simulation.geo.metrics.prior_probability * 100).toFixed(1)
    : "18.5";

  // 4. NEW SPR AGENT ALIGNMENT (Phase 2)
  const sprAnalysis = simulation?.agentAnalysis?.spr_readout;
  const isSprStable = !sprAnalysis || sprAnalysis.days_until_breach === Infinity;
  const displaySprDays = isSprStable ? "9.5" : sprAnalysis.days_until_breach.toFixed(1);

  return (
    <div className="fixed right-6 top-[100px] z-20 flex items-start space-x-2 font-mono h-[calc(100vh-140px)] pointer-events-none">
      
      {/* EXPANDED CONTENT AREA */}
      <div className="w-[320px] relative pointer-events-auto">
        
        {/* NEW SPR PANEL - ALWAYS AVAILABLE */}
        <div className={`absolute top-0 right-0 w-full transition-all duration-500 ease-cinematic origin-right
          ${activeTab === 'spr' ? 'opacity-100 scale-100 translate-x-0' : 'opacity-0 scale-95 translate-x-4 pointer-events-none'}`}>
          <div className="backdrop-blur-md bg-panel/90 border border-tactical-cyan/50 rounded shadow-2xl p-4">
            <div className="flex items-center space-x-2 mb-3 pb-2 border-b border-borderline">
              <Database className="w-4 h-4 text-tactical-cyan" />
              <h3 className="text-xs font-bold text-tactical-cyan tracking-widest">STRATEGIC RESERVE</h3>
            </div>
            <div className="grid grid-cols-2 gap-2 mb-2">
              <div className="p-2 bg-console/50 rounded border border-borderline/50 text-center">
                <div className="text-[9px] text-slate-500 mb-1">STATUS</div>
                <div className="text-sm text-tactical-cyan font-bold">{isSprStable ? 'STABLE' : 'DRAWDOWN'}</div>
              </div>
              <div className="p-2 bg-tactical-red/10 rounded border border-tactical-red/30 text-center">
                <div className="text-[9px] text-tactical-red mb-1">DAYS TO BREACH</div>
                <div className="text-sm font-bold text-tactical-red">{displaySprDays}</div>
              </div>
            </div>
            
            {!isSprStable && sprAnalysis?.replenishment_trigger_date ? (
              <div className="text-[9px] text-slate-400 p-2 bg-console/50 rounded leading-relaxed border border-tactical-red/30">
                <span className="text-tactical-red">WARNING:</span> Critical threshold breach projected on <span className="font-bold text-slate-200">{sprAnalysis.replenishment_trigger_date}</span>. Replenishment ops required.
              </div>
            ) : (
              <div className="text-[9px] text-slate-400 p-2 bg-console/50 rounded leading-relaxed border border-tactical-green/30">
                <span className="text-tactical-green">SECURE:</span> Reserves are stable at ~45.0M barrels. No breach projected.
              </div>
            )}
          </div>
        </div>

        {/* AI REASONING PANEL */}
        <div className={`absolute top-0 right-0 w-full transition-all duration-500 ease-cinematic origin-right
          ${activeTab === 'intel' ? 'opacity-100 scale-100 translate-x-0' : 'opacity-0 scale-95 translate-x-4 pointer-events-none'}`}>
          <AgentAnalysisPanel agentAnalysis={simulation?.agentAnalysis} />
        </div>

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
                <div className="text-sm text-slate-300">{priorProb}%</div>
              </div>
              <div className="p-2 bg-tactical-red/10 rounded border border-tactical-red/30 text-center">
                <div className="text-[9px] text-tactical-red mb-1">POSTERIOR</div>
                <div className="text-sm font-bold text-tactical-red">{threatScore}%</div>
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
                <div className="text-sm font-bold text-tactical-green">{mcCI}</div>
              </div>
            </div>
            <div className="h-16 w-full flex items-end justify-between space-x-[2px] opacity-80 border-b border-borderline pb-1">
              {histogramHeights.map((heightPct, idx) => (
                <div key={idx} style={{ height: `${heightPct}%` }} className="w-full bg-tactical-purple/60 rounded-t-sm transition-all duration-500" />
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
              <div className="text-sm font-bold text-slate-200 truncate">{routeName}</div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="p-2 bg-console/40 rounded border border-borderline/40">
                <div className="text-[8px] text-slate-500 uppercase">Delay</div>
                <div className="text-xs font-bold text-tactical-amber">+{delayDays > 0 ? delayDays : 6.5} D</div>
              </div>
              <div className="p-2 bg-console/40 rounded border border-borderline/40">
                <div className="text-[8px] text-slate-500 uppercase">Delta</div>
                <div className="text-xs font-bold text-tactical-red">₹{dailyCost}L / DAY</div>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* COLLAPSED TABS COLUMN */}
      <div className="flex flex-col space-y-2 pointer-events-auto w-[60px]">
        
        {/* NEW: SPR Tab (Always Visible) */}
        <button 
          onClick={() => setActiveTab(activeTab === 'spr' ? null : 'spr')}
          className={`w-full flex flex-col items-center justify-center py-2 px-1 rounded border transition-colors ${activeTab === 'spr' ? 'bg-tactical-cyan/20 border-tactical-cyan text-tactical-cyan' : 'bg-panel/80 border-borderline text-slate-400 hover:border-tactical-cyan/50'}`}>
          <Database className="w-3.5 h-3.5 mb-1" />
          <span className="text-[10px] font-bold">{displaySprDays}D</span>
        </button>

        {/* Bayes Tab */}
        <button 
          onClick={() => setActiveTab(activeTab === 'bayes' ? null : 'bayes')}
          className={`w-full flex flex-col items-center justify-center py-2 px-1 rounded border transition-colors ${activeTab === 'bayes' ? 'bg-tactical-amber/20 border-tactical-amber text-tactical-amber' : 'bg-panel/80 border-borderline text-slate-400 hover:border-tactical-amber/50'}`}>
          <span className="text-[8px] uppercase tracking-wider mb-1">POST</span>
          <span className="text-[10px] font-bold">{threatScore}%</span>
        </button>

        {/* MC Tab */}
        {['SIMULATING', 'OPTIMIZING', 'RECOMMENDING'].includes(phase) && (
          <button 
            onClick={() => setActiveTab(activeTab === 'mc' ? null : 'mc')}
            className={`w-full flex flex-col items-center justify-center py-2 px-1 rounded border transition-colors ${activeTab === 'mc' ? 'bg-tactical-purple/20 border-tactical-purple text-tactical-purple' : 'bg-panel/80 border-borderline text-slate-400 hover:border-tactical-purple/50'}`}>
            <span className="text-[8px] uppercase tracking-wider mb-1">MC</span>
            <span className="text-[10px] font-bold">{sprDays}D</span>
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

        {/* Intel Tab */}
        {['EXECUTING', 'ANALYZING', 'SIMULATING', 'OPTIMIZING', 'RECOMMENDING'].includes(phase) && (
          <button 
            onClick={() => setActiveTab(activeTab === 'intel' ? null : 'intel')}
            className={`w-full flex flex-col items-center justify-center py-2 px-1 rounded border transition-colors ${activeTab === 'intel' ? 'bg-tactical-cyan/20 border-tactical-cyan text-tactical-cyan' : 'bg-panel/80 border-borderline text-slate-400 hover:border-tactical-cyan/50'}`}>
            <span className="text-[8px] uppercase tracking-wider mb-1">AI</span>
            <span className="text-[10px] font-bold">INTEL</span>
          </button>
        )}
      </div>

    </div>
  );
}