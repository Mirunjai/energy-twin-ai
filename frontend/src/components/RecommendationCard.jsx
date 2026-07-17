const inrFormatter = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
})

const mockRecommendation = {
  route: 'West Coast Spot Blend Diversion',
  projectedSavings: 58000000,
  hedgeBuffer: 12000000,
}

function RecommendationCard() {
  return (
    <section className="rounded-xl border border-slate-700 bg-slate-900 p-4">
      <h2 className="text-sm font-semibold text-slate-200">Financial Recommendation</h2>
      <p className="mt-2 text-sm text-slate-400">{mockRecommendation.route}</p>
      <p className="mt-3 text-lg font-semibold text-emerald-300">
        Estimated Savings: {inrFormatter.format(mockRecommendation.projectedSavings)}
      </p>
      <p className="text-sm text-amber-300">
        Hedge Buffer: {inrFormatter.format(mockRecommendation.hedgeBuffer)}
      </p>
    </section>
  )
}

export default RecommendationCard
