import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_KEY = process.env.REACT_APP_API_KEY || '';

const api = axios.create({
  baseURL: API_URL,
  headers: API_KEY ? { Authorization: `Bearer ${API_KEY}` } : {},
});

export const checkSymptoms = (symptoms) =>
  api.post('/symptoms/check', { symptoms });

// Document Reader APIs
export const uploadToBlob = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const uploadDocument = (fileUrl) =>
  api.post('/documents/analyze', { file_url: fileUrl });

// Prescription Scanner API
export const scanPrescription = (imageUrl) =>
  api.post('/prescription/scan', { image_url: imageUrl });

// Ask SEHA API
export const askSeha = (question, language = 'en') =>
  api.post('/ask/query', { question, language });

export const askSehaStream = async (question, language, { onMeta, onToken, onDone, onError }) => {
  try {
    const response = await fetch(`${API_URL}/ask/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(API_KEY ? { Authorization: `Bearer ${API_KEY}` } : {}),
      },
      body: JSON.stringify({ question, language }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || 'Stream request failed');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const payload = JSON.parse(line.slice(6));
        if (payload.type === 'meta') onMeta?.(payload);
        else if (payload.type === 'token') onToken?.(payload.content);
        else if (payload.type === 'done') onDone?.();
      }
    }
    onDone?.();
  } catch (err) {
    onError?.(err.message || 'Could not reach the server.');
  }
};