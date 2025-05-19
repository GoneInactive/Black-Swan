import { useState, useEffect } from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import './App.css'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

type GraphProps = {
  index: number
  defaultTicker: string
}

function Graph({ index, defaultTicker }: GraphProps) {
  const [ticker, setTicker] = useState(defaultTicker)
  const [prices, setPrices] = useState<number[]>([])
  const [labels, setLabels] = useState<string[]>([])

  useEffect(() => {
    const interval = setInterval(async () => {
      if (!ticker) return
      try {
        const res = await fetch(`/api/price_data?ticker=${ticker}`)
        const data = await res.json()
        setPrices((prev) => [...prev.slice(-19), data.price])
        setLabels((prev) => [...prev.slice(-19), new Date().toLocaleTimeString()])
      } catch (_) {}
    }, 5000)
    return () => clearInterval(interval)
  }, [ticker])

  const data = {
    labels,
    datasets: [
      {
        label: `${ticker}`,
        data: prices,
        fill: false,
        backgroundColor: 'green',
        borderColor: 'green'
      }
    ]
  }

  return (
    <div className="graph-container">
      <input
        type="text"
        value={ticker}
        onChange={(e) => setTicker(e.target.value.toUpperCase())}
        placeholder={`Ticker ${index + 1}`}
      />
      <Line data={data} />
    </div>
  )
}

function ScrollingTicker() {
  const [priceText, setPriceText] = useState('')

  useEffect(() => {
    const fetchPrices = async () => {
      try {
        const res = await fetch('/api/prices')
        const data = await res.json()
        const formatted = Object.entries(data)
          .map(([k, v]) => `${k.toUpperCase()}: $${parseFloat(v as string).toFixed(2)}`)
          .join('    ')
        setPriceText(formatted)
      } catch {
        const now = new Date().toLocaleTimeString()
        setPriceText(`${now}    BTC: $00.00    ETH: $00.00`)
      }
    }

    fetchPrices()
    const interval = setInterval(fetchPrices, 10000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="ticker-bar">
      <div className="ticker-text">{priceText}</div>
    </div>
  )
}

function TerminalInput() {
  const [inputVal, setInputVal] = useState('')

  const handleSubmit = async () => {
    await fetch('/api/terminal_input', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input: inputVal })
    })
    setInputVal('')
  }

  return (
    <div className="terminal-input">
      <input
        type="text"
        value={inputVal}
        onChange={(e) => setInputVal(e.target.value)}
        placeholder="Terminal Input"
        onKeyDown={(e) => {
          if (e.key === 'Enter') handleSubmit()
        }}
      />
    </div>
  )
}

function App() {
  return (
    <>
      <ScrollingTicker />
      <div className="main-content">
        <div>
          <h1 className='logo1'>T</h1><h1 className='logo2'>rade</h1><h1 className='logo1'>Byte</h1>
        </div>
        <div className="graph-grid">
          {Array.from({ length: 6 }).map((_, i) => (
            <Graph key={i} index={i} defaultTicker="BTC" />
          ))}
        </div>
        <TerminalInput />
      </div>
    </>
  )
}

export default App
