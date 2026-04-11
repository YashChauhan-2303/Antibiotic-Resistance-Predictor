import { useMemo } from 'react'

function ResultsTable({ data, darkMode }) {
  const getCellClass = (value) => {
    if (value === 'Resistant') {
      return 'bg-red-100 text-red-900 font-semibold'
    } else if (value === 'Susceptible') {
      return 'bg-green-100 text-green-900 font-semibold'
    }
    return ''
  }

  const getDarkCellClass = (value) => {
    if (value === 'Resistant') {
      return 'bg-red-900 text-red-100 font-semibold'
    } else if (value === 'Susceptible') {
      return 'bg-green-900 text-green-100 font-semibold'
    }
    return 'bg-gray-700 text-gray-300'
  }

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'text-green-600'
    if (confidence >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getDarkConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'text-green-400'
    if (confidence >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  return (
    <div className="space-y-4">
      {/* Table */}
      <div className={`rounded-lg border ${darkMode ? 'border-gray-700' : 'border-gray-200'} overflow-x-visible`}>
        <table className="w-full text-xs">
          <thead>
            <tr className={`${darkMode ? 'bg-gray-700' : 'bg-gray-200'} border-b ${darkMode ? 'border-gray-600' : 'border-gray-300'}`}>
              <th className={`px-4 py-3 text-left font-bold text-sm ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
                Antibiotic
              </th>
              <th className={`px-4 py-3 text-center font-bold text-sm ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
                Prediction
              </th>
              <th className={`px-4 py-3 text-center font-bold text-sm ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
                Confidence %
              </th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr
                key={idx}
                className={`border-b ${darkMode ? 'border-gray-700 hover:bg-gray-750' : 'border-gray-200 hover:bg-gray-50'} transition-colors`}
              >
                <td className={`px-4 py-3 font-semibold text-sm ${darkMode ? 'text-gray-100' : 'text-gray-800'} whitespace-nowrap`}>
                  {row.antibiotic}
                </td>
                <td className={`px-4 py-3 text-center ${darkMode ? getDarkCellClass(row.prediction) : getCellClass(row.prediction)}`}>
                  <span className="inline-flex items-center gap-2">
                    {row.prediction === 'Resistant' ? '🔴' : '🟢'}
                    {row.prediction}
                  </span>
                </td>
                <td className={`px-4 py-3 text-center text-sm font-semibold ${
                  darkMode ? getDarkConfidenceColor(row.confidence) : getConfidenceColor(row.confidence)
                }`}>
                  {Math.round(row.confidence)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 gap-3">
        <div className={`p-3 rounded-lg text-center ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`}>
          <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Total</p>
          <p className={`text-sm font-semibold ${darkMode ? 'text-gray-300' : 'text-gray-800'}`}>
            Antibiotics: {data.length}
          </p>
        </div>
        <div className={`p-3 rounded-lg text-center ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`}>
          <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Model</p>
          <p className={`text-sm font-semibold ${darkMode ? 'text-gray-300' : 'text-gray-800'}`}>
            XGBoost
          </p>
        </div>
      </div>

      {/* Legend */}
      <div className={`space-y-2 text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
        <p className="font-semibold">Legend:</p>
        <div className="flex flex-wrap gap-4">
          <div className="flex items-center gap-2">
            <span className="text-lg">🔴</span>
            <span>Resistant</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-lg">🟢</span>
            <span>Susceptible</span>
          </div>
        </div>
        <p className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-500'} mt-2`}>
          Confidence score indicates probability of the prediction
        </p>
      </div>
    </div>
  )
}

export default ResultsTable
