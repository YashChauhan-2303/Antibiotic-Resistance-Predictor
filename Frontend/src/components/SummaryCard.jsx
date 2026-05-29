import React from 'react'

function SummaryCard({ summary, darkMode }) {
  return (
    <div className={`p-6 overflow-hidden relative transition-all duration-300 ${
      darkMode ? 'uiverse-glass-card-dark' : 'uiverse-glass-card-light'
    }`}>
      {/* Decorative gradient blur background */}
      <div className="absolute top-0 right-0 w-48 h-48 bg-blue-500/5 dark:bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
      
      <div className="flex items-center gap-2 mb-6">
        <span className="text-xl">📊</span>
        <h2 className="text-lg font-bold tracking-tight">Clinical Analysis Summary</h2>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        {/* Resistant Metric Card */}
        <div className={`p-4 rounded-xl border transition-all backdrop-blur-sm ${
          darkMode 
            ? 'bg-slate-900/50 border-slate-800/80 hover:border-red-900/40' 
            : 'bg-slate-50/50 border-slate-100/80 hover:border-red-100'
        }`}>
          <div className="flex justify-between items-start">
            <span className={`text-xxs uppercase font-extrabold tracking-wider ${darkMode ? 'text-slate-450' : 'text-slate-500'}`}>
              Resistant Strains
            </span>
            <span className="px-1.5 py-0.5 rounded text-xxs font-extrabold bg-red-500/10 text-red-500">
              {summary.resistant_percentage}%
            </span>
          </div>
          <p className="text-3xl font-black mt-2 tracking-tight text-red-505 dark:text-red-400">
            {summary.resistant_count}
          </p>
          <p className={`text-xxs mt-1 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
            Antibiotics with active resistance predicted
          </p>
        </div>

        {/* Susceptible Metric Card */}
        <div className={`p-4 rounded-xl border transition-all backdrop-blur-sm ${
          darkMode 
            ? 'bg-slate-900/50 border-slate-800/80 hover:border-emerald-900/40' 
            : 'bg-slate-50/50 border-slate-100/80 hover:border-emerald-100'
        }`}>
          <div className="flex justify-between items-start">
            <span className={`text-xxs uppercase font-extrabold tracking-wider ${darkMode ? 'text-slate-450' : 'text-slate-500'}`}>
              Susceptible Strains
            </span>
            <span className="px-1.5 py-0.5 rounded text-xxs font-extrabold bg-emerald-500/10 text-emerald-500">
              {summary.susceptible_percentage}%
            </span>
          </div>
          <p className="text-3xl font-black mt-2 tracking-tight text-emerald-505 dark:text-emerald-400">
            {summary.susceptible_count}
          </p>
          <p className={`text-xxs mt-1 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
            Antibiotics with active susceptibility predicted
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {/* Recommended Panel */}
        {summary.recommended_antibiotics && summary.recommended_antibiotics.length > 0 && (
          <div className={`p-4 rounded-xl border transition-all backdrop-blur-sm ${
            darkMode 
              ? 'bg-emerald-950/20 border-emerald-900/40' 
              : 'bg-emerald-50/40 border-emerald-100/80'
          }`}>
            <p className="text-xxs font-extrabold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
              <span>💊</span> High-Confidence Treatments (Susceptible)
            </p>
            <div className="flex flex-wrap gap-1.5 mt-3">
              {summary.recommended_antibiotics.map((ab, idx) => (
                <span
                  key={idx}
                  className={`px-2.5 py-1 rounded-md text-xxs font-bold transition-all hover:scale-105 duration-200 border ${
                    darkMode
                      ? 'bg-emerald-900/40 text-emerald-300 border-emerald-800/40'
                      : 'bg-emerald-100/80 text-emerald-800 border-emerald-200/50'
                  }`}
                >
                  {ab}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* High Resistance Risk Panel */}
        {summary.high_confidence_resistant && summary.high_confidence_resistant.length > 0 && (
          <div className={`p-4 rounded-xl border transition-all backdrop-blur-sm ${
            darkMode 
              ? 'bg-red-950/20 border-red-900/40' 
              : 'bg-red-50/40 border-red-100/80'
          }`}>
            <p className="text-xxs font-extrabold uppercase tracking-wider text-red-650 dark:text-red-400 flex items-center gap-1.5">
              <span>⚠️</span> Avoid (High-Confidence Resistance)
            </p>
            <div className="flex flex-wrap gap-1.5 mt-3">
              {summary.high_confidence_resistant.slice(0, 5).map((ab, idx) => (
                <span
                  key={idx}
                  className={`px-2.5 py-1 rounded-md text-xxs font-bold transition-all hover:scale-105 duration-200 border ${
                    darkMode
                      ? 'bg-red-900/40 text-red-300 border-red-800/40'
                      : 'bg-red-100/80 text-red-850 border-red-200/50'
                  }`}
                >
                  {ab}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default SummaryCard
