import { useState } from 'react'

function ResultsTable({ data, darkMode }) {
  const [showExperimental, setShowExperimental] = useState(false)
  const [expandedCard, setExpandedCard] = useState(null)

  // Separating production and experimental models
  const productionModels = data.filter(row => row.model_tier?.toLowerCase() === 'production')
  const experimentalModels = data.filter(row => row.model_tier?.toLowerCase() === 'experimental')

  const getConfidenceBadgeClass = (confidence) => {
    switch (confidence?.toLowerCase()) {
      case 'high':
        return darkMode 
          ? 'bg-emerald-950/40 text-emerald-300 border-emerald-800/40' 
          : 'bg-emerald-100/60 text-emerald-800 border-emerald-200/50'
      case 'medium':
        return darkMode 
          ? 'bg-yellow-950/40 text-yellow-300 border-yellow-800/40' 
          : 'bg-yellow-100/60 text-yellow-800 border-yellow-200/50'
      default: // low
        return darkMode 
          ? 'bg-red-950/40 text-red-305 border-red-800/40' 
          : 'bg-red-100/60 text-red-800 border-red-200/50'
    }
  }

  const getTierBadgeClass = (tier) => {
    if (tier?.toLowerCase() === 'production') {
      return darkMode 
        ? 'bg-blue-950/40 text-blue-300 border-blue-900/40' 
        : 'bg-blue-100/60 text-blue-800 border-blue-200/50'
    }
    return darkMode 
      ? 'bg-purple-950/40 text-purple-300 border-purple-900/40' 
      : 'bg-purple-100/60 text-purple-800 border-purple-200/50'
  }

  const toggleExplanation = (antibioticName) => {
    setExpandedCard(expandedCard === antibioticName ? null : antibioticName)
  }

  const renderCard = (row) => {
    const isExpanded = expandedCard === row.antibiotic
    const isResistant = row.prediction === 'Resistant'
    const formattedProb = Math.round(row.probability * 100)
    const isExperimental = row.model_tier?.toLowerCase() === 'experimental'

    return (
      <div
        key={row.antibiotic}
        className={`flex flex-col p-5 transition-all duration-300 relative group overflow-hidden ${
          darkMode ? 'uiverse-glass-card-dark' : 'uiverse-glass-card-light'
        }`}
      >
        {/* Subtle hover glow accent lines */}
        <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-blue-500/0 to-transparent group-hover:via-blue-500/30 transition-all duration-500" />

        {/* Header Block */}
        <div className="flex justify-between items-start mb-3">
          <div>
            <h3 className="text-base font-extrabold tracking-tight text-slate-900 dark:text-white">
              {row.antibiotic}
            </h3>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 font-bold block mt-0.5 uppercase tracking-wide">
              Threshold: {row.decision_threshold}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className={`px-2 py-0.5 rounded-md text-[9px] font-extrabold uppercase tracking-wide border ${getTierBadgeClass(row.model_tier)}`}>
              {row.model_tier}
            </span>
            <span className={`px-2 py-0.5 rounded-md text-[9px] font-extrabold uppercase tracking-wide border ${getConfidenceBadgeClass(row.confidence)}`}>
              {row.confidence} Confidence
            </span>
          </div>
        </div>

        {/* Status, Probability & Progress Bar */}
        <div className="grid grid-cols-2 gap-4 items-center my-4">
          <div>
            <p className={`text-[9px] uppercase font-bold tracking-wider ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>Clinical Status</p>
            <p className={`text-xl font-black mt-1 flex items-center gap-1.5 ${isResistant ? 'text-red-500 dark:text-red-400' : 'text-emerald-500 dark:text-emerald-400'}`}>
              <span className="text-sm">{isResistant ? '🔴' : '🟢'}</span> {row.prediction}
            </p>
          </div>
          <div className="text-right">
            <p className={`text-[9px] uppercase font-bold tracking-wider ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>Resistance Probability</p>
            <p className="text-2xl font-black mt-0.5 tracking-tight text-slate-800 dark:text-slate-100">{formattedProb}%</p>
          </div>
        </div>

        {/* Custom Slate Progress Bar */}
        <div className={`w-full h-1.5 rounded-full mb-5 overflow-hidden ${darkMode ? 'bg-slate-800' : 'bg-slate-100'}`}>
          <div
            className={`h-full rounded-full transition-all duration-500 ease-out ${isResistant ? 'bg-red-500 dark:bg-red-400' : 'bg-emerald-500 dark:bg-emerald-400'}`}
            style={{ width: `${formattedProb}%` }}
          />
        </div>

        {/* Expandable Explanation Panel Trigger */}
        <button
          onClick={() => toggleExplanation(row.antibiotic)}
          className={`w-full py-2 px-3 text-xxs font-extrabold rounded-xl transition-all duration-200 flex items-center justify-center gap-1.5 border active:scale-[0.98] ${
            darkMode
              ? 'bg-slate-900/50 hover:bg-slate-850 text-slate-300 border-slate-850 hover:border-slate-800'
              : 'bg-slate-50 hover:bg-slate-100 text-slate-650 border-slate-150 hover:border-slate-200'
          }`}
        >
          🧬 {isExpanded ? 'Collapse Insight Panel' : 'Expand Clinical Insights'}
        </button>

        {/* Explainable AI Insight Panel Drawer */}
        {isExpanded && (
          <div className={`mt-4 p-4 rounded-xl border text-[11px] leading-relaxed transition-all duration-300 fade-in ${
            darkMode 
              ? 'bg-slate-950/60 border-slate-850 text-slate-300 shadow-inner' 
              : 'bg-blue-50/20 border-blue-100/50 text-slate-700 shadow-inner'
          }`}>
            <h4 className="font-extrabold text-xs mb-3 flex items-center gap-1.5 text-slate-900 dark:text-white">
              🩺 Mathematical Contribution Factors (SHAP)
            </h4>

            {row.explanation ? (
              <div className="space-y-3">
                {/* Positive (Increases Resistance Risk) */}
                {row.explanation.top_positive_factors && row.explanation.top_positive_factors.length > 0 ? (
                  <div>
                    <p className="font-extrabold text-red-500 dark:text-red-400 text-[9px] uppercase tracking-wider mb-1">
                      Resistance Driver Factors (Promotes Risk)
                    </p>
                    <ul className="space-y-1">
                      {row.explanation.top_positive_factors.map((feat, fidx) => (
                        <li key={fidx} className="flex items-center gap-2">
                          <span className="text-red-500 font-extrabold text-xs leading-none">+</span>
                          <span className="font-medium text-slate-755 dark:text-slate-300">{feat}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null}

                {/* Negative (Protects / Decreases Risk) */}
                {row.explanation.top_negative_factors && row.explanation.top_negative_factors.length > 0 ? (
                  <div className="pt-1 border-t border-slate-800/40">
                    <p className="font-extrabold text-emerald-500 dark:text-emerald-400 text-[9px] uppercase tracking-wider mb-1">
                      Risk Protection Factors (Decreases Risk)
                    </p>
                    <ul className="space-y-1">
                      {row.explanation.top_negative_factors.map((feat, fidx) => (
                        <li key={fidx} className="flex items-center gap-2">
                          <span className="text-emerald-500 font-extrabold text-xs leading-none">-</span>
                          <span className="font-medium text-slate-755 dark:text-slate-300">{feat}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null}

                {(!row.explanation.top_positive_factors || row.explanation.top_positive_factors.length === 0) &&
                 (!row.explanation.top_negative_factors || row.explanation.top_negative_factors.length === 0) && (
                   <p className="text-slate-500 italic py-1 text-xxs">No clinical features had meaningful attribution impact on this model.</p>
                 )}
              </div>
            ) : (
              <div className="text-center py-2 italic text-slate-500 text-xxs">
                ℹ️ SHAP calculations were bypassed. Check "Enable Explainable AI" in the form to run mathematical attributions.
              </div>
            )}
          </div>
        )}

        {/* Experimental Clinical Advisory */}
        {isExperimental && (
          <div className={`mt-4 pt-3 border-t text-center ${darkMode ? 'border-slate-805/50' : 'border-slate-100'}`}>
            <p className="text-[9px] font-extrabold text-red-500/80 dark:text-red-400/80 uppercase tracking-wider flex items-center justify-center gap-1.5">
              ⚠️ Investigative Research Model — Confirm via lab cultures
            </p>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 🛡️ Primary Production Grid */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold tracking-tight text-slate-900 dark:text-white flex items-center gap-2">
            🛡️ Primary Clinical Predictors <span className="text-xxs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-500 font-extrabold uppercase">Beta-Lactams</span>
          </h2>
          <span className={`text-[10px] font-bold ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
            6 Models Active
          </span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {productionModels.map(renderCard)}
        </div>
      </div>

      {/* 🔬 Collapsible Secondary/Experimental Accordion */}
      {experimentalModels.length > 0 && (
        <div className={`overflow-hidden transition-all duration-300 ${
          darkMode ? 'uiverse-glass-card-dark' : 'uiverse-glass-card-light'
        }`}>
          {/* Header Toggle */}
          <button
            onClick={() => setShowExperimental(!showExperimental)}
            className={`w-full px-5 py-4 flex justify-between items-center transition-colors ${
              darkMode ? 'hover:bg-slate-900/40' : 'hover:bg-slate-100/30'
            }`}
          >
            <div className="text-left">
              <p className="text-sm font-bold tracking-tight text-slate-900 dark:text-white flex items-center gap-2">
                🔬 Experimental Research Predictors
                <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-purple-500/10 text-purple-500 font-extrabold uppercase">Secondary</span>
              </p>
              <p className={`text-[10px] mt-0.5 font-bold ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
                {experimentalModels.length} models with lower clinical discrimination or high class imbalance
              </p>
            </div>
            <span className="text-sm font-bold text-slate-400 group-hover:text-white transition-all">
              {showExperimental ? '🔼 Collapse' : '🔽 Expand Models'}
            </span>
          </button>

          {/* Collapsible Content */}
          {showExperimental && (
            <div className={`p-5 border-t ${darkMode ? 'border-slate-805/50' : 'border-slate-100'} fade-in`}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {experimentalModels.map(renderCard)}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ResultsTable
