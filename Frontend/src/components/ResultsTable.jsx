import { useMemo } from 'react'

function ResultsTable({ data, darkMode }) {
  const models = useMemo(() => [
    'Logistic Regression',
    'Random Forest',
    'SVM',
    'XGBoost',
    'Bagging',
    'AdaBoost'
  ], [])

  const getAbbreviation = (model) => {
    const abbr = {
      'Logistic Regression': 'LR',
      'Random Forest': 'RF',
      'SVM': 'SVM',
      'XGBoost': 'XGB',
      'Bagging': 'Bag',
      'AdaBoost': 'Ada'
    }
    return abbr[model] || model
  }

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

  const getConsensusClass = (value) => {
    if (value === 'Resistant') {
      return 'bg-red-200 text-red-900 font-bold'
    } else if (value === 'Susceptible') {
      return 'bg-green-200 text-green-900 font-bold'
    }
    return 'bg-gray-200'
  }

  const getDarkConsensusClass = (value) => {
    if (value === 'Resistant') {
      return 'bg-red-800 text-red-100 font-bold'
    } else if (value === 'Susceptible') {
      return 'bg-green-800 text-green-100 font-bold'
    }
    return 'bg-gray-600'
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
              <th className={`px-2 py-2 text-left font-bold text-sm ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
                Antibiotic
              </th>
              {models.map(model => (
                <th
                  key={model}
                  className={`px-1 py-2 text-center font-bold text-xs ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}
                  title={model}
                >
                  {getAbbreviation(model)}
                </th>
              ))}
              <th className={`px-1 py-2 text-center font-bold text-xs ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
                Result
              </th>
              <th className={`px-1 py-2 text-center font-bold text-xs ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
                Conf%
              </th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr
                key={idx}
                className={`border-b ${darkMode ? 'border-gray-700 hover:bg-gray-750' : 'border-gray-200 hover:bg-gray-50'} transition-colors`}
              >
                <td className={`px-2 py-2 font-semibold text-xs ${darkMode ? 'text-gray-100' : 'text-gray-800'} whitespace-nowrap`}>
                  {row.antibiotic}
                </td>
                {models.map(model => (
                  <td
                    key={`${idx}-${model}`}
                    className={`px-1 py-2 text-center ${
                      darkMode ? getDarkCellClass(row[model]) : getCellClass(row[model])
                    }`}
                  >
                    {row[model] === 'Resistant' ? '🔴' : '🟢'}
                  </td>
                ))}
                <td
                  className={`px-1 py-2 text-center text-xs font-semibold ${
                    darkMode ? getDarkConsensusClass(row.consensus) : getConsensusClass(row.consensus)
                  }`}
                >
                  {row.consensus === 'Resistant' ? '🔴' : '🟢'}
                </td>
                <td className={`px-1 py-2 text-center text-xs font-semibold ${
                  darkMode ? getDarkConfidenceColor(row.confidence) : getConfidenceColor(row.confidence)
                }`}>
                  {Math.round(row.confidence)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 gap-3">
        <div className={`p-3 rounded-lg text-center ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`}>
          <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Votes</p>
          <p className={`text-sm font-semibold ${darkMode ? 'text-gray-300' : 'text-gray-800'}`}>
            Models Analyzed: {data.length * models.length}
          </p>
        </div>
        <div className={`p-3 rounded-lg text-center ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`}>
          <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Antibiotics</p>
          <p className={`text-sm font-semibold ${darkMode ? 'text-gray-300' : 'text-gray-800'}`}>
            Analyzed: {data.length}
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
          Confidence shows agreement level across all 6 models (80%+ = high confidence)
        </p>
      </div>
    </div>
  )
}

export default ResultsTable
