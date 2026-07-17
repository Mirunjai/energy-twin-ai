import { useEffect, useState } from 'react'

import AgentTelemetry from './components/AgentTelemetry'
import MapView from './components/MapView'
import RecommendationCard from './components/RecommendationCard'
import SprWidget from './components/SprWidget'

function App() {
  const [backendStatus, setBackendStatus] = useState('connecting')

  useEffect(() => {
    const fetchBackendState = async () => {
      try {
        const response = await fetch('http://localhost:8000/health')
        const data = await response.json()
        setBackendStatus(data.status ?? 'unknown')
      } catch {
        setBackendStatus('offline')
      }
    }

    fetchBackendState()
  }, [])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <main className="mx-auto grid max-w-7xl gap-4 p-4 lg:grid-cols-[2fr_1fr]">
        <section className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
          <MapView />
        </section>
        <aside className="space-y-4">
          <AgentTelemetry latencyMs={1800} />
          <SprWidget daysRemaining={27} />
          <RecommendationCard />
          <div className="rounded-xl border border-slate-700 bg-slate-900 p-4 text-xs text-slate-400">
            Backend health: <span className="font-semibold text-slate-200">{backendStatus}</span>
          </div>
        </aside>
      </main>
    </div>
  )
}

export default App
