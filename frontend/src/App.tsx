import { useEffect, useRef } from 'react'
import { createChart } from 'lightweight-charts'

export default function App() {
  const chartRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!chartRef.current) return
    const chart = createChart(chartRef.current, {
      width: chartRef.current.clientWidth,
      height: 500,
      layout: { background: { color: '#0e1117' }, textColor: '#d1d4dc' },
      grid: { vertLines: { color: '#1e222d' }, horzLines: { color: '#1e222d' } },
    })
    const series = chart.addCandlestickSeries()
    // TODO: feed paper or Binance testnet data
    series.setData([
      { time: '2026-10-21', open: 65000, high: 65500, low: 64800, close: 65200 },
    ])
    return () => chart.remove()
  }, [])

  return (
    <div style={{ background: '#0e1117', color: '#fff', minHeight: '100vh', padding: 16 }}>
      <h1>BullPenTrader — Paper</h1>
      <div ref={chartRef} style={{ width: '100%' }} />
      <div style={{ marginTop: 16 }}>
        <button>Buy</button>
        <button style={{ marginLeft: 8 }}>Sell</button>
      </div>
    </div>
  )
}
