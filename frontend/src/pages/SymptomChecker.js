import { useState } from 'react';
import { checkSymptoms } from '../api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const SYMPTOMS = [
  'itching', 'skin_rash', 'nodal_skin_eruptions', 'continuous_sneezing',
  'shivering', 'chills', 'joint_pain', 'stomach_pain', 'acidity',
  'ulcers_on_tongue', 'muscle_wasting', 'vomiting', 'burning_micturition',
  'fatigue', 'weight_gain', 'anxiety', 'cold_hands_and_feets', 'mood_swings',
  'weight_loss', 'restlessness', 'lethargy', 'patches_in_throat',
  'irregular_sugar_level', 'cough', 'high_fever', 'sunken_eyes',
  'breathlessness', 'sweating', 'dehydration', 'indigestion', 'headache',
  'yellowish_skin', 'dark_urine', 'nausea', 'loss_of_appetite', 'pain_behind_the_eyes',
  'back_pain', 'constipation', 'abdominal_pain', 'diarrhoea', 'mild_fever',
  'yellow_urine', 'yellowing_of_eyes', 'acute_liver_failure', 'fluid_overload',
  'swelling_of_stomach', 'swelled_lymph_nodes', 'malaise', 'blurred_and_distorted_vision',
  'phlegm', 'throat_irritation', 'redness_of_eyes', 'sinus_pressure',
  'runny_nose', 'congestion', 'chest_pain', 'weakness_in_limbs',
  'fast_heart_rate', 'pain_during_bowel_movements', 'neck_pain',
  'dizziness', 'cramps', 'bruising', 'obesity', 'puffy_face_and_eyes',
  'enlarged_thyroid', 'brittle_nails', 'swollen_extremeties', 'excessive_hunger',
  'drying_and_tingling_lips', 'slurred_speech', 'knee_pain', 'hip_joint_pain',
  'muscle_weakness', 'stiff_neck', 'swelling_joints', 'movement_stiffness',
  'spinning_movements', 'loss_of_balance', 'unsteadiness', 'weakness_of_one_body_side',
  'loss_of_smell', 'bladder_discomfort', 'foul_smell_of_urine',
  'continuous_feel_of_urine', 'passage_of_gases', 'internal_itching',
  'depression', 'irritability', 'muscle_pain', 'altered_sensorium',
  'red_spots_over_body', 'belly_pain', 'abnormal_menstruation',
  'watering_from_eyes', 'increased_appetite', 'polyuria', 'family_history',
  'mucoid_sputum', 'rusty_sputum', 'lack_of_concentration', 'visual_disturbances',
  'receiving_blood_transfusion', 'receiving_unsterile_injections', 'coma',
  'stomach_bleeding', 'distention_of_abdomen', 'history_of_alcohol_consumption',
  'blood_in_sputum', 'prominent_veins_on_calf', 'palpitations',
  'painful_walking', 'pus_filled_pimples', 'blackheads', 'scurring',
  'skin_peeling', 'silver_like_dusting', 'small_dents_in_nails',
  'inflammatory_nails', 'blister', 'red_sore_around_nose', 'yellow_crust_ooze'
];

const TRIAGE_STYLE = {
  LOW:       { bg: 'bg-green-100 text-green-800 border-green-300',   dot: 'bg-green-500',   label: 'LOW RISK' },
  MEDIUM:    { bg: 'bg-yellow-100 text-yellow-800 border-yellow-300', dot: 'bg-yellow-500',  label: 'MEDIUM RISK' },
  HIGH:      { bg: 'bg-orange-100 text-orange-800 border-orange-300', dot: 'bg-orange-500',  label: 'HIGH RISK' },
  EMERGENCY: { bg: 'bg-red-100 text-red-800 border-red-300',         dot: 'bg-red-600',     label: 'EMERGENCY' },
};

// Show symptoms in readable form
const formatSymptom = (s) => s.replace(/_/g, ' ');

function SymptomChecker() {
  const [search, setSearch]     = useState('');
  const [selected, setSelected] = useState([]);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);
  const [results, setResults]   = useState(null);

  const filtered = SYMPTOMS.filter(s =>
    s.includes(search.toLowerCase().replace(/ /g, '_'))
  );

  const toggle = (symptom) => {
    setSelected(prev =>
      prev.includes(symptom)
        ? prev.filter(s => s !== symptom)
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
    } catch {
      setError('Could not reach the server. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSelected([]);
    setResults(null);
    setError(null);
    setSearch('');
  };

  const hasEmergency = results?.predictions?.some(p => p.triage === 'EMERGENCY');

  return (
    <div style={{ maxWidth: '720px', margin: '0 auto', padding: '32px 20px' }}>

      {/* Header */}
      <h1 style={{ fontSize: '1.75rem', fontWeight: 'bold', color: '#15803d', marginBottom: '4px' }}>
        🩺 Symptom Checker
      </h1>
      <p style={{ color: '#6b7280', marginBottom: '24px', fontSize: '0.95rem' }}>
        Select your symptoms below and get an AI-powered health assessment.
      </p>

      {/* Search box */}
      <input
        type="text"
        placeholder="Search symptoms..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        style={{
          width: '100%', padding: '10px 14px', borderRadius: '8px',
          border: '1px solid #d1d5db', marginBottom: '12px',
          fontSize: '0.9rem', boxSizing: 'border-box'
        }}
      />

      {/* Selected count */}
      {selected.length > 0 && (
        <div style={{ marginBottom: '10px', color: '#15803d', fontWeight: '600', fontSize: '0.9rem' }}>
          ✓ {selected.length} symptom{selected.length > 1 ? 's' : ''} selected
        </div>
      )}

      {/* Selected chips */}
      {selected.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '16px' }}>
          {selected.map(s => (
            <span
              key={s}
              onClick={() => toggle(s)}
              style={{
                background: '#15803d', color: 'white', borderRadius: '20px',
                padding: '4px 12px', fontSize: '0.8rem', cursor: 'pointer'
              }}
            >
              {formatSymptom(s)} ✕
            </span>
          ))}
        </div>
      )}

      {/* Symptom grid */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))',
        gap: '8px', marginBottom: '20px', maxHeight: '280px', overflowY: 'auto',
        border: '1px solid #e5e7eb', borderRadius: '8px', padding: '12px'
      }}>
        {filtered.map(symptom => (
          <button
            key={symptom}
            onClick={() => toggle(symptom)}
            style={{
              border: selected.includes(symptom) ? '2px solid #15803d' : '1px solid #d1d5db',
              borderRadius: '8px', padding: '8px 12px', fontSize: '0.8rem',
              textAlign: 'left', cursor: 'pointer', textTransform: 'capitalize',
              background: selected.includes(symptom) ? '#dcfce7' : 'white',
              color: selected.includes(symptom) ? '#15803d' : '#374151',
              fontWeight: selected.includes(symptom) ? '600' : 'normal',
              transition: 'all 0.15s'
            }}
          >
            {selected.includes(symptom) ? '✓ ' : ''}{formatSymptom(symptom)}
          </button>
        ))}
        {filtered.length === 0 && (
          <p style={{ color: '#9ca3af', fontSize: '0.85rem', gridColumn: '1/-1' }}>
            No symptoms found for "{search}"
          </p>
        )}
      </div>

      {/* Error */}
      {error && (
        <div style={{
          background: '#fef2f2', border: '1px solid #fca5a5', color: '#b91c1c',
          borderRadius: '8px', padding: '12px 16px', marginBottom: '16px', fontSize: '0.9rem'
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* Buttons */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
        <button
          onClick={handleSubmit}
          disabled={loading}
          style={{
            flex: 1, background: loading ? '#86efac' : '#15803d', color: 'white',
            border: 'none', borderRadius: '8px', padding: '14px',
            fontSize: '1rem', fontWeight: '600', cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Analyzing...' : 'Check Symptoms'}
        </button>
        {(selected.length > 0 || results) && (
          <button
            onClick={handleClear}
            style={{
              padding: '14px 20px', border: '1px solid #d1d5db', borderRadius: '8px',
              background: 'white', color: '#6b7280', cursor: 'pointer', fontSize: '0.9rem'
            }}
          >
            Clear
          </button>
        )}
      </div>

      {/* Loading */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '24px', color: '#6b7280' }}>
          <div style={{
            width: '40px', height: '40px', border: '4px solid #dcfce7',
            borderTop: '4px solid #15803d', borderRadius: '50%',
            animation: 'spin 0.8s linear infinite', margin: '0 auto 12px'
          }} />
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          Analyzing your symptoms with AI...
        </div>
      )}

      {/* Results */}
      {results && (
        <div>
          <h2 style={{ fontWeight: '600', color: '#374151', marginBottom: '16px', fontSize: '1.1rem' }}>
            Assessment Results:
          </h2>

          {/* Emergency banner */}
          {hasEmergency && (
            <div style={{
              background: '#dc2626', color: 'white', borderRadius: '10px',
              padding: '16px', marginBottom: '16px', textAlign: 'center',
              fontWeight: 'bold', fontSize: '1.1rem'
            }}>
              🚨 EMERGENCY — Go to the nearest hospital immediately!
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {results.predictions?.map((pred, i) => {
              const style = TRIAGE_STYLE[pred.triage] || TRIAGE_STYLE['MEDIUM'];
              return (
                <div key={i} style={{
                  border: '1px solid #e5e7eb', borderRadius: '12px',
                  padding: '20px', background: 'white',
                  boxShadow: '0 1px 4px rgba(0,0,0,0.06)'
                }}>
                  {/* Top row */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <span style={{ fontWeight: '700', fontSize: '1.1rem', color: '#111827' }}>
                      {i + 1}. {pred.disease}
                    </span>
                    <span style={{
                      fontSize: '0.75rem', fontWeight: '700', padding: '4px 12px',
                      borderRadius: '20px', border: '1px solid',
                      ...Object.fromEntries(
                        style.bg.split(' ').map(cls => {
                          if (cls.startsWith('bg-')) return ['background', cls.includes('green') ? '#dcfce7' : cls.includes('yellow') ? '#fef9c3' : cls.includes('orange') ? '#ffedd5' : '#fee2e2'];
                          if (cls.startsWith('text-')) return ['color', cls.includes('green') ? '#166534' : cls.includes('yellow') ? '#854d0e' : cls.includes('orange') ? '#9a3412' : '#991b1b'];
                          if (cls.startsWith('border-')) return ['borderColor', cls.includes('green') ? '#86efac' : cls.includes('yellow') ? '#fde047' : cls.includes('orange') ? '#fdba74' : '#fca5a5'];
                          return [cls, cls];
                        })
                      )
                    }}>
                      {style.label}
                    </span>
                  </div>

                  {/* Probability bar */}
                  <div style={{ marginBottom: '10px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: '#6b7280', marginBottom: '4px' }}>
                      <span>Probability</span>
                      <span style={{ fontWeight: '600', color: '#374151' }}>{pred.probability}%</span>
                    </div>
                    <div style={{ background: '#f3f4f6', borderRadius: '999px', height: '8px' }}>
                      <div style={{
                        width: `${pred.probability}%`, height: '8px', borderRadius: '999px',
                        background: pred.triage === 'EMERGENCY' ? '#dc2626' : pred.triage === 'HIGH' ? '#ea580c' : pred.triage === 'MEDIUM' ? '#ca8a04' : '#16a34a',
                        transition: 'width 0.5s ease'
                      }} />
                    </div>
                  </div>

                  {/* Explanation */}
                  {pred.explanation && (
                    <p style={{ fontSize: '0.875rem', color: '#4b5563', margin: 0 }}>
                      💡 {pred.explanation}
                    </p>
                  )}
                </div>
              );
            })}
          </div>

          <p style={{ fontSize: '0.75rem', color: '#9ca3af', marginTop: '20px', textAlign: 'center' }}>
            ⚠️ This is for information only. Always consult a licensed healthcare provider.
          </p>
        </div>
      )}
    </div>
  );
}

export default SymptomChecker;