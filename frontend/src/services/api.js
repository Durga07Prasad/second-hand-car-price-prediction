/**
 * API Service — Centralized Axios client for the Car Price Prediction backend.
 * 
 * Base URL is read from the VITE_API_URL environment variable.
 * Falls back to http://localhost:8000 for local development.
 */
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: { 
    'Content-Type': 'application/json',
    'X-Device-Type': 'web',
  },
});

// ─── Health Check ────────────────────────────────────────────────────
export async function getHealth() {
  try {
    const { data } = await api.get('/health');
    return data;
  } catch (err) {
    throw new Error('Unable to reach the prediction API. Is the backend running?');
  }
}

// ─── Model Metadata ──────────────────────────────────────────────────
export async function getModelInfo() {
  try {
    const { data } = await api.get('/model-info');
    return data;
  } catch (err) {
    throw new Error('Failed to fetch model information.');
  }
}

// ─── Feature Importance (Top 15) ─────────────────────────────────────
export async function getFeatureImportance() {
  try {
    const { data } = await api.get('/feature-importance');
    return data;
  } catch (err) {
    throw new Error('Failed to fetch feature importance data.');
  }
}

// ─── Predict Price (no explanation) ──────────────────────────────────
export async function predictPrice(carData) {
  try {
    const { data } = await api.post('/predict', carData);
    return data;
  } catch (err) {
    const detail = err.response?.data?.detail;
    throw new Error(detail || 'Prediction failed. Please check your inputs.');
  }
}

// ─── Predict Price + SHAP Explanation ────────────────────────────────
export async function predictWithExplanation(carData) {
  try {
    const { data } = await api.post('/predict-with-explanation', carData);
    return data;
  } catch (err) {
    const detail = err.response?.data?.detail;
    throw new Error(detail || 'Prediction with explanation failed.');
  }
}

// ─── Prediction History ──────────────────────────────────────────────
export async function getPredictionHistory(limit = 20) {
  try {
    const { data } = await api.get(`/predictions/history?limit=${limit}`);
    return data;
  } catch (err) {
    throw new Error('Failed to fetch prediction history.');
  }
}

// ─── Prediction Stats ────────────────────────────────────────────────
export async function getPredictionStats() {
  try {
    const { data } = await api.get('/predictions/stats');
    return data;
  } catch (err) {
    throw new Error('Failed to fetch prediction statistics.');
  }
}

export default api;
