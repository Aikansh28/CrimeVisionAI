import React, { useState } from 'react';
import { Image, Mic, Search, Eye, Calendar } from 'lucide-react';

function EvidenceCard({ evidence, onAnalyze, onViewResults }) {
  const [analyzing, setAnalyzing] = useState(false);

  const isImage = evidence.file_type === 'image';
  const isAudio = evidence.file_type === 'audio';
  const hasResults = evidence.analysis_result !== null && evidence.analysis_result !== undefined;

  // Handle the analyze button click
  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      await onAnalyze(evidence.id);
    } catch (err) {
      console.error('Analysis failed:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  // Format the creation date
  const formattedDate = evidence.created_at
    ? new Date(evidence.created_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : 'Unknown date';

  return (
    <div className="evidence-card bg-gray-800 border border-gray-700 rounded-lg p-4 shadow-lg transition-all">
      {/* File icon and type badge */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div
            className={`p-2 rounded-lg ${
              isImage ? 'bg-purple-500 bg-opacity-20' : 'bg-amber-500 bg-opacity-20'
            }`}
          >
            {isImage ? (
              <Image className="w-5 h-5 text-purple-400" />
            ) : (
              <Mic className="w-5 h-5 text-amber-400" />
            )}
          </div>

          {/* Type badge */}
          <span
            className={`text-xs font-semibold px-2 py-1 rounded ${
              isImage
                ? 'bg-purple-500 bg-opacity-20 text-purple-400'
                : 'bg-amber-500 bg-opacity-20 text-amber-400'
            }`}
          >
            {isImage ? 'IMAGE' : 'AUDIO'}
          </span>
        </div>
      </div>

      {/* Filename */}
      <h3 className="text-sm font-medium text-white truncate mb-2" title={evidence.filename}>
        {evidence.filename}
      </h3>

      {/* Created date */}
      <div className="flex items-center gap-1 text-xs text-gray-500 mb-4">
        <Calendar className="w-3 h-3" />
        {formattedDate}
      </div>

      {/* Analysis action */}
      <div>
        {hasResults ? (
          <button
            onClick={() => onViewResults(evidence)}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-white text-sm font-medium transition-colors"
          >
            <Eye className="w-4 h-4" />
            View Results
          </button>
        ) : analyzing ? (
          <div className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-blue-800 rounded-lg text-blue-300 text-sm">
            <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
            Analyzing...
          </div>
        ) : (
          <button
            onClick={handleAnalyze}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white text-sm font-medium transition-colors"
          >
            <Search className="w-4 h-4" />
            Analyze
          </button>
        )}
      </div>
    </div>
  );
}

export default EvidenceCard;
