import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: API_URL });

export const checkSymptoms = (symptoms) =>
  api.post('/symptoms/check', { symptoms });

export const uploadDocument = (file) => {
  const form = new FormData();
  form.append('file', file);
  return api.post('/documents/upload', form);
};

export const scanPrescription = (file) => {
  const form = new FormData();
  form.append('file', file);
  return api.post('/prescription/scan', form);
};

export const askSeha = (question, language = 'en') =>
  api.post('/ask/query', { question, language });