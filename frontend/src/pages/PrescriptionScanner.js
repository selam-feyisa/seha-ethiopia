import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { scanPrescription, uploadToBlob } from '../api';

const SAFETY_STYLE = {
  SAFE:           { bg: '#f0fdf4', border: '#86efac', color: '#166534', icon: '✅' },
  'REVIEW NEEDED':{ bg: '#fffbeb', border: '#fcd34d', color: '#92400e', icon: '⚠️' },
  UNSAFE:         { bg: '#fef2f2', border: '#fca5a5', color: '#b91c1c', icon: '❌' },
  UNKNOWN:        { bg: '#f9fafb', border: '#d1d5db', color: '#6b7280', icon: '❓' },
};

const ACCEPTED_TYPES = {
  'image/png': ['.png'],
  'image/jpeg': ['.jpg', '.jpeg'],
};

function PrescriptionScanner() {
  const [imageUrl, setImageUrl] = useState('');
  const [droppedFile, setDroppedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    setError(null);
    setResult(null);
    if (rejectedFiles.length > 0) {
      setError('Only JPG and PNG images are allowed.');
      return;
    }
    if (acceptedFiles.length > 0) {
      setDroppedFile(acceptedFiles[0]);
      setImageUrl('');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxFiles: 1,
  });

  const handleScan = async () => {
    if (!droppedFile && !imageUrl.trim()) {
      setError('Please drop an image or enter an image URL.');
      return;
    }

    setError(null);
    setResult(null);
    setLoading(true);

    try {
      let targetUrl = imageUrl.trim();

      // Upload file to Azure Blob if dropped
      if (droppedFile) {
        const uploadRes = await uploadToBlob(droppedFile);
        targetUrl = uploadRes.data.url;
        console.log("✅ Uploaded prescription to Blob:", targetUrl);
      }

      if (!targetUrl) {
        throw new Error("No image URL available");
      }

      const res = await scanPrescription(targetUrl);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Could not scan the prescription. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const safety = result ? (SAFETY_STYLE[result.safety_status] || SAFETY_STYLE['UNKNOWN']) : null;

  return (
    <div style={{ maxWidth: '720px', margin: '0 auto', padding: '32px 20px' }}>

      <h1 style={{ fontSize: '1.75rem', fontWeight: 'bold', color: '#15803d', marginBottom: '4px' }}>
        💊 Prescription Scanner
      </h1>
      <p style={{ color: '#6b7280', marginBottom: '24px', fontSize: '0.95rem' }}>
        Take a photo or upload a prescription image to extract details and check safety.
      </p>

      {/* Drag & Drop Zone */}
      <div
        {...getRootProps()}
        style={{
          border: `2px dashed ${isDragActive ? '#15803d' : '#d1d5db'}`,
          borderRadius: '12px',
          background: isDragActive ? '#f0fdf4' : '#fafafa',
          padding: '40px 20px',
          textAlign: 'center',
          cursor: 'pointer',
          marginBottom: '16px'
        }}
      >
        <input {...getInputProps()} />
        <div style={{ fontSize: '2.5rem', marginBottom: '12px' }}>📸</div>
        {droppedFile ? (
          <p style={{ color: '#15803d', fontWeight: '600' }}>✓ {droppedFile.name}</p>
        ) : isDragActive ? (
          <p style={{ color: '#15803d' }}>Drop the prescription image here...</p>
        ) : (
          <p style={{ color: '#374151' }}>
            Drag & drop image here, click to browse,<br />or use camera below
          </p>
        )}
      </div>

      {/* Camera Capture */}
      <input
        type="file"
        accept="image/*"
        capture="environment"
        onChange={(e) => {
          if (e.target.files?.[0]) {
            setDroppedFile(e.target.files[0]);
            setImageUrl('');
          }
        }}
        style={{ marginBottom: '16px', width: '100%' }}
      />

      {/* URL Input (optional) */}
      <input
        type="text"
        placeholder="Or paste image URL"
        value={imageUrl}
        onChange={e => { setImageUrl(e.target.value); setDroppedFile(null); }}
        style={{
          width: '100%', padding: '12px 14px', borderRadius: '8px',
          border: '1px solid #d1d5db', fontSize: '0.95rem',
          boxSizing: 'border-box', marginBottom: '16px'
        }}
      />

      {error && (
        <div style={{
          background: '#fef2f2', border: '1px solid #fca5a5', color: '#b91c1c',
          borderRadius: '8px', padding: '10px 14px', marginBottom: '12px'
        }}>
          ⚠️ {error}
        </div>
      )}

      <button
        onClick={handleScan}
        disabled={loading}
        style={{
          width: '100%', background: loading ? '#86efac' : '#15803d',
          color: 'white', border: 'none', borderRadius: '8px',
          padding: '14px', fontSize: '1rem', fontWeight: '600',
          cursor: loading ? 'not-allowed' : 'pointer', marginBottom: '24px'
        }}
      >
        {loading ? 'Scanning Prescription...' : '🔍 Scan Prescription'}
      </button>

      {/* Results */}
      {result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Prescription Card */}
          <div style={{ border: '1px solid #e5e7eb', borderRadius: '12px', background: 'white', padding: '24px' }}>
            <h2 style={{ fontWeight: '700', color: '#374151', marginBottom: '16px' }}>💊 Prescription Details</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              {[
                { label: 'Drug Name', value: result.drug_name },
                { label: 'Dosage', value: result.dose_mg ? `${result.dose_mg} mg` : null },
                { label: 'Frequency', value: result.frequency },
                { label: 'Duration', value: result.duration_days ? `${result.duration_days} days` : null },
                { label: 'Doctor', value: result.doctor_name },
                { label: 'Patient', value: result.patient_name },
              ].map(({ label, value }) => (
                <div key={label}>
                  <p style={{ fontSize: '0.75rem', color: '#9ca3af', margin: '0 0 2px' }}>{label}</p>
                  <p style={{ fontWeight: '600', color: value ? '#111827' : '#9ca3af' }}>
                    {value || 'Not detected'}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Safety */}
          {safety && (
            <div style={{
              border: `1px solid ${safety.border}`, borderRadius: '12px',
              background: safety.bg, padding: '20px'
            }}>
              <h2 style={{ fontWeight: '700', color: safety.color, marginBottom: '8px' }}>
                {safety.icon} Safety Status — {result.safety_status}
              </h2>
              <p style={{ color: safety.color, lineHeight: '1.6' }}>{result.safety_note}</p>
            </div>
          )}

          {/* Raw OCR */}
          {result.raw_ocr_text && (
            <details style={{ border: '1px solid #e5e7eb', borderRadius: '12px', padding: '16px', background: 'white' }}>
              <summary style={{ cursor: 'pointer', fontWeight: '600' }}>View Raw OCR Text</summary>
              <pre style={{ marginTop: '12px', whiteSpace: 'pre-wrap', fontSize: '0.85rem' }}>
                {result.raw_ocr_text}
              </pre>
            </details>
          )}
        </div>
      )}
    </div>
  );
}

export default PrescriptionScanner;