import { Gauge } from 'lucide-react'

function SprWidget({ daysRemaining }) {
  return (
    <section className="rounded-xl border border-slate-700 bg-slate-900 p-4">
      <div className="flex items-center gap-2 text-cyan-300">
        <Gauge className="h-4 w-4" />
        <h2 className="text-sm font-semibold">SPR Countdown</h2>
      </div>
      <p className="mt-2 text-3xl font-bold">{daysRemaining} days</p>
      <p className="mt-1 text-xs text-slate-400">Strategic Petroleum Reserve projected autonomy window.</p>
    </section>
  )
}

export default SprWidget
