import { useState } from 'react';
import { checkSymptoms } from '../api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const SYMPTOMS = [
  'fever', 'headache', 'chills', 'cough', 'fatigue',
  'nausea', 'vomiting', 'diarrhea', 'rash', 'chest pain',
  'shortness of breath', 'stiff neck', 'joint pain',
  'sore throat', 'abdominal pain', 'loss of appetite',
  'sweating', 'muscle pain', 'yellowing of skin', 'confusion'
];

const TRIAGE_STYLE = {
  LOW:       { bg: 'bg-green-100 text-green-800',   label: '🟢 LOW' },
  MEDIUM:    { bg: 'bg-yellow-100 text-yellow-800', label: '🟡 MEDIUM' },
  HIGH:      { bg: 'bg-orange-100 text-orange-800', label: '🟠 HIGH' },
  EMERGENCY: { bg: 'bg-red-100 text-red-800',       label: '🔴 EMERGENCY' },
};

function SymptomChecker() {
  const [selected, setSelected] = useState([]);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);
  const [results, setResults]   = useState(null);

  const toggle = (symptom) => {
    setSelected((prev) =>
      prev.includes(symptom)
        ? prev.filter((s) => s !== symptom)
        : [...prev, symptom]
    );
  };

  const handleSubmit = async () => {
    if (selected.length === 0) {
      setError('Please select at least one symptom.');
      return;
    }
    setError(null);
    setResults(null);
    setLoading(true);
    try {
      const res = await checkSymptoms(selected);
      setResults(res.data);
    } catch (err) {
      setError('Could not reach the server. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSelected([]);
    setResults(null);
    setError(null);
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-green-700 mb-1">Symptom Checker</h1>
      <p className="text-gray-500 text-sm mb-6">
        Select your symptoms below and get an AI-powered health assessment.
      </p>

      {/* Symptom Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mb-4">
        {SYMPTOMS.map((symptom) => (
          <button
            key={symptom}
            onClick={() => toggle(symptom)}
            className={`border rounded-lg px-3 py-2 text-sm capitalize text-left transition-all ${
              selected.includes(symptom)
                ? 'bg-green-600 text-white border-green-600 font-medium'
                : 'bg-white text-gray-700 border-gray-300 hover:border-green-400'
            }`}
          >
            {selected.includes(symptom) ? '✓ ' : ''}{symptom}
          </button>
        ))}
      </div>

      {/* Selected count */}
      {selected.length > 0 && (
        <p className="text-sm text-green-700 mb-3 font-medium">
          {selected.length} symptom{selected.length > 1 ? 's' : ''} selected
        </p>
      )}

      {/* Error */}
      {error && <ErrorMessage message={error} />}

      {/* Buttons */}
      <div className="flex gap-3 mb-4">
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="flex-1 bg-green-600 text-white font-semibold py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 transition-all"
        >
          {loading ? 'Checking...' : 'Check Symptoms'}
        </button>
        {(selected.length > 0 || results) && (
          <button
            onClick={handleClear}
            className="px-4 py-3 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50 text-sm"
          >
            Clear
          </button>
        )}
      </div>

      {/* Loading */}
      {loading && <LoadingSpinner message="Analyzing your symptoms with AI..." />}

      {/* Results */}
      {results && (
        <div className="mt-4">
          <h2 className="font-semibold text-gray-700 mb-3">Assessment Results:</h2>

          {/* Emergency banner */}
          {results.predictions?.some(p => p.triage === 'EMERGENCY') && (
            <div className="bg-red-600 text-white rounded-lg p-4 mb-4 font-semibold text-center animate-pulse">
              🚨 EMERGENCY — Please go to the nearest hospital immediately!
            </div>
          )}

          <div className="space-y-3">
            {results.predictions?.map((pred, i) => {
              const style = TRIAGE_STYLE[pred.triage] || TRIAGE_STYLE['LOW'];
              return (
                <div key={i} className="border rounded-lg p-4 bg-white shadow-sm">
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-semibold text-gray-800 text-lg">{pred.disease}</span>
                    <span className={`text-xs px-3 py-1 rounded-full font-semibold ${style.bg}`}>
                      {style.label}
                    </span>
                  </div>
                  <div className="mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500">Probability:</span>
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${pred.probability}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-700">{pred.probability}%</span>
                    </div>
                  </div>
                  {pred.explanation && (
                    <p className="text-sm text-gray-600 mt-2">{pred.explanation}</p>
                  )}
                </div>
              );
            })}
          </div>

          <p className="text-xs text-gray-400 mt-4 text-center">
            ⚠️ This is for information only. Always consult a licensed healthcare provider.
          </p>
        </div>
      )}
    </div>
  );
}

export default SymptomChecker;