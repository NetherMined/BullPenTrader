import { useEffect, useRef, useState } from 'react'
import { createChart, IChartApi, ISeriesApi } from 'lightweight-charts'

const API = 'http://localhost:8000'

export default function App() {
  const chartRef = useRef<HTMLDivElement>(null)
  const chartApi = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)
  const [symbol, setSymbol] = useState('BTCUSDT')
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
      timeScale: { timeVisible: true },
    })
    const series = chart.addCandlestickSeries()
    chartApi.current = chart
    seriesRef.current = series
    return () => chart.remove()
  }, [])

  const loadChart = async (sym: string) => {
    try {
      const res = await fetch(`${API}/klines?symbol=${sym}&interval=1h&limit=120`)
      const data = await res.json()
      if (seriesRef.current && data.candles) {
        seriesRef.current.setData(data.candles)
        chartApi.current?.timeScale().fitContent()
      }
    } catch (e) {
      console.error(e)
    }
  }

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
    loadChart(symbol)
    loadSignals()
    loadPaper()
    const id = setInterval(loadPaper, 15000)
    return () => clearInterval(id)
  }, [symbol])

  const openFromSignal = async (s: any) => {
    await fetch(`${API}/paper/open?symbol=${s.symbol}&side=${s.side}&size_usd=100`, { method: 'POST' })
    loadPaper()
    if (s.symbol !== symbol) setSymbol(s.symbol)
  }

  const closePos = async (id: string) => {
    await fetch(`${API}/paper/close/${id}`, { method: 'POST' })
    loadPaper()
  }

  return (
    <div style={{ background: '#0e1117', color: '#d1d4dc', minHeight: '100vh', padding: 16, fontFamily: 'system-ui' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h1 style={{ margin: 0 }}>BullPenTrader — Paper</h1>
        <select value={symbol} onChange={(e) => setSymbol(e.target.value)} style={{ padding: 6 }}>
          <option>BTCUSDT</option>
          <option>ETHUSDT</option>
          <option>SOLUSDT</option>
        </select>
      </div>

      <div ref={chartRef} style={{ width: '100%', marginBottom: 16 }} />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 16 }}>
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
              <p>Open PnL: ${paper.open_pnl}</p>
              <p>Open positions: {paper.open_positions}</p>
              {paper.positions?.map((p: any) => (
                <div key={p.id} style={{ fontSize: 13, marginBottom: 8, padding: 6, border: '1px solid #2a2e39', borderRadius: 4 }}>
                  <div>{p.symbol} {p.side} ${p.size_usd}</div>
                  <div>Entry: {p.entry_price} → Mark: {p.mark_price ?? '—'}</div>
                  <div style={{ color: p.pnl >= 0 ? '#0ecb81' : '#f6465d' }}>PnL: ${p.pnl}</div>
                  <button onClick={() => closePos(p.id)} style={{ fontSize: 12, marginTop: 4 }}>Close</button>
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
