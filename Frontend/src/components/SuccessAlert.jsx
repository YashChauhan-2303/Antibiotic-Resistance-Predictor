function SuccessAlert({ message }) {
  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4 animate-fadeIn">
      <div className="flex items-start gap-3">
        <div className="text-2xl">✓</div>
        <div>
          <h3 className="font-bold text-green-800 mb-1">Success</h3>
          <p className="text-green-700 text-sm">{message}</p>
        </div>
      </div>
    </div>
  )
}

export default SuccessAlert
