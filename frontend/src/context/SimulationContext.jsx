import React, { createContext, useContext, useState } from 'react';
import { triggerCrisisSimulation } from '../services/api';
import { useUI } from './UIProvider';

const SimulationContext = createContext(null);

export function SimulationProvider({ children }) {
  const { setPhase, animatePipeline } = useUI();
  
  const [simulation, setSimulation] = useState({
    geo: null,
    monteCarlo: null,
    procurement: null,
    agentAnalysis: null
  });
  
  const [telemetry, setTelemetry] = useState({
    networkRtt: null,
    backendProcess: null,
    reqId: null
  });

  const executeSimulation = async (payload) => {
    try {
      setPhase('INCIDENT');
      setTimeout(() => setPhase('EXECUTING'), 500); 

      // ⚠️ IMPORTANT: If you haven't built the FastAPI backend yet, this will fail.
      // For testing the UI right now, we will mock the API call if it fails.
      let data, apiTelemetry;
      
      try {
        const result = await triggerCrisisSimulation(payload);
        data = result.data;
        apiTelemetry = result.telemetry;
      } catch (e) {
        console.warn("Backend not running. Using mock pipeline data.");
        data = { geo_results: {}, monte_carlo_results: {}, optimization_results: {}, agent_analysis: {} };
        apiTelemetry = { networkLatency: 142, serverLatency: 87, requestId: 'mock_req_123' };
      }

      setSimulation({
        geo: data?.geo_results || null,
        monteCarlo: data?.monte_carlo_results || null,
        procurement: data?.optimization_results || null,
        agentAnalysis: data?.agent_analysis || null
      });

      setTelemetry({
        networkRtt: apiTelemetry?.networkLatency,
        backendProcess: apiTelemetry?.serverLatency,
        reqId: apiTelemetry?.requestId
      });

      await animatePipeline([
        { state: 'ANALYZING', delay: 800 },
        { state: 'SIMULATING', delay: 1500 },
        { state: 'OPTIMIZING', delay: 1800 },
        { state: 'RECOMMENDING', delay: 1000 }
      ]);

    } catch (error) {
      console.error("Simulation failed:", error);
      setPhase('MONITORING'); 
    }
  };

  return (
    <SimulationContext.Provider value={{ simulation, telemetry, executeSimulation }}>
      {children}
    </SimulationContext.Provider>
  );
}

export const useSimulation = () => {
  const context = useContext(SimulationContext);
  if (!context) throw new Error("useSimulation must be used within SimulationProvider");
  return context;
};