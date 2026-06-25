import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const api = axios.create({ baseURL: API_URL });

export const checkSymptoms = (symptoms) =>
  api.post('/symptoms/check', { symptoms });

// Document Reader APIs
export const uploadToBlob = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};
export const uploadDocument = (fileUrl) =>
  api.post('/documents/upload', { file_url: fileUrl });

// Prescription Scanner API
export const scanPrescription = (imageUrl) =>
  api.post('/prescription/scan', { image_url: imageUrl });

// Ask SEHA API
export const askSeha = (question, language = 'en') =>
  api.post('/ask/query', { question, language });