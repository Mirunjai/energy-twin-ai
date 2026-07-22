import React, { createContext, useContext, useState } from 'react';

const UIContext = createContext(null);

export function UIProvider({ children }) {
  const [phase, setPhase] = useState('MONITORING');

  // Derived UI State
  const isMonitoring = phase === 'MONITORING';
  const isExecuting = phase === 'EXECUTING';
  const isRunning = phase !== 'MONITORING' && phase !== 'RECOMMENDING';
  const hasRecommendation = phase === 'RECOMMENDING';

  // The central animation controller
  const animatePipeline = async (phases) => {
    for (const { state, delay } of phases) {
      await new Promise(resolve => setTimeout(resolve, delay));
      setPhase(state);
    }
  };

  // Reset the UI back to a clean monitoring state
  const resetToMonitoring = () => {
    setPhase('MONITORING');
  };

  return (
    <UIContext.Provider value={{ 
      phase, setPhase, isMonitoring, isExecuting, 
      isRunning, hasRecommendation, animatePipeline, resetToMonitoring
    }}>
      {children}
    </UIContext.Provider>
  );
}

export const useUI = () => {
  const context = useContext(UIContext);
  if (!context) throw new Error("useUI must be used within UIProvider");
  return context;
};