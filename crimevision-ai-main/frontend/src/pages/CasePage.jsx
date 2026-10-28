import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  FileText,
  Clock,
  Brain,
  MessageSquare,
  FolderOpen,
  Download,
  Loader2,
  Image,
  Mic,
} from 'lucide-react';
import EvidenceUpload from '../components/EvidenceUpload';
import EvidenceCard from '../components/EvidenceCard';
import AnalysisResults from '../components/AnalysisResults';
import Timeline from '../components/Timeline';
import CaseSummary from '../components/CaseSummary';
import ChatBox from '../components/ChatBox';
import {
  getCase,
  getEvidence,
  analyzeEvidence,
  getTimeline,
  downloadReport,
} from '../services/api';

// Tab names used for navigation within the case page
const TABS = ['Evidence', 'Timeline', 'Summary', 'Chat'];

function CasePage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [caseData, setCaseData] = useState(null);
  const [evidenceList, setEvidenceList] = useState([]);
  const [activeTab, setActiveTab] = useState('Evidence');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Timeline state
  const [timelineEvents, setTimelineEvents] = useState([]);
  const [timelineLoading, setTimelineLoading] = useState(false);

  // Selected evidence for viewing analysis results
  const [selectedEvidence, setSelectedEvidence] = useState(null);

  // Report download state
  const [downloadingReport, setDownloadingReport] = useState(false);

  // Fetch case details and evidence list
  const fetchCaseData = useCallback(async () => {
    try {
      const [caseRes, evidenceRes] = await Promise.all([
        getCase(id),
        getEvidence(id),
      ]);
      setCaseData(caseRes.data);
      setEvidenceList(evidenceRes.data || []);
    } catch (err) {
      setError('Failed to load case data.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchCaseData();
  }, [fetchCaseData]);

  // Fetch timeline when the Timeline tab is selected
  useEffect(() => {
    if (activeTab === 'Timeline') {
      const fetchTimeline = async () => {
        setTimelineLoading(true);
        try {
          const res = await getTimeline(id);
          const events = res.data?.timeline || res.data || [];
          setTimelineEvents(Array.isArray(events) ? events : []);
        } catch (err) {
          console.error('Failed to load timeline:', err);
          setTimelineEvents([]);
        } finally {
          setTimelineLoading(false);
        }
      };
      fetchTimeline();
    }
  }, [activeTab, id]);

  // Handle evidence analysis
  const handleAnalyze = async (evidenceId) => {
    await analyzeEvidence(evidenceId);
    // Refresh evidence list after analysis completes
    const res = await getEvidence(id);
    setEvidenceList(res.data || []);
  };

  // Handle opening analysis results for an evidence item
  const handleViewResults = (evidence) => {
    setSelectedEvidence(evidence);
  };

  // Handle PDF report download
  const handleDownloadReport = async () => {
    setDownloadingReport(true);
    try {
      const res = await downloadReport(id);
      // Create a blob URL and trigger browser download
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `case-${id}-report.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Report download failed:', err);
      setError('Failed to download report.');
    } finally {
      setDownloadingReport(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    );
  }

  // Error state
  if (error && !caseData) {
    return (
      <div className="p-8">
        <div className="bg-red-500 bg-opacity-20 border border-red-500 text-red-400 px-6 py-4 rounded-lg">
          {error}
        </div>
        <button
          onClick={() => navigate('/')}
          className="mt-4 flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header Area */}
      <div className="mb-6">
        {/* Back button */}
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </button>

        <div className="flex items-start justify-between">
          <div>
            {/* Case number */}
            <span className="text-xs font-mono text-blue-400 bg-blue-500 bg-opacity-10 px-2 py-1 rounded">
              {caseData?.case_number || `CV-${id}`}
            </span>

            {/* Case name */}
            <h1 className="text-2xl font-bold text-white mt-2">
              {caseData?.case_name || caseData?.name || 'Untitled Case'}
            </h1>

            {/* Description */}
            {caseData?.description && (
              <p className="text-gray-400 mt-1">{caseData.description}</p>
            )}
          </div>

          {/* Generate PDF Report button */}
          <button
            onClick={handleDownloadReport}
            disabled={downloadingReport}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-800 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-colors shrink-0"
          >
            {downloadingReport ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            {downloadingReport ? 'Generating...' : 'Generate PDF Report'}
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-500 bg-opacity-20 border border-red-500 text-red-400 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex border-b border-gray-700 mb-6">
        {TABS.map((tab) => {
          const Icon =
            tab === 'Evidence'
              ? FolderOpen
              : tab === 'Timeline'
              ? Clock
              : tab === 'Summary'
              ? Brain
              : MessageSquare;

          return (
            <button
              key={tab}
              onClick={() => {
                setActiveTab(tab);
                setSelectedEvidence(null); // Reset selection when switching tabs
              }}
              className={`flex items-center gap-2 px-5 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-white'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div>
        {/* ---- Evidence Tab ---- */}
        {activeTab === 'Evidence' && (
          <div>
            {/* Upload component */}
            <EvidenceUpload caseId={id} onUploadComplete={fetchCaseData} />

            {/* Analysis results panel (shown when user clicks "View Results") */}
            {selectedEvidence && (
              <div className="mb-6">
                <AnalysisResults
                  evidence={selectedEvidence}
                  onClose={() => setSelectedEvidence(null)}
                />
              </div>
            )}

            {/* Evidence cards grid */}
            {evidenceList.length === 0 ? (
              <div className="text-center py-12 bg-gray-800 border border-gray-700 rounded-lg">
                <FolderOpen className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400">No evidence uploaded yet.</p>
                <p className="text-gray-500 text-sm mt-1">
                  Drag and drop files above to upload evidence.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {evidenceList.map((evidence) => (
                  <EvidenceCard
                    key={evidence.id}
                    evidence={evidence}
                    onAnalyze={handleAnalyze}
                    onViewResults={handleViewResults}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* ---- Timeline Tab ---- */}
        {activeTab === 'Timeline' && (
          <div>
            {timelineLoading ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
              </div>
            ) : (
              <Timeline events={timelineEvents} />
            )}
          </div>
        )}

        {/* ---- Summary Tab ---- */}
        {activeTab === 'Summary' && <CaseSummary caseId={id} />}

        {/* ---- Chat Tab ---- */}
        {activeTab === 'Chat' && <ChatBox caseId={id} />}
      </div>
    </div>
  );
}

export default CasePage;
