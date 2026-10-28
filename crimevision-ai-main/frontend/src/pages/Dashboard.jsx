import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Plus, Play, FolderOpen, FileText, Loader2 } from 'lucide-react';
import CreateCaseModal from '../components/CreateCaseModal';
import { getCases, createCase, loadDemoCase } from '../services/api';

function Dashboard() {
  const navigate = useNavigate();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [loadingDemo, setLoadingDemo] = useState(false);

  // Fetch all cases on mount
  const fetchCases = useCallback(async () => {
    try {
      const res = await getCases();
      setCases(res.data || []);
    } catch (err) {
      setError('Failed to load cases.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  // Create a new case
  const handleCreateCase = async (data) => {
    const res = await createCase(data);
    // Refresh the list and navigate to the new case
    await fetchCases();
    navigate(`/case/${res.data.id}`);
  };

  // Load a demo case
  const handleLoadDemo = async () => {
    setLoadingDemo(true);
    setError('');
    try {
      // First create a case, then load demo data into it
      const createRes = await createCase({
        case_name: 'Demo Case - Downtown Incident',
        description: 'Demo case with sample forensic evidence (Fictional Data).',
      });
      const caseId = createRes.data.id;
      await loadDemoCase(caseId);
      navigate(`/case/${caseId}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load demo case.');
    } finally {
      setLoadingDemo(false);
    }
  };

  // Calculate total evidence count across all cases
  const totalEvidence = cases.reduce((sum, c) => sum + (c.evidence_count || 0), 0);

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Shield className="w-8 h-8 text-blue-500" />
          <h1 className="text-3xl font-bold text-white">CrimeVision AI</h1>
        </div>
        <p className="text-gray-400">AI-Assisted Forensic Evidence Analysis</p>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-2 gap-4 mb-8 max-w-md">
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <p className="text-sm text-gray-400">Total Cases</p>
          <p className="text-2xl font-bold text-white">{cases.length}</p>
        </div>
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <p className="text-sm text-gray-400">Total Evidence</p>
          <p className="text-2xl font-bold text-white">{totalEvidence}</p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 mb-8">
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition-colors"
        >
          <Plus className="w-5 h-5" />
          Create New Case
        </button>
        <button
          onClick={handleLoadDemo}
          disabled={loadingDemo}
          className="flex items-center gap-2 px-5 py-2.5 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-colors"
        >
          {loadingDemo ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Play className="w-5 h-5" />
          )}
          {loadingDemo ? 'Loading Demo...' : 'Load Demo Case'}
        </button>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-500 bg-opacity-20 border border-red-500 text-red-400 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
        </div>
      ) : cases.length === 0 ? (
        /* Empty State */
        <div className="text-center py-16 bg-gray-800 border border-gray-700 rounded-lg">
          <FolderOpen className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg text-gray-300 mb-2">No Cases Yet</h3>
          <p className="text-gray-500 text-sm">Create a new case or load a demo to get started.</p>
        </div>
      ) : (
        /* Case Cards Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cases.map((caseItem) => (
            <div
              key={caseItem.id}
              onClick={() => navigate(`/case/${caseItem.id}`)}
              className="bg-gray-800 border border-gray-700 rounded-lg p-5 shadow-lg cursor-pointer hover:border-blue-500 transition-colors"
            >
              {/* Case Number */}
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-mono text-blue-400 bg-blue-500 bg-opacity-10 px-2 py-1 rounded">
                  {caseItem.case_number || `CV-${caseItem.id}`}
                </span>
                <span className="flex items-center gap-1 text-xs text-gray-500">
                  <FileText className="w-3 h-3" />
                  {caseItem.evidence_count || 0} evidence
                </span>
              </div>

              {/* Case Name */}
              <h3 className="text-white font-semibold mb-1 truncate">
                {caseItem.case_name || caseItem.name}
              </h3>

              {/* Description */}
              {caseItem.description && (
                <p className="text-gray-400 text-sm truncate mb-3">{caseItem.description}</p>
              )}

              {/* Created Date */}
              <p className="text-xs text-gray-500">
                {caseItem.created_at
                  ? new Date(caseItem.created_at).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })
                  : 'Unknown date'}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Create Case Modal */}
      <CreateCaseModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onCreate={handleCreateCase}
      />
    </div>
  );
}

export default Dashboard;
