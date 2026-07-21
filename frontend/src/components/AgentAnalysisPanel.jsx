import React from 'react';
import { BrainCircuit, ArrowDown } from 'lucide-react';

export default function AgentAnalysisPanel({ agentAnalysis }) {
  if (!agentAnalysis) return null;

  const escalation = agentAnalysis.escalation_status || "NORMAL";
  const hiddenState = agentAnalysis.current_hidden_state || "UNKNOWN";
  
  const reasoning = agentAnalysis.reasoning_trail || {};
  const systemConfidence = reasoning.overall_system_confidence || 0.65;
  const confidencePct = (systemConfidence * 100).toFixed(0);
  
  const evidenceCards = agentAnalysis.evidence_cards || [];
  const firstEvidence = evidenceCards.length > 0 ? evidenceCards[0] : null;

  const geoRisk = agentAnalysis.geo?.posterior_probability || 0.18;
  const geoRiskPct = (geoRisk * 100).toFixed(0);
  const geoSeverity = geoRisk > 0.75 ? "CRITICAL" : geoRisk > 0.5 ? "HIGH" : geoRisk > 0.25 ? "MODERATE" : "LOW";

  const commFinalCapacity = agentAnalysis.comm?.final_capacity || 100;
  const commRisk = 1 - (commFinalCapacity / 100);
  const commRiskPct = (commRisk * 100).toFixed(0);
  const commSeverity = commRisk > 0.7 ? "CRITICAL" : commRisk > 0.4 ? "ELEVATED" : "STABLE";

  const disagreement = reasoning.disagreement_context || "NONE";
  
  const getBadgeStyle = (status) => {
    if (status.includes("ESCALATE")) return "bg-tactical-red/20 text-tactical-red border-tactical-red/50";
    if (status.includes("CONSENSUS") || status.includes("NORMAL")) return "bg-tactical-green/20 text-tactical-green border-tactical-green/50";
    return "bg-tactical-amber/20 text-tactical-amber border-tactical-amber/50";
  };

  const getConfLabel = (conf) => {
    if (conf >= 0.8) return "HIGH";
    if (conf >= 0.4) return "MED";
    return "LOW";
  };

  const timeline = [
    { text: "Threat Detected", active: true },
    { text: "Bayesian Update", active: reasoning.bayesian_evidence },
    { text: "Lanchester Simulation", active: reasoning.lanchester_evidence },
    { text: "Historical Match", active: evidenceCards.length > 0 },
    { text: "Hidden State Inference", active: !!hiddenState },
    { text: "Decision", active: true }
  ];

  return (
    <div className="backdrop-blur-md bg-panel/90 border border-borderline rounded shadow-2xl p-4 flex flex-col space-y-4">
      
      {/* SECTION 1: Title */}
      <div className="flex items-center justify-between border-b border-borderline pb-2">
        <div className="flex flex-col">
          <div className="flex items-center space-x-2">
            <BrainCircuit className="w-4 h-4 text-tactical-cyan" />
            <h3 className="text-xs font-bold text-tactical-cyan tracking-widest">AI REASONING</h3>
          </div>
          <span className="text-[8px] text-slate-500 uppercase tracking-wider mt-0.5">Explain why the system reached its decision.</span>
        </div>
      </div>

      {/* Decision Support Badge & Confidence */}
      <div className="grid grid-cols-2 gap-2">
        <div className="p-2 bg-console/50 rounded border border-borderline/50 flex flex-col items-center justify-center">
          <span className="text-[8px] text-slate-500 uppercase tracking-wider mb-1">Decision Support Status</span>
          <span className={`px-2 py-0.5 rounded text-[10px] font-bold border uppercase ${getBadgeStyle(escalation)}`}>
            {escalation.includes("ESCALATE") ? "ESCALATE" : escalation.includes("REVIEW") ? "REVIEW" : escalation.includes("MONITORING") ? "REVIEW" : "NORMAL"}
          </span>
        </div>
        <div className="p-2 bg-console/50 rounded border border-borderline/50 flex flex-col justify-center">
          <div className="flex justify-between items-center mb-1 text-[9px] uppercase tracking-wider">
            <span className="text-slate-500">System Confidence</span>
            <span className="text-slate-300 font-bold">{getConfLabel(systemConfidence)} {confidencePct}%</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden flex">
            <div className={`h-full ${systemConfidence >= 0.8 ? 'bg-tactical-green' : systemConfidence >= 0.4 ? 'bg-tactical-amber' : 'bg-tactical-red'}`} style={{ width: `${confidencePct}%` }}></div>
          </div>
        </div>
      </div>

      {/* Agent Consensus */}
      <div className="p-2 bg-console/30 rounded border border-borderline/30 space-y-2">
        <div className="text-[9px] text-slate-500 uppercase tracking-wider mb-1 border-b border-borderline/30 pb-1">Agent Consensus</div>
        
        <div className="flex justify-between items-end">
          <div className="text-[9px] font-bold text-slate-300">Agent 1 <span className="text-slate-500 font-normal ml-1">Geopolitical</span></div>
          <div className="text-[9px] text-slate-400">{geoRisk.toFixed(2)} <span className={`ml-1 ${geoRisk > 0.5 ? 'text-tactical-red' : 'text-slate-500'}`}>{geoSeverity} Risk</span></div>
        </div>
        <div className="w-full bg-slate-800 h-1 rounded-sm overflow-hidden"><div className="bg-tactical-cyan h-1" style={{ width: `${geoRiskPct}%` }}></div></div>

        <div className="flex justify-between items-end pt-1">
          <div className="text-[9px] font-bold text-slate-300">Agent 2 <span className="text-slate-500 font-normal ml-1">Logistics</span></div>
          <div className="text-[9px] text-slate-400">{commRisk.toFixed(2)} <span className={`ml-1 ${commRisk > 0.5 ? 'text-tactical-red' : 'text-slate-500'}`}>{commSeverity} Risk</span></div>
        </div>
        <div className="w-full bg-slate-800 h-1 rounded-sm overflow-hidden mb-2"><div className="bg-tactical-cyan h-1" style={{ width: `${commRiskPct}%` }}></div></div>

        <div className={`text-[9px] p-1.5 rounded font-bold border mt-2 ${disagreement !== "NONE" ? "bg-tactical-amber/10 border-tactical-amber/50 text-tactical-amber" : "bg-tactical-green/10 border-tactical-green/50 text-tactical-green"}`}>
          {disagreement !== "NONE" ? `⚠ Disagreement: ${disagreement}` : "✔ Consensus Reached"}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {/* Reasoning Pipeline */}
        <div className="p-2 bg-console/50 rounded border border-borderline/50">
          <div className="text-[9px] text-slate-500 uppercase tracking-wider mb-2">Reasoning Pipeline</div>
          <div className="flex flex-col items-center space-y-1">
            {timeline.filter(t => t.active).map((step, idx, arr) => (
              <React.Fragment key={idx}>
                <div className={`text-[8px] px-1.5 py-0.5 rounded border border-borderline/50 text-slate-300 bg-panel/50 w-full text-center truncate ${idx === arr.length - 1 ? 'animate-pulse text-tactical-cyan border-tactical-cyan/50' : ''}`}>
                  {step.text}
                </div>
                {idx < arr.length - 1 && (
                  <ArrowDown className="w-3 h-3 text-slate-600" />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Evidence Card */}
        <div className="p-2 bg-console/50 rounded border border-borderline/50 flex flex-col">
          <div className="text-[9px] text-slate-500 uppercase tracking-wider mb-2">Historical Match</div>
          {firstEvidence ? (
            <div className="space-y-1 text-[9px] leading-relaxed flex-grow flex flex-col justify-between">
              <div>
                <div className="flex flex-col mb-1">
                  <span className="font-bold text-slate-200 truncate">{firstEvidence.title || "Analogue"}</span>
                  <span className="text-tactical-cyan">{(firstEvidence.similarity_score * 100).toFixed(0)}% Similar</span>
                </div>
                {firstEvidence.metadata?.threat && <div className="text-tactical-red truncate mb-0.5">Threat: {firstEvidence.metadata.threat}</div>}
                <div className="text-slate-400 italic line-clamp-3">"{firstEvidence.summary}"</div>
              </div>
              <div className="text-slate-600 truncate mt-1 pt-1 border-t border-borderline/30">
                [{firstEvidence.citation || "Source"}]
              </div>
            </div>
          ) : (
            <div className="text-[9px] text-slate-500 italic mt-2">No analogue.</div>
          )}
        </div>
      </div>

    </div>
  );
}
