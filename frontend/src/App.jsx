import { useState } from 'react'
import './App.css'

const API_URL = 'http://127.0.0.1:8000'

function App() {
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const askQuestion = async (text = question) => {
    const query = text.trim()

    if (!query) return

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: query,
        }),
      })

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(
        'Unable to connect to the BI backend. Make sure FastAPI is running on port 8000.'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    askQuestion()
  }

  const exampleQuestions = [
    "How's our pipeline looking for renewables this quarter?",
    'Which sector has the largest pipeline?',
    'How much revenue do we have?',
    'Show me our work orders',
    'What is happening with billing?',
  ]

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <div className="brand-icon">S</div>

          <div>
            <h1>Skylark BI Agent</h1>
            <p>Monday.com Business Intelligence</p>
          </div>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          Connected
        </div>
      </header>

      <main className="main">
        <section className="hero-section">
          <div className="eyebrow">BUSINESS INTELLIGENCE</div>

          <h2>
            Ask your business
            <br />
            <span>anything.</span>
          </h2>

          <p className="hero-description">
            Get real-time insights from your Monday.com deals and work orders.
          </p>

          <form className="question-form" onSubmit={handleSubmit}>
            <div className="input-wrapper">
              <span className="search-icon">⌕</span>

              <input
                type="text"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Ask a business question..."
                disabled={loading}
              />

              <button type="submit" disabled={loading || !question.trim()}>
                {loading ? 'Analyzing...' : 'Ask'}
              </button>
            </div>
          </form>

          <div className="examples">
            <span>Try asking:</span>

            {exampleQuestions.map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => {
                  setQuestion(item)
                  askQuestion(item)
                }}
                disabled={loading}
              >
                {item}
              </button>
            ))}
          </div>
        </section>

        {loading && (
          <section className="loading-card">
            <div className="loader"></div>

            <div>
              <strong>Analyzing your data</strong>
              <p>
                Fetching the latest information from Monday.com and processing
                your question...
              </p>
            </div>
          </section>
        )}

        {error && (
          <section className="error-card">
            <div className="error-icon">!</div>

            <div>
              <strong>Connection error</strong>
              <p>{error}</p>
            </div>
          </section>
        )}

        {result && !loading && (
          <section className="result-section">
            <div className="result-header">
              <div>
                <div className="result-label">ANALYSIS RESULT</div>
                <h3>{result.question}</h3>
              </div>

              <div className="intent-badge">
                {result.intent?.intent || 'general'}
              </div>
            </div>

            <div className="answer-card">
              <div className="answer-header">
                <div className="answer-icon">✦</div>

                <div>
                  <span>BI AGENT</span>
                  <h4>Business Analysis</h4>
                </div>
              </div>

              <div className="answer-text">
                {result.answer || result.message}
              </div>
            </div>

            {result.data && (
              <DataDisplay data={result.data} answerType={result.answer_type} />
            )}

            {result.warnings && result.warnings.length > 0 && (
              <div className="warnings-card">
                <div className="warnings-title">
                  <span>⚠</span>
                  Data quality notes
                </div>

                {result.warnings.map((warning, index) => (
                  <div className="warning" key={index}>
                    {warning}
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {!result && !loading && !error && (
          <section className="feature-section">
            <div className="feature">
              <div className="feature-icon">↗</div>
              <h3>Pipeline Intelligence</h3>
              <p>
                Analyze deals, pipeline value, weighted pipeline and sector
                performance.
              </p>
            </div>

            <div className="feature">
              <div className="feature-icon">₹</div>
              <h3>Revenue Insights</h3>
              <p>
                Track billed revenue, collections and outstanding amounts.
              </p>
            </div>

            <div className="feature">
              <div className="feature-icon">◫</div>
              <h3>Operations</h3>
              <p>
                Understand work orders, sectors and operational status.
              </p>
            </div>
          </section>
        )}
      </main>

      <footer>
        <span>Skylark Monday BI Agent</span>
        <span>Powered by FastAPI + React + Monday.com</span>
      </footer>
    </div>
  )
}

function DataDisplay({ data, answerType }) {
  if (answerType === 'pipeline') {
    return (
      <div className="metrics-grid">
        <MetricCard
          label="Pipeline Value"
          value={formatCurrency(data.pipeline_value)}
        />

        <MetricCard
          label="Weighted Pipeline"
          value={formatCurrency(data.weighted_pipeline)}
        />

        <MetricCard
          label="Deals"
          value={data.deal_count ?? 0}
        />

        <MetricCard
          label="Period"
          value={formatPeriod(data.period)}
        />
      </div>
    )
  }

  if (answerType === 'revenue') {
    return (
      <div className="metrics-grid">
        <MetricCard
          label="Billed Revenue"
          value={formatCurrency(data.billed_revenue)}
        />

        <MetricCard
          label="Collected Revenue"
          value={formatCurrency(data.collected_revenue)}
        />

        <MetricCard
          label="Outstanding"
          value={formatCurrency(data.outstanding_revenue)}
        />

        <MetricCard
          label="Work Orders"
          value={data.work_order_count ?? 0}
        />
      </div>
    )
  }

  if (answerType === 'sector_breakdown' && Array.isArray(data)) {
    return (
      <div className="table-card">
        <div className="table-title">Sector Breakdown</div>

        <div className="table">
          <div className="table-row table-head">
            <span>Sector</span>
            <span>Deals</span>
            <span>Pipeline</span>
          </div>

          {data.map((sector, index) => (
            <div className="table-row" key={index}>
              <span>{sector.sector_clean}</span>
              <span>{sector.deal_count}</span>
              <span>{formatCurrency(sector.pipeline_value)}</span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (answerType === 'operations') {
    return (
      <div className="distribution-grid">
        <DistributionCard
          title="Work Orders by Sector"
          data={data.sector_distribution}
        />

        <DistributionCard
          title="Billing Status"
          data={data.billing_status_distribution}
        />
      </div>
    )
  }

  return null
}

function MetricCard({ label, value }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

function DistributionCard({ title, data }) {
  if (!data) return null

  return (
    <div className="distribution-card">
      <h4>{title}</h4>

      {Object.entries(data).map(([key, value]) => (
        <div className="distribution-row" key={key}>
          <span>{key}</span>
          <strong>{value}</strong>
        </div>
      ))}
    </div>
  )
}

function formatCurrency(value) {
  const number = Number(value || 0)

  if (number >= 10000000) {
    return `₹${(number / 10000000).toFixed(2)} Cr`
  }

  if (number >= 100000) {
    return `₹${(number / 100000).toFixed(2)} L`
  }

  return `₹${number.toLocaleString('en-IN', {
    maximumFractionDigits: 0,
  })}`
}

function formatPeriod(period) {
  if (!period) return 'All time'

  return period
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

export default App