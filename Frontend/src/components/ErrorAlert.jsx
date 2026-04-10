function ErrorAlert({ message }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <div className="flex items-start gap-3">
        <div className="text-2xl">❌</div>
        <div>
          <h3 className="font-bold text-red-800 mb-1">Error</h3>
          <p className="text-red-700 text-sm">{message}</p>
        </div>
      </div>
    </div>
  )
}

export default ErrorAlert
