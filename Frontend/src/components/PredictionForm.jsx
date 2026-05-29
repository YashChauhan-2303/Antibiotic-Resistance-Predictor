import { useState } from 'react'

const SAMPLE_DATA = {
  Age: 55,
  Gender: 'F',
  Souches: 'Escherichia coli',
  Diabetes: 'Yes',
  Hypertension: 'No',
  Hospital_before: 'Yes',
  Infection_Freq: 2
}

function PredictionForm({ onSubmit, isLoading, darkMode, apiHealthy = true }) {
  const [formData, setFormData] = useState({
    Age: '',
    Gender: '',
    Souches: '',
    Diabetes: '',
    Hypertension: '',
    Hospital_before: '',
    Infection_Freq: ''
  })
  const [explain, setExplain] = useState(false)
  const [errors, setErrors] = useState({})

  const validateForm = () => {
    const newErrors = {}

    if (!formData.Age || isNaN(formData.Age) || formData.Age <= 0) {
      newErrors.Age = 'Age must be positive'
    }

    if (!formData.Gender) {
      newErrors.Gender = 'Gender is required'
    }

    if (!formData.Souches || formData.Souches.trim() === '') {
      newErrors.Souches = 'Strain is required'
    }

    if (!formData.Diabetes) {
      newErrors.Diabetes = 'Diabetes is required'
    }

    if (!formData.Hypertension) {
      newErrors.Hypertension = 'Hypertension is required'
    }

    if (!formData.Hospital_before) {
      newErrors.Hospital_before = 'Required'
    }

    if (!formData.Infection_Freq || isNaN(formData.Infection_Freq) || formData.Infection_Freq < 0) {
      newErrors.Infection_Freq = 'Frequency must be non-negative'
    }

    return newErrors
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    const newErrors = validateForm()

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    setErrors({})

    const submitData = {
      ...formData,
      Age: parseFloat(formData.Age),
      Infection_Freq: parseFloat(formData.Infection_Freq)
    }

    onSubmit(submitData, explain)
  }

  const handleSampleData = () => {
    setFormData(SAMPLE_DATA)
    setErrors({})
  }

  const handleReset = () => {
    setFormData({
      Age: '',
      Gender: '',
      Souches: '',
      Diabetes: '',
      Hypertension: '',
      Hospital_before: '',
      Infection_Freq: ''
    })
    setErrors({})
  }

  const inputBaseClass = (errorState) => `
    w-full px-3 py-1.5 text-xs rounded-lg border transition-all duration-200 outline-none
    ${darkMode 
      ? `bg-slate-900/60 border-slate-800 text-white focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500` 
      : `bg-white border-slate-200 text-slate-900 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500`}
    ${errorState ? 'border-red-500 dark:border-red-500 focus:ring-red-500/20' : ''}
  `

  const labelClass = `block text-xxs font-extrabold tracking-wider uppercase mb-1 ${darkMode ? 'text-slate-450' : 'text-slate-500'}`

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* 2-Column Grid for Demographics */}
      <div className="grid grid-cols-2 gap-4">
        {/* Age */}
        <div>
          <label className={labelClass}>Age (Years) *</label>
          <input
            type="number"
            name="Age"
            value={formData.Age}
            onChange={handleChange}
            placeholder="e.g., 55"
            min="0"
            max="150"
            step="1"
            className={inputBaseClass(errors.Age)}
          />
          {errors.Age && <p className="text-red-500 text-xxs mt-0.5">{errors.Age}</p>}
        </div>

        {/* Gender */}
        <div>
          <label className={labelClass}>Gender *</label>
          <select
            name="Gender"
            value={formData.Gender}
            onChange={handleChange}
            className={inputBaseClass(errors.Gender)}
          >
            <option value="">Select</option>
            <option value="M">Male</option>
            <option value="F">Female</option>
          </select>
          {errors.Gender && <p className="text-red-500 text-xxs mt-0.5">{errors.Gender}</p>}
        </div>
      </div>

      {/* Bacterial Strain Info Pair */}
      <div className="grid grid-cols-2 gap-4">
        {/* Souches (Bacterial strain) */}
        <div>
          <label className={labelClass}>Bacterial Strain *</label>
          <input
            type="text"
            name="Souches"
            value={formData.Souches}
            onChange={handleChange}
            placeholder="e.g., Escherichia coli"
            className={inputBaseClass(errors.Souches)}
          />
          {errors.Souches && <p className="text-red-500 text-xxs mt-0.5">{errors.Souches}</p>}
        </div>

        {/* Infection Frequency */}
        <div>
          <label className={labelClass}>Infection Freq *</label>
          <input
            type="number"
            name="Infection_Freq"
            value={formData.Infection_Freq}
            onChange={handleChange}
            placeholder="e.g., 2"
            min="0"
            step="0.1"
            className={inputBaseClass(errors.Infection_Freq)}
          />
          {errors.Infection_Freq && <p className="text-red-500 text-xxs mt-0.5">{errors.Infection_Freq}</p>}
        </div>
      </div>

      {/* Comorbidities Pair */}
      <div className="grid grid-cols-2 gap-4">
        {/* Diabetes */}
        <div>
          <label className={labelClass}>Diabetes *</label>
          <select
            name="Diabetes"
            value={formData.Diabetes}
            onChange={handleChange}
            className={inputBaseClass(errors.Diabetes)}
          >
            <option value="">Select</option>
            <option value="Yes">Yes</option>
            <option value="No">No</option>
          </select>
          {errors.Diabetes && <p className="text-red-500 text-xxs mt-0.5">{errors.Diabetes}</p>}
        </div>

        {/* Hypertension */}
        <div>
          <label className={labelClass}>Hypertension *</label>
          <select
            name="Hypertension"
            value={formData.Hypertension}
            onChange={handleChange}
            className={inputBaseClass(errors.Hypertension)}
          >
            <option value="">Select</option>
            <option value="Yes">Yes</option>
            <option value="No">No</option>
          </select>
          {errors.Hypertension && <p className="text-red-500 text-xxs mt-0.5">{errors.Hypertension}</p>}
        </div>
      </div>

      {/* Hospital Before (Hospitalization History) */}
      <div>
        <label className={labelClass}>Previous Hospitalization *</label>
        <select
          name="Hospital_before"
          value={formData.Hospital_before}
          onChange={handleChange}
          className={inputBaseClass(errors.Hospital_before)}
        >
          <option value="">Select Status</option>
          <option value="Yes">Yes</option>
          <option value="No">No</option>
        </select>
        {errors.Hospital_before && <p className="text-red-500 text-xxs mt-0.5">{errors.Hospital_before}</p>}
      </div>

      {/* Explainable AI Checkbox */}
      <div className={`flex items-start gap-3 p-3 rounded-xl border transition-all duration-200 ${
        darkMode 
          ? 'bg-slate-900/40 border-slate-800/80 hover:border-slate-700/50' 
          : 'bg-slate-50 border-slate-200/60 hover:border-slate-300'
      }`}>
        <input
          type="checkbox"
          id="explain"
          name="explain"
          checked={explain}
          onChange={(e) => setExplain(e.target.checked)}
          className="w-4 h-4 mt-0.5 rounded text-blue-650 focus:ring-blue-500/20 border-slate-300 dark:border-slate-700 cursor-pointer"
        />
        <label htmlFor="explain" className="flex-1 cursor-pointer select-none">
          <span className="block text-xs font-bold leading-tight">🧬 Enable Explainable AI (SHAP Analysis)</span>
          <span className={`block mt-0.5 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`} style={{ fontSize: '9px' }}>
            Computes mathematical feature contributions. Adds ~3 seconds to clinical analysis.
          </span>
        </label>
      </div>

      {/* Buttons */}
      <div className="flex gap-2 pt-2">
        <button
          type="submit"
          disabled={isLoading || !apiHealthy}
          className={`flex-[2] py-2 px-4 rounded-xl text-xs font-bold transition-all duration-200 shadow-md ${
            isLoading || !apiHealthy 
              ? 'opacity-40 cursor-not-allowed bg-blue-600/30 text-white/50' 
              : 'bg-blue-600 hover:bg-blue-500 active:scale-[0.98] text-white shadow-blue-500/10'
          }`}
          title={!apiHealthy ? 'Backend is not available' : ''}
        >
          {isLoading ? '⏳ Analyzing Patterns...' : '🔍 Run Clinical Prediction'}
        </button>
        <button
          type="button"
          onClick={handleSampleData}
          disabled={isLoading}
          className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold border transition-all active:scale-[0.98] ${
            darkMode 
              ? 'border-slate-800 bg-slate-900/50 hover:bg-slate-800 text-slate-350 hover:text-white' 
              : 'border-slate-250 bg-white hover:bg-slate-50 text-slate-650 hover:text-slate-900'
          }`}
          title="Fill with sample data"
        >
          📋 Sample
        </button>
        <button
          type="button"
          onClick={handleReset}
          disabled={isLoading}
          className={`py-2 px-3 rounded-xl text-xs border transition-all active:scale-[0.98] ${
            darkMode 
              ? 'border-slate-800 bg-slate-900/50 hover:bg-slate-800 text-slate-350 hover:text-white' 
              : 'border-slate-250 bg-white hover:bg-slate-50 text-slate-650 hover:text-slate-900'
          }`}
          title="Clear form"
        >
          🔄 Reset
        </button>
      </div>
    </form>
  )
}

export default PredictionForm
