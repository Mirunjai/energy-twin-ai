import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

export const triggerCrisisSimulation = async (payload = {}) => {
  const startTime = performance.now();
  
  const defaultPayload = {
    corridor: "strait_of_hormuz",
    event_type: "kinetic_incident",
    supplier: "saudi_arabia",
    ...payload
  };

  // Idiomatic throw on failure
  const response = await apiClient.post('/crisis/trigger', defaultPayload);
  const endTime = performance.now();

  return {
    data: response.data,
    telemetry: {
      networkLatency: Math.round(endTime - startTime),
      serverLatency: parseInt(response.headers['x-system-latency-ms'], 10) ?? null,
      requestId: response.headers['x-request-id'] ?? null,
    }
  };
};