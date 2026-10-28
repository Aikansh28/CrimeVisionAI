import axios from 'axios';

const API_BASE = '/api';

// Cases
export const createCase = (data) => axios.post(`${API_BASE}/cases`, data);
export const getCases = () => axios.get(`${API_BASE}/cases`);
export const getCase = (id) => axios.get(`${API_BASE}/cases/${id}`);
export const loadDemoCase = (id) => axios.post(`${API_BASE}/cases/${id}/demo`);

// Evidence
export const uploadEvidence = (caseId, formData) =>
  axios.post(`${API_BASE}/cases/${caseId}/evidence`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
export const getEvidence = (caseId) => axios.get(`${API_BASE}/cases/${caseId}/evidence`);
export const analyzeEvidence = (evidenceId) => axios.post(`${API_BASE}/evidence/${evidenceId}/analyze`);

// Chat
export const sendChatMessage = (caseId, message) =>
  axios.post(`${API_BASE}/cases/${caseId}/chat`, { message });
export const getChatMessages = (caseId) => axios.get(`${API_BASE}/cases/${caseId}/chat`);

// Timeline
export const getTimeline = (caseId) => axios.get(`${API_BASE}/cases/${caseId}/timeline`);

// Summary
export const getSummary = (caseId) => axios.get(`${API_BASE}/cases/${caseId}/summary`);

// Report
export const downloadReport = (caseId) =>
  axios.get(`${API_BASE}/cases/${caseId}/report`, { responseType: 'blob' });
