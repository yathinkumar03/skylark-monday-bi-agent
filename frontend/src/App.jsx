import { useState } from 'react'
import './App.css'

const API_URL = 'http://127.0.0.1:8000'

const exampleQuestions = [
  {
    icon: '↗',
    label: 'Pipeline',
    question: "How's our pipeline looking for renewables this quarter?",
  },
  {
    icon: '◆',
    label: 'Top Sector',
    question: 'Which sector has the largest pipeline?',
  },
  {
    icon: '₹',
    label: 'Revenue',
    question: 'How much revenue do we have?',
  },
  {
    icon: '▦',
    label: 'Operations',
    question: 'Show me our work orders',
  },
  {
    icon: '◉',
    label: 'Billing',
    question: 'What is happening with billing?',
  },
]

function App() {
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const askQuestion = async () => {
    if (!question.trim() || loading) return

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          question: question.trim(),
        }),
      })

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(
        'Unable to connect to the BI Agent. Please make sure the backend server is running.'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      askQuestion()
    }
  }

  const useExample = (example) => {
    setQuestion(example)
    setResult(null)
    setError('')
  }

  const resetQuery = () => {
    setQuestion('')
    setResult(null)
    setError('')
  }

  const getIntentLabel = () => {
    if (!result?.intent?.intent) return 'BUSINESS ANALYSIS'

    return result.intent.intent
      .replaceAll('_', ' ')
      .toUpperCase()
  }

  const getPeriod = () => {
    return result?.data?.period
      ? result.data.period.replaceAll('_', ' ').toUpperCase()
      : 'ALL TIME'
  }

  return (
    <div className="app">

      {/* =====================================================
          BACKGROUND
      ===================================================== */}

      <div className="background-grid"></div>

      <div className="ambient ambient-one"></div>
      <div className="ambient ambient-two"></div>
      <div className="ambient ambient-three"></div>


      {/* =====================================================
          TOP NAVIGATION
      ===================================================== */}

      <header className="topbar">

        <div className="brand">

          <div className="brand-logo">
            <span></span>
            <span></span>
            <span></span>
          </div>

          <div className="brand-info">
            <div className="brand-name">
              SKYLARK
            </div>

            <div className="brand-subtitle">
              BUSINESS INTELLIGENCE
            </div>
          </div>

        </div>


        <div className="topbar-right">

          <div className="system-status">
            <span className="status-light"></span>

            <div>
              <strong>LIVE</strong>
              <small>MONDAY.COM</small>
            </div>
          </div>

          <div className="version">
            AI / BI
          </div>

        </div>

      </header>


      {/* =====================================================
          MAIN CONTENT
      ===================================================== */}

      <main className="main">


        {/* =================================================
            HERO
        ================================================= */}

        {!result && !loading && (

          <section className="hero">

            <div className="hero-tag">

              <span className="tag-line"></span>

              <span>INTELLIGENT BUSINESS ANALYTICS</span>

              <span className="tag-line"></span>

            </div>


            <h1>

              <span className="hero-main">
                Ask your business.
              </span>

              <span className="hero-gradient">
                Get intelligent answers.
              </span>

            </h1>


            <p className="hero-description">

              Turn your Monday.com data into actionable business intelligence.
              Ask questions naturally across pipeline, revenue, operations and billing.

            </p>


            <div className="hero-stats">

              <div>
                <strong>01</strong>
                <span>Pipeline</span>
              </div>

              <div>
                <strong>02</strong>
                <span>Revenue</span>
              </div>

              <div>
                <strong>03</strong>
                <span>Operations</span>
              </div>

              <div>
                <strong>04</strong>
                <span>Billing</span>
              </div>

            </div>

          </section>

        )}


        {/* =================================================
            QUERY AREA
        ================================================= */}

        <section className="query-wrapper">

          <div className="query-card">

            <div className="query-card-top">

              <div className="analyst-label">

                <div className="analyst-icon">
                  ✦
                </div>

                <div>
                  <span>SKYLARK AI</span>
                  <small>BUSINESS ANALYST</small>
                </div>

              </div>


              <div className="keyboard-hint">

                <kbd>ENTER</kbd>

                <span>to analyze</span>

              </div>

            </div>


            <div className="input-area">

              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask a question about your business..."
                rows="3"
              />

              <div className="input-glow"></div>

            </div>


            <div className="query-bottom">

              <div className="query-capability">

                <span className="sparkle">
                  ✦
                </span>

                <span>
                  Natural language → Business intelligence
                </span>

              </div>


              <button
                className="ask-button"
                onClick={askQuestion}
                disabled={loading || !question.trim()}
              >

                {loading ? (
                  <>
                    <span className="button-spinner"></span>
                    ANALYZING
                  </>
                ) : (
                  <>
                    ANALYZE
                    <span className="button-arrow">→</span>
                  </>
                )}

              </button>

            </div>

          </div>

        </section>


        {/* =================================================
            QUICK QUESTIONS
        ================================================= */}

        {!result && !loading && (

          <section className="quick-section">

            <div className="section-heading">

              <div>
                <span className="section-number">
                  01
                </span>

                <span>
                  QUICK ANALYSIS
                </span>
              </div>

              <p>
                Start with a suggested business question
              </p>

            </div>


            <div className="quick-grid">

              {exampleQuestions.map((item) => (

                <button
                  className="quick-card"
                  key={item.label}
                  onClick={() => useExample(item.question)}
                >

                  <div className="quick-card-icon">
                    {item.icon}
                  </div>


                  <div className="quick-card-content">

                    <strong>
                      {item.label}
                    </strong>

                    <span>
                      {item.question}
                    </span>

                  </div>


                  <div className="quick-card-arrow">
                    →
                  </div>

                </button>

              ))}

            </div>

          </section>

        )}


        {/* =================================================
            LOADING
        ================================================= */}

        {loading && (

          <section className="loading-container">

            <div className="loading-card">

              <div className="loading-visual">

                <div className="orbit orbit-one"></div>
                <div className="orbit orbit-two"></div>

                <div className="loading-core">
                  ✦
                </div>

              </div>


              <div className="loading-content">

                <div className="loading-label">
                  LIVE ANALYSIS
                </div>

                <h2>
                  Analyzing your business
                </h2>

                <p>
                  Connecting to Monday.com and processing your business data.
                </p>

                <div className="loading-progress">
                  <span></span>
                </div>

              </div>

            </div>

          </section>

        )}


        {/* =================================================
            ERROR
        ================================================= */}

        {error && (

          <section className="error-container">

            <div className="error-card">

              <div className="error-symbol">
                !
              </div>

              <div>

                <strong>
                  CONNECTION ERROR
                </strong>

                <p>
                  {error}
                </p>

              </div>

              <button
                onClick={askQuestion}
              >
                RETRY
              </button>

            </div>

          </section>

        )}


        {/* =================================================
            RESULT
        ================================================= */}

        {result && !loading && (

          <section className="result-section">


            {/* RESULT HEADER */}

            <div className="result-header">

              <div>

                <div className="result-status">

                  <span></span>

                  ANALYSIS COMPLETE

                </div>

                <h2>
                  Business Intelligence
                </h2>

                <p>
                  Your business question has been analyzed against live data.
                </p>

              </div>


              <button
                className="new-query"
                onClick={resetQuery}
              >
                <span>+</span>
                NEW QUERY
              </button>

            </div>


            {/* QUESTION */}

            <div className="asked-card">

              <div className="asked-label">
                YOU ASKED
              </div>

              <div className="asked-question">
                “{result.question}”
              </div>

            </div>


            {/* SUMMARY METRICS */}

            <div className="result-metrics">

              <div className="metric-card">

                <span className="metric-label">
                  ANALYSIS TYPE
                </span>

                <strong>
                  {getIntentLabel()}
                </strong>

              </div>


              <div className="metric-card">

                <span className="metric-label">
                  DATA PERIOD
                </span>

                <strong>
                  {getPeriod()}
                </strong>

              </div>


              <div className="metric-card">

                <span className="metric-label">
                  DATA SOURCE
                </span>

                <strong>
                  MONDAY.COM
                </strong>

              </div>


              <div className="metric-card verified">

                <span className="metric-label">
                  STATUS
                </span>

                <strong>
                  ✓ VERIFIED
                </strong>

              </div>

            </div>


            {/* AI ANSWER */}

            <div className="answer-card">

              <div className="answer-header">

                <div className="answer-title">

                  <div className="answer-icon">
                    ✦
                  </div>

                  <div>

                    <span>
                      AI INSIGHT
                    </span>

                    <small>
                      SKYLARK BUSINESS ANALYST
                    </small>

                  </div>

                </div>


                <div className="intent-badge">

                  {getIntentLabel()}

                </div>

              </div>


              <div className="answer-content">

                {result.answer || result.message}

              </div>

            </div>


            {/* RAW DATA */}

            {result.data && (

              <details className="raw-data">

                <summary>

                  <div>

                    <span className="raw-number">
                      02
                    </span>

                    <span>
                      ANALYSIS DATA
                    </span>

                  </div>

                  <span className="expand">
                    VIEW DATA +
                  </span>

                </summary>


                <div className="raw-content">

                  <pre>
                    {JSON.stringify(result.data, null, 2)}
                  </pre>

                </div>

              </details>

            )}


            {/* NEW QUESTION */}

            <div className="result-footer">

              <span>
                Want to explore another metric?
              </span>

              <button
                onClick={resetQuery}
              >
                ASK ANOTHER QUESTION →
              </button>

            </div>

          </section>

        )}

      </main>


      {/* =====================================================
          FOOTER
      ===================================================== */}

      <footer className="footer">

        <div className="footer-brand">

          <span className="footer-mark">
            ◈
          </span>

          <span>
            SKYLARK
          </span>

        </div>


        <div className="footer-center">

          BUSINESS INTELLIGENCE AGENT

        </div>


        <div className="footer-status">

          <span></span>

          LIVE DATA CONNECTION

        </div>

      </footer>

    </div>
  )
}

export default App