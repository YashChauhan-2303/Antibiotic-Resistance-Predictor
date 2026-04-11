import { useState, useEffect } from 'react'
import axios from 'axios'
import PredictionForm from './components/PredictionForm'
import ResultsTable from './components/ResultsTable'
import LoadingSpinner from './components/LoadingSpinner'
import ErrorAlert from './components/ErrorAlert'
import SuccessAlert from './components/SuccessAlert'
import SummaryCard from './components/SummaryCard'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

function App() {
  const [predictions, setPredictions] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [darkMode, setDarkMode] = useState(true)
  const [formData, setFormData] = useState(null)
  const [summary, setSummary] = useState(null)
  const [healthStatus, setHealthStatus] = useState('checking')

  // Check API health on component mount
  useEffect(() => {
    checkHealth()
  }, [])

  const checkHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/health`, {
        timeout: 5000,
      })
      setHealthStatus(response.data.models_loaded ? 'healthy' : 'unhealthy')
    } catch (err) {
      console.error('Health check failed:', err)
      setHealthStatus('unhealthy')
    }
  }

  const handleSubmit = async (data) => {
    setLoading(true)
    setError(null)
    setPredictions(null)
    setSummary(null)
    setSuccess(null)
    setFormData(data)

    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/predict`, data, {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 30000,
      })

      if (response.data && response.data.data) {
        setPredictions(response.data.data)
        setSummary(response.data.summary)
        setSuccess('Predictions generated successfully!')
        setTimeout(() => setSuccess(null), 5000)
      }
    } catch (err) {
      let errorMessage = 'Failed to get predictions. Please try again.'

      if (err.response) {
        errorMessage = err.response.data?.error || err.response.data?.detail || errorMessage
      } else if (err.request) {
        errorMessage = `No response from server. Make sure the backend is running on ${API_BASE_URL}`
      } else if (err.message) {
        errorMessage = err.message
      }

      setError(errorMessage)
      console.error('Prediction error:', err)
    } finally {
      setLoading(false)
    }
  }

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
  }

  return (
    <div className={`min-h-screen transition-colors duration-300 ${darkMode ? 'bg-gray-900 text-white' : 'bg-gradient-to-br from-blue-50 to-indigo-100'}`}>
      {/* Header */}
      <header className={`${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-b shadow-sm sticky top-0 z-50`}>
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl md:text-3xl font-bold text-blue-600">
              🔬 Antibiotic Resistance Predictor
            </h1>
            <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
              healthStatus === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {healthStatus === 'healthy' ? '✓ Connected' : '✗ Disconnected'}
            </div>
          </div>
          <button
            onClick={toggleDarkMode}
            className={`p-2 rounded-lg transition-colors ${darkMode ? 'bg-yellow-500 text-gray-900 hover:bg-yellow-600' : 'bg-gray-200 text-yellow-600 hover:bg-gray-300'}`}
            title="Toggle dark mode"
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Success Alert */}
        {success && <SuccessAlert message={success} />}

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Form Section */}
          <div className="fade-in">
            <div className={`card ${darkMode ? 'bg-gray-800 border border-gray-700' : ''}`}>
              <h2 className="text-2xl font-bold mb-6">Patient Information</h2>
              <PredictionForm
                onSubmit={handleSubmit}
                isLoading={loading}
                darkMode={darkMode}
                apiHealthy={healthStatus === 'healthy'}
              />
            </div>
          </div>

          {/* Results Section */}
          <div className="fade-in space-y-4">
            {loading && (
              <div className={`card flex flex-col items-center justify-center h-96 ${darkMode ? 'bg-gray-800 border border-gray-700' : ''}`}>
                <LoadingSpinner />
                <p className={`mt-4 text-lg font-semibold ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                  Analyzing resistance patterns...
                </p>
              </div>
            )}

            {error && !loading && (
              <ErrorAlert message={error} />
            )}

            {summary && !loading && (
              <>
                <SummaryCard
                  summary={summary}
                  darkMode={darkMode}
                />
                <div className={`card fade-in ${darkMode ? 'bg-gray-800 border border-gray-700' : ''}`}>
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-2xl font-bold">Detailed Results</h2>
                    <button
                      onClick={() => {
                        const dataStr = JSON.stringify({
                          input: formData,
                          results: predictions,
                          summary: summary,
                          timestamp: new Date().toISOString()
                        }, null, 2)
                        const dataBlob = new Blob([dataStr], { type: 'application/json' })
                        const url = URL.createObjectURL(dataBlob)
                        const link = document.createElement('a')
                        link.href = url
                        link.download = `predictions_${Date.now()}.json`
                        link.click()
                        URL.revokeObjectURL(url)
                      }}
                      className="btn-secondary text-sm"
                    >
                      📥 Download
                    </button>
                  </div>
                  <ResultsTable data={predictions} darkMode={darkMode} />
                </div>
              </>
            )}

            {!loading && !error && !predictions && healthStatus === 'healthy' && (
              <div className={`card flex flex-col items-center justify-center h-96 ${darkMode ? 'bg-gray-800 border border-gray-700' : ''}`}>
                <div className="text-5xl mb-2">📊</div>
                <p className={`text-lg font-semibold ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  Results will appear here
                </p>
                <p className={`text-sm ${darkMode ? 'text-gray-500' : 'text-gray-400'} mt-2`}>
                  Fill out the form and click "Get Predictions"
                </p>
              </div>
            )}

            {!loading && !error && !predictions && healthStatus !== 'healthy' && (
              <div className={`card flex flex-col items-center justify-center h-96 ${darkMode ? 'bg-gray-800 border border-gray-700' : ''}`}>
                <div className="text-5xl mb-2">⚠️</div>
                <p className={`text-lg font-semibold ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  Backend not available
                </p>
                <p className={`text-sm ${darkMode ? 'text-gray-500' : 'text-gray-400'} mt-2`}>
                  Please ensure the backend server is running
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Info Section */}
        <div className={`mt-12 p-6 rounded-lg ${darkMode ? 'bg-gray-800 border border-gray-700' : 'bg-blue-50 border border-blue-200'}`}>
          <h3 className="text-lg font-bold mb-3">ℹ️ About the System</h3>
          <p className={`${darkMode ? 'text-gray-300' : 'text-gray-700'} text-sm leading-relaxed`}>
            This prediction system uses a single XGBoost multi-output machine learning model trained on antibiotic resistance patterns. The model is optimized with per-antibiotic thresholds to predict resistance for 15 different antibiotics with high accuracy. Results are shown with individual predictions and confidence scores that reflect the model's certainty.
          </p>
          <p className={`mt-3 ${darkMode ? 'text-gray-400' : 'text-gray-600'} text-sm italic`}>
            ⚠️ Predictions are influenced by historical antibiotic resistance patterns. Clinical decisions should always be made in consultation with healthcare professionals.
          </p>
        </div>
      </main>

      {/* Footer */}
      <footer className={`${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-t mt-12 py-6 text-center text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
        <p>Antibiotic Resistance Prediction System • Version 1.0.0 • Production Ready</p>
      </footer>
    </div>
  )
}

export default App
