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

  const [errors, setErrors] = useState({})

  const validateForm = () => {
    const newErrors = {}

    if (!formData.Age || isNaN(formData.Age) || formData.Age <= 0) {
      newErrors.Age = 'Age must be a positive number'
    }

    if (!formData.Gender) {
      newErrors.Gender = 'Gender is required'
    }

    if (!formData.Souches || formData.Souches.trim() === '') {
      newErrors.Souches = 'Bacterial strain is required'
    }

    if (!formData.Diabetes) {
      newErrors.Diabetes = 'Diabetes status is required'
    }

    if (!formData.Hypertension) {
      newErrors.Hypertension = 'Hypertension status is required'
    }

    if (!formData.Hospital_before) {
      newErrors.Hospital_before = 'Hospital history is required'
    }

    if (!formData.Infection_Freq || isNaN(formData.Infection_Freq) || formData.Infection_Freq < 0) {
      newErrors.Infection_Freq = 'Infection frequency must be a non-negative number'
    }

    return newErrors
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    // Clear error for this field when user starts typing
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

    // Convert to proper types
    const submitData = {
      ...formData,
      Age: parseFloat(formData.Age),
      Infection_Freq: parseFloat(formData.Infection_Freq)
    }

    onSubmit(submitData)
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

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Age */}
      <div>
        <label className="block text-sm font-semibold mb-1">Age (years) *</label>
        <input
          type="number"
          name="Age"
          value={formData.Age}
          onChange={handleChange}
          placeholder="e.g., 55"
          min="0"
          max="150"
          step="1"
          className={`input-field ${darkMode ? 'bg-gray-700 border-gray-600 text-white' : ''} ${errors.Age ? 'border-red-500' : ''}`}
        />
        {errors.Age && <p className="text-red-500 text-xs mt-1">{errors.Age}</p>}
      </div>

      {/* Gender */}
      <div>
        <label className="block text-sm font-semibold mb-1">Gender *</label>
        <select
          name="Gender"
          value={formData.Gender}
          onChange={handleChange}
          className={`select-field ${darkMode ? 'bg-gray-700 border-gray-600 text-white' : ''} ${errors.Gender ? 'border-red-500' : ''}`}
        >
          <option value="">Select Gender</option>
          <option value="M">Male</option>
          <option value="F">Female</option>
        </select>
        {errors.Gender && <p className="text-red-500 text-xs mt-1">{errors.Gender}</p>}
      </div>

      {/* Souches (Bacterial strain) */}
      <div>
        <label className="block text-sm font-semibold mb-1">Bacterial Strain *</label>
        <input
          type="text"
          name="Souches"
          value={formData.Souches}
          onChange={handleChange}
          placeholder="e.g., Escherichia coli"
          className={`input-field ${darkMode ? 'bg-gray-700 border-gray-600 text-white' : ''} ${errors.Souches ? 'border-red-500' : ''}`}
        />
        {errors.Souches && <p className="text-red-500 text-xs mt-1">{errors.Souches}</p>}
      </div>

      {/* Diabetes */}
      <div>
        <label className="block text-sm font-semibold mb-1">Diabetes *</label>
        <select
          name="Diabetes"
          value={formData.Diabetes}
          onChange={handleChange}
          className={`select-field ${darkMode ? 'bg-gray-700 border-gray-600 text-white' : ''} ${errors.Diabetes ? 'border-red-500' : ''}`}
        >
          <option value="">Select Status</option>
          <option value="Yes">Yes</option>
          <option value="No">No</option>
        </select>
        {errors.Diabetes && <p className="text-red-500 text-xs mt-1">{errors.Diabetes}</p>}
      </div>

      {/* Hypertension */}
      <div>
        <label className="block text-sm font-semibold mb-1">Hypertension *</label>
        <select
          name="Hypertension"
          value={formData.Hypertension}
          onChange={handleChange}
          className={`select-field ${darkMode ? 'bg-gray-700 border-gray-600 text-white' : ''} ${errors.Hypertension ? 'border-red-500' : ''}`}
        >
          <option value="">Select Status</option>
          <option value="Yes">Yes</option>
          <option value="No">No</option>
        </select>
        {errors.Hypertension && <p className="text-red-500 text-xs mt-1">{errors.Hypertension}</p>}
      </div>

      {/* Hospital Before */}
      <div>
        <label className="block text-sm font-semibold mb-1">Previous Hospitalization *</label>
        <select
          name="Hospital_before"
          value={formData.Hospital_before}
          onChange={handleChange}
          className={`select-field ${darkMode ? 'bg-gray-700 border-gray-600 text-white' : ''} ${errors.Hospital_before ? 'border-red-500' : ''}`}
        >
          <option value="">Select Status</option>
          <option value="Yes">Yes</option>
          <option value="No">No</option>
        </select>
        {errors.Hospital_before && <p className="text-red-500 text-xs mt-1">{errors.Hospital_before}</p>}
      </div>

      {/* Infection Frequency */}
      <div>
        <label className="block text-sm font-semibold mb-1">Infection Frequency *</label>
        <input
          type="number"
          name="Infection_Freq"
          value={formData.Infection_Freq}
          onChange={handleChange}
          placeholder="e.g., 2"
          min="0"
          step="0.1"
          className={`input-field ${darkMode ? 'bg-gray-700 border-gray-600 text-white' : ''} ${errors.Infection_Freq ? 'border-red-500' : ''}`}
        />
        {errors.Infection_Freq && <p className="text-red-500 text-xs mt-1">{errors.Infection_Freq}</p>}
      </div>

      {/* Buttons */}
      <div className="flex gap-3 pt-4">
        <button
          type="submit"
          disabled={isLoading || !apiHealthy}
          className={`flex-1 btn-primary ${isLoading || !apiHealthy ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-700'}`}
          title={!apiHealthy ? 'Backend is not available' : ''}
        >
          {isLoading ? '⏳ Analyzing...' : '🔍 Get Predictions'}
        </button>
        <button
          type="button"
          onClick={handleSampleData}
          disabled={isLoading}
          className="btn-secondary"
          title="Fill with sample data"
        >
          📋 Sample
        </button>
        <button
          type="button"
          onClick={handleReset}
          disabled={isLoading}
          className="btn-secondary"
          title="Clear form"
        >
          🔄 Reset
        </button>
      </div>

      <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'} mt-2`}>
        * All fields are required
      </p>
    </form>
  )
}

export default PredictionForm
