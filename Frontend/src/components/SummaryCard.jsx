function SummaryCard({ summary, darkMode }) {
  return (
    <div className={`card fade-in ${darkMode ? 'bg-gray-800 border border-gray-700' : ''}`}>
      <h2 className="text-2xl font-bold mb-4">📊 Analysis Summary</h2>

      <div className="grid grid-cols-2 gap-3 mb-6">
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-100'} text-center`}>
          <p className="text-3xl font-bold text-red-600">{summary.resistant_count}</p>
          <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-600'} mt-1`}>Resistant</p>
          <p className="text-sm font-semibold text-red-600">{summary.resistant_percentage}%</p>
        </div>

        <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-100'} text-center`}>
          <p className="text-3xl font-bold text-green-600">{summary.susceptible_count}</p>
          <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-600'} mt-1`}>Susceptible</p>
          <p className="text-sm font-semibold text-green-600">{summary.susceptible_percentage}%</p>
        </div>
      </div>

      {summary.recommended_antibiotics && summary.recommended_antibiotics.length > 0 && (
        <div className={`p-3 rounded-lg ${darkMode ? 'bg-green-900 border border-green-700' : 'bg-green-50 border border-green-200'}`}>
          <p className={`text-xs font-semibold uppercase ${darkMode ? 'text-green-300' : 'text-green-700'}`}>
            💊 Recommended Antibiotics
          </p>
          <div className="flex flex-wrap gap-2 mt-2">
            {summary.recommended_antibiotics.map((ab, idx) => (
              <span
                key={idx}
                className={`px-2 py-1 rounded text-xs font-semibold ${
                  darkMode
                    ? 'bg-green-700 text-green-100'
                    : 'bg-green-200 text-green-800'
                }`}
              >
                {ab}
              </span>
            ))}
          </div>
        </div>
      )}

      {summary.high_confidence_resistant && summary.high_confidence_resistant.length > 0 && (
        <div className={`p-3 rounded-lg mt-3 ${darkMode ? 'bg-red-900 border border-red-700' : 'bg-red-50 border border-red-200'}`}>
          <p className={`text-xs font-semibold uppercase ${darkMode ? 'text-red-300' : 'text-red-700'}`}>
            ⚠️ High Resistance Risk
          </p>
          <div className="flex flex-wrap gap-2 mt-2">
            {summary.high_confidence_resistant.slice(0, 5).map((ab, idx) => (
              <span
                key={idx}
                className={`px-2 py-1 rounded text-xs font-semibold ${
                  darkMode
                    ? 'bg-red-700 text-red-100'
                    : 'bg-red-200 text-red-800'
                }`}
              >
                {ab}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default SummaryCard
