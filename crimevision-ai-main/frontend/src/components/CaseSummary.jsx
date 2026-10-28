import React, { useState } from 'react';
import { Brain, Loader2, FileText, AlertTriangle, Eye, List } from 'lucide-react';
import { getSummary } from '../services/api';

function CaseSummary({ caseId }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch the AI-generated summary
  const handleGenerate = async () => {
    setLoading(true);
    setError('');

    try {
      const res = await getSummary(caseId);
      const data = res.data?.summary || res.data;
      if (data?.error) {
        setError(data.error);
        setSummary(null);
      } else {
        setSummary(data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate summary.');
    } finally {
      setLoading(false);
    }
  };

  // Show loading state
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <Loader2 className="w-10 h-10 text-blue-500 animate-spin mb-4" />
        <p className="text-gray-300 font-medium">Generating AI Summary...</p>
        <p className="text-gray-500 text-sm mt-1">This may take a moment.</p>
      </div>
    );
  }

  // Show the generate button if no summary has been generated
  if (!summary) {
    return (
      <div className="text-center py-16">
        <Brain className="w-16 h-16 text-gray-600 mx-auto mb-4" />
        <h3 className="text-lg text-gray-300 mb-2">AI Case Summary</h3>
        <p className="text-gray-500 text-sm mb-6 max-w-md mx-auto">
          Generate an AI-powered summary of all analyzed evidence in this case.
        </p>

        {error && (
          <div className="bg-red-500 bg-opacity-20 text-red-400 px-4 py-2 rounded-lg text-sm mb-4 max-w-md mx-auto">
            {error}
          </div>
        )}

        <button
          onClick={handleGenerate}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition-colors inline-flex items-center gap-2"
        >
          <Brain className="w-5 h-5" />
          Generate AI Summary
        </button>
      </div>
    );
  }

  // Display the summary results
  return (
    <div className="space-y-6">
      {/* Overview */}
      {summary.overview && (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-5">
          <div className="flex items-center gap-2 mb-3">
            <FileText className="w-5 h-5 text-blue-400" />
            <h3 className="text-white font-semibold">Overview</h3>
          </div>
          <p className="text-gray-300 text-sm leading-relaxed">{summary.overview}</p>
        </div>
      )}

      {/* Key Observations */}
      {summary.key_observations && summary.key_observations.length > 0 && (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-5">
          <div className="flex items-center gap-2 mb-3">
            <Eye className="w-5 h-5 text-green-400" />
            <h3 className="text-white font-semibold">Key Observations</h3>
          </div>
          <ul className="space-y-2">
            {summary.key_observations.map((obs, i) => (
              <li key={i} className="text-gray-300 text-sm flex items-start gap-2">
                <span className="text-green-400 mt-1">•</span>
                {obs}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Evidence Summary */}
      {summary.evidence_summary && summary.evidence_summary.length > 0 && (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-5">
          <div className="flex items-center gap-2 mb-3">
            <List className="w-5 h-5 text-blue-400" />
            <h3 className="text-white font-semibold">Evidence Summary</h3>
          </div>
          <ul className="space-y-2">
            {summary.evidence_summary.map((item, i) => (
              <li key={i} className="text-gray-300 text-sm flex items-start gap-2">
                <span className="text-blue-400 mt-1">•</span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Uncertainties */}
      {summary.uncertainties && summary.uncertainties.length > 0 && (
        <div className="bg-gray-800 border border-amber-600 border-opacity-40 rounded-lg p-5">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <h3 className="text-amber-400 font-semibold">Uncertainties</h3>
          </div>
          <ul className="space-y-2">
            {summary.uncertainties.map((item, i) => (
              <li key={i} className="text-amber-200 text-sm flex items-start gap-2">
                <span className="text-amber-400 mt-1">•</span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Regenerate button */}
      <div className="text-center pt-2">
        <button
          onClick={handleGenerate}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-gray-300 text-sm transition-colors"
        >
          Regenerate Summary
        </button>
      </div>
    </div>
  );
}

export default CaseSummary;
