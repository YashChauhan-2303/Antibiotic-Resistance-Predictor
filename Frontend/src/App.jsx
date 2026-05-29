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

  const handleSubmit = async (data, explainFlag = false) => {
    setLoading(true)
    setError(null)
    setPredictions(null)
    setSummary(null)
    setSuccess(null)
    setFormData(data)

    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/predict`, data, {
        params: { explain: explainFlag },
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 30000,
      })

      if (response.data && response.data.data) {
        setPredictions(response.data.data)
        setSummary(response.data.summary)
        setSuccess('Clinical predictions generated successfully.')
        setTimeout(() => setSuccess(null), 4000)
      }
    } catch (err) {
      let errorMessage = 'Failed to generate predictions. Please check input parameters.'

      if (err.response) {
        errorMessage = err.response.data?.error || err.response.data?.detail || errorMessage
      } else if (err.request) {
        errorMessage = `Could not reach prediction engine. Ensure API is launched on ${API_BASE_URL}`
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
    <div className={`min-h-screen relative transition-colors duration-500 selection:bg-blue-500/30 selection:text-white ${
      darkMode 
        ? 'bg-slate-950 text-slate-100' 
        : 'bg-slate-50 text-slate-900'
    }`}>
      {/* Background Grid Pattern Layer */}
      <div className={`fixed inset-0 z-0 pointer-events-none transition-all duration-500 ${
        darkMode ? 'clinical-grid-dark' : 'clinical-grid-light'
      }`} />

      {/* Decorative Blur Backdrops */}
      {darkMode && (
        <>
          <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-blue-500/5 rounded-full blur-[120px] pointer-events-none z-0" />
          <div className="absolute top-1/3 right-1/4 w-[400px] h-[400px] bg-purple-500/5 rounded-full blur-[100px] pointer-events-none z-0" />
        </>
      )}

      {/* Relative wrapper so layout elements stack correctly on top of background z-0 */}
      <div className="relative z-10 flex flex-col min-h-screen justify-between">

      {/* Header Block */}
      <header className={`border-b backdrop-blur-md sticky top-0 z-50 transition-all duration-300 ${
        darkMode 
          ? 'bg-slate-950/80 border-slate-900' 
          : 'bg-white/80 border-slate-200'
      }`}>
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <h1 className={`text-lg font-black tracking-tight ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              🔬 <span className="bg-gradient-to-r from-blue-500 via-indigo-400 to-purple-500 bg-clip-text text-transparent">Clinical Resistance Predictor</span>
            </h1>
            <span className={`px-2 py-0.5 rounded-full text-[9px] font-extrabold tracking-wide uppercase border flex items-center gap-1 ${
              healthStatus === 'healthy' 
                ? (darkMode ? 'bg-emerald-950/30 text-emerald-450 border-emerald-900/30' : 'bg-emerald-100 text-emerald-800 border-emerald-200')
                : (darkMode ? 'bg-red-950/30 text-red-450 border-red-900/30' : 'bg-red-100 text-red-800 border-red-200')
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${healthStatus === 'healthy' ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
              {healthStatus === 'healthy' ? 'Connected' : 'Offline'}
            </span>
          </div>
          
          <button
            onClick={toggleDarkMode}
            className={`p-2 rounded-xl border transition-all active:scale-95 ${
              darkMode 
                ? 'bg-slate-900 border-slate-800 text-yellow-450 hover:bg-slate-800' 
                : 'bg-slate-100 border-slate-250 text-slate-650 hover:bg-slate-200'
            }`}
            title="Toggle theme"
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      {/* Main Layout Container */}
      <main className="max-w-7xl mx-auto px-6 py-10">
        
        {/* Alerts Block */}
        {success && (
          <div className="mb-6 max-w-4xl">
            <SuccessAlert message={success} />
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Form Left Section (4/12 columns) */}
          <div className="lg:col-span-4 space-y-6">
            <div className={`p-6 transition-all duration-300 ${
              darkMode ? 'uiverse-glass-card-dark' : 'uiverse-glass-card-light'
            }`}>
              <div className="mb-6">
                <h2 className="text-base font-bold tracking-tight">Patient Diagnostics</h2>
                <p className={`text-[10px] mt-0.5 font-bold ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
                  Input clinical profiles to engineer features and calculate risk scores
                </p>
              </div>
              <PredictionForm
                onSubmit={handleSubmit}
                isLoading={loading}
                darkMode={darkMode}
                apiHealthy={healthStatus === 'healthy'}
              />
            </div>

            {/* Decoupled Info block to reduce card size */}
            <div className={`p-5 transition-all duration-300 ${
              darkMode ? 'uiverse-glass-card-dark text-slate-400' : 'uiverse-glass-card-light text-slate-600'
            }`}>
              <h3 className="text-xxs font-extrabold uppercase tracking-wider mb-2 text-slate-800 dark:text-white">
                🛡️ Operational System Reference
              </h3>
              <p className="text-[10px] leading-relaxed">
                Predictions are generated across 15 per-antibiotic specialized XGBoost pipelines optimized via custom validation F1 scores. Attributes attributions are calculated using SHAP TreeExplainers to detail local risk parameters.
              </p>
            </div>
          </div>

          {/* Results Right Section (8/12 columns) */}
          <div className="lg:col-span-8 space-y-6">
            
            {/* Loading shimmer card */}
            {loading && (
              <div className={`h-96 flex flex-col items-center justify-center p-8 transition-all duration-300 animate-pulse ${
                darkMode ? 'uiverse-glass-card-dark' : 'uiverse-glass-card-light'
              }`}>
                <LoadingSpinner />
                <p className="mt-4 text-sm font-bold tracking-tight">Performing advanced multi-model resistance screening...</p>
                <p className={`text-[10px] mt-1 font-bold ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
                  Engineering patient factors, calling classifier layers, and computing attributions
                </p>
              </div>
            )}

            {/* Error state */}
            {error && !loading && (
              <div className="fade-in">
                <ErrorAlert message={error} />
              </div>
            )}

            {/* Predictions & Summary Area */}
            {summary && !loading && (
              <div className="space-y-6 fade-in">
                {/* Hero Clinical Analysis Summary */}
                <SummaryCard
                  summary={summary}
                  darkMode={darkMode}
                />
                
                {/* Detailed Results Grid */}
                <div className={`p-6 transition-all duration-300 ${
                  darkMode ? 'uiverse-glass-card-dark' : 'uiverse-glass-card-light'
                }`}>
                  <div className="flex justify-between items-center mb-6">
                    <div>
                      <h2 className="text-base font-bold tracking-tight">Resistance Profile Screening</h2>
                      <p className={`text-[10px] mt-0.5 font-bold ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
                        Individual predictions mapped by customized decision thresholds
                      </p>
                    </div>
                    
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
                        link.download = `resistance_report_${Date.now()}.json`
                        link.click()
                        URL.revokeObjectURL(url)
                      }}
                      className={`py-1.5 px-3 rounded-xl text-xxs font-extrabold border transition-all active:scale-[0.98] ${
                        darkMode 
                          ? 'border-slate-800 bg-slate-900/50 hover:bg-slate-800 text-slate-300 hover:text-white' 
                          : 'border-slate-200 bg-white hover:bg-slate-50 text-slate-650 hover:text-slate-900'
                      }`}
                    >
                      📥 Export Report (JSON)
                    </button>
                  </div>
                  
                  <ResultsTable data={predictions} darkMode={darkMode} />
                </div>
              </div>
            )}

            {/* Neutral idle state */}
            {!loading && !error && !predictions && healthStatus === 'healthy' && (
              <div className={`h-[420px] flex flex-col items-center justify-center p-8 text-center transition-all duration-300 ${
                darkMode ? 'uiverse-glass-card-dark' : 'uiverse-glass-card-light'
              }`}>
                <div className="w-16 h-16 rounded-2xl bg-blue-500/10 flex items-center justify-center text-3xl mb-4 animate-bounce duration-1000">
                  📊
                </div>
                <h3 className="text-base font-extrabold tracking-tight">Diagnostics Pipeline Ready</h3>
                <p className={`text-xxs mt-1.5 max-w-sm mx-auto leading-relaxed ${darkMode ? 'text-slate-500' : 'text-slate-450'}`}>
                  Input a bacterial strain profile on the left and run screening diagnostics to generate treatment recommendations and explainability drivers.
                </p>
              </div>
            )}

            {/* Offline state */}
            {!loading && !error && !predictions && healthStatus !== 'healthy' && (
              <div className={`h-[420px] flex flex-col items-center justify-center p-8 text-center transition-all duration-300 ${
                darkMode ? 'uiverse-glass-card-dark' : 'uiverse-glass-card-light'
              }`}>
                <div className="w-16 h-16 rounded-2xl bg-red-500/10 flex items-center justify-center text-3xl mb-4">
                  ⚠️
                </div>
                <h3 className="text-base font-extrabold tracking-tight text-red-500 dark:text-red-400">Clinical Engine Disconnected</h3>
                <p className={`text-xxs mt-1.5 max-w-sm mx-auto leading-relaxed ${darkMode ? 'text-slate-500' : 'text-slate-450'}`}>
                  Could not reach prediction microservice. Ensure that the backend Python FastAPI server is active and running locally on <code className="px-1.5 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">port 8000</code>.
                </p>
              </div>
            )}

          </div>

        </div>

      </main>

      {/* Footer */}
      <footer className={`border-t py-8 text-center text-[10px] font-bold transition-all duration-300 ${
        darkMode 
          ? 'bg-slate-950/50 border-slate-900 text-slate-600' 
          : 'bg-slate-100/50 border-slate-200 text-slate-400'
      }`}>
        <p>Antibiotic Resistance Prediction System • Professional Clinical Decision Support Platform • Version 2.0.0</p>
      </footer>
      </div>
    </div>
  )
}

export default App
