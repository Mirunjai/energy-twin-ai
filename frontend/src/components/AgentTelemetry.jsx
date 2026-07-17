import { Activity } from 'lucide-react'

function AgentTelemetry({ latencyMs }) {
  const underFiveSeconds = latencyMs < 5000

  return (
    <section className="rounded-xl border border-emerald-500/30 bg-slate-900/80 p-4 shadow-lg shadow-emerald-900/20">
      <div className="mb-2 flex items-center gap-2 text-emerald-300">
        <Activity className="h-4 w-4" />
        <h2 className="text-sm font-semibold">Agent Telemetry</h2>
      </div>
      <p className="text-2xl font-bold">{(latencyMs / 1000).toFixed(2)}s</p>
      <p className="mt-1 text-xs text-slate-300">
        {underFiveSeconds ? 'Sub-5-second processing target achieved.' : 'Latency warning: above 5 seconds.'}
      </p>
    </section>
  )
}

export default AgentTelemetry
