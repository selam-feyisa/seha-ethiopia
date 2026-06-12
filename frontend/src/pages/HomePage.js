function HomePage() {
  return (
    <div className="max-w-3xl mx-auto p-8 text-center">
      <h1 className="text-4xl font-bold text-green-700 mb-3">
        Welcome to SEHA 🏥
      </h1>
      <p className="text-gray-500 text-lg mb-8">
        AI Healthcare Assistant for Ethiopia — ሰሃ
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-left">
        <div className="border rounded-xl p-5 bg-white shadow-sm hover:shadow-md transition">
          <div className="text-3xl mb-2">🩺</div>
          <h2 className="font-bold text-gray-800 mb-1">Symptom Checker</h2>
          <p className="text-sm text-gray-500">Select your symptoms and get an AI-powered health assessment with triage level.</p>
        </div>
        <div className="border rounded-xl p-5 bg-white shadow-sm hover:shadow-md transition">
          <div className="text-3xl mb-2">📄</div>
          <h2 className="font-bold text-gray-800 mb-1">Document Reader</h2>
          <p className="text-sm text-gray-500">Upload medical documents and get an instant AI summary of key findings.</p>
        </div>
        <div className="border rounded-xl p-5 bg-white shadow-sm hover:shadow-md transition">
          <div className="text-3xl mb-2">💊</div>
          <h2 className="font-bold text-gray-800 mb-1">Prescription Scanner</h2>
          <p className="text-sm text-gray-500">Photograph a handwritten prescription and get a digital card with safety check.</p>
        </div>
        <div className="border rounded-xl p-5 bg-white shadow-sm hover:shadow-md transition">
          <div className="text-3xl mb-2">🤖</div>
          <h2 className="font-bold text-gray-800 mb-1">Ask SEHA</h2>
          <p className="text-sm text-gray-500">Ask health questions in Amharic or English — grounded in MoH guidelines.</p>
        </div>
      </div>

      <p className="text-xs text-gray-400 mt-8">
        ⚠️ For informational use only. Always consult a licensed healthcare provider.
      </p>
    </div>
  );
}
export default HomePage;