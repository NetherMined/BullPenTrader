import { useEffect, useRef, useState } from 'react'
import { createChart } from 'lightweight-charts'

const API = 'http://localhost:8000'

export default function App() {
  const chartRef = useRef<HTMLDivElement>(null)
  const [signals, setSignals] = useState<any[]>([])
  const [paper, setPaper] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!chartRef.current) return
    const chart = createChart(chartRef.current, {
      width: chartRef.current.clientWidth,
      height: 420,
      layout: { background: { color: '#0e1117' }, textColor: '#d1d4dc' },
      grid: { vertLines: { color: '#1e222d' }, horzLines: { color: '#1e222d' } },
    })
    const series = chart.addCandlestickSeries()
    series.setData([
      { time: '2026-10-21', open: 65000, high: 65500, low: 64800, close: 65200 },
    ])
    return () => chart.remove()
  }, [])

  const loadSignals = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API}/signals?mapped=true&limit=12`)
      const data = await res.json()
      setSignals(data.signals || [])
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  const loadPaper = async () => {
    const res = await fetch(`${API}/paper`)
    setPaper(await res.json())
  }

  useEffect(() => {
    loadSignals()
    loadPaper()
  }, [])

  const openFromSignal = async (s: any) => {
    await fetch(`${API}/paper/open?symbol=${s.symbol}&side=${s.side}&size_usd=100`, { method: 'POST' })
    loadPaper()
  }

  return (
    <div style={{ background: '#0e1117', color: '#d1d4dc', minHeight: '100vh', padding: 16, fontFamily: 'system-ui' }}>
      <h1 style={{ margin: '0 0 12px' }}>BullPenTrader — Paper</h1>

      <div ref={chartRef} style={{ width: '100%', marginBottom: 16 }} />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 16 }}>
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ margin: 0 }}>Signals</h2>
            <button onClick={loadSignals} disabled={loading} style={{ padding: '6px 12px' }}>
              {loading ? 'Loading…' : 'Refresh'}
            </button>
          </div>
          <div style={{ maxHeight: 420, overflow: 'auto', marginTop: 8 }}>
            {signals.length === 0 && <p>No mapped signals yet. Ensure Bullpen CLI is logged in and backend is running.</p>}
            {signals.map((s, i) => (
              <div key={i} style={{ border: '1px solid #2a2e39', padding: 10, marginBottom: 8, borderRadius: 6 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <strong>{s.symbol} — {s.side}</strong>
                  <span style={{ opacity: 0.7 }}>conf {s.confidence}</span>
                </div>
                <div style={{ fontSize: 13, opacity: 0.8, margin: '4px 0' }}>{s.raw_preview}</div>
                <button onClick={() => openFromSignal(s)} style={{ fontSize: 12, padding: '4px 8px' }}>
                  Paper open $100
                </button>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 style={{ marginTop: 0 }}>Paper</h2>
          {paper && (
            <div>
              <p>Balance: ${paper.balance}</p>
              <p>Equity: ${paper.equity}</p>
              <p>Open: {paper.open_positions}</p>
              {paper.positions?.map((p: any) => (
                <div key={p.id} style={{ fontSize: 13, marginBottom: 6 }}>
                  {p.symbol} {p.side} ${p.size_usd} @ {p.entry_price}
                </div>
              ))}
              <button onClick={loadPaper} style={{ marginTop: 8 }}>Refresh</button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
