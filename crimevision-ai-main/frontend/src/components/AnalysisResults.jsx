import React from 'react';
import {
  Image,
  Mic,
  User,
  Crosshair,
  Package,
  Eye,
  FileText,
  Clock,
  AlertTriangle,
  Info,
  X,
} from 'lucide-react';

function AnalysisResults({ evidence, onClose }) {
  const result = evidence?.analysis_result;

  // If there are no results, show a message
  if (!result) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <p className="text-gray-400">No analysis results available yet.</p>
      </div>
    );
  }

  const isImage = evidence.file_type === 'image';

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
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
          <div>
            <h3 className="text-white font-medium">{evidence.filename}</h3>
            <p className="text-xs text-gray-400">AI Forensic Findings</p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Results body */}
      <div className="p-4 space-y-5">
        {result.error && (
          <div className="bg-red-500 bg-opacity-20 border border-red-500 text-red-400 p-3 rounded-lg text-sm flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{result.error}</span>
          </div>
        )}

        {isImage ? (
          <ImageResults result={result} />
        ) : (
          <AudioResults result={result} />
        )}
      </div>
    </div>
  );
}

/* ---------- Image Analysis Results ---------- */
function ImageResults({ result }) {
  const scene = result.scene || result.scene_description;
  const people = result.people || result.people_detected || [];
  const weapons = result.weapons || result.possible_weapons || [];
  const objects = result.objects || result.objects_found || [];
  const observations = result.observations || [];

  return (
    <>
      {/* Scene Description */}
      {scene && (
        <ResultSection icon={<Eye className="w-4 h-4" />} title="Scene Description">
          <p className="text-gray-300 text-sm leading-relaxed">{scene}</p>
        </ResultSection>
      )}

      {/* People Detected */}
      {people.length > 0 && (
        <ResultSection icon={<User className="w-4 h-4" />} title="People Visible">
          <ul className="space-y-1">
            {people.map((person, i) => (
              <li key={i} className="text-gray-300 text-sm flex items-start gap-2">
                <span className="text-blue-400 mt-1">•</span>
                <span>{person}</span>
              </li>
            ))}
          </ul>
        </ResultSection>
      )}

      {/* Possible Weapons */}
      {weapons.length > 0 && (
        <ResultSection
          icon={<Crosshair className="w-4 h-4 text-red-400" />}
          title="Possible Weapons"
          titleColor="text-red-400"
        >
          <ul className="space-y-1">
            {weapons.map((weapon, i) => (
              <li key={i} className="text-red-300 text-sm flex items-start gap-2">
                <AlertTriangle className="w-3 h-3 mt-1 text-red-400 shrink-0" />
                <span>{weapon}</span>
              </li>
            ))}
          </ul>
        </ResultSection>
      )}

      {/* Objects Found */}
      {objects.length > 0 && (
        <ResultSection icon={<Package className="w-4 h-4" />} title="Objects Identified">
          <div className="flex flex-wrap gap-2">
            {objects.map((obj, i) => (
              <span
                key={i}
                className="bg-gray-700 text-gray-300 text-xs px-2.5 py-1 rounded"
              >
                {obj}
              </span>
            ))}
          </div>
        </ResultSection>
      )}

      {/* Observations */}
      {observations.length > 0 && (
        <ResultSection icon={<Info className="w-4 h-4" />} title="Key Observations">
          <ul className="space-y-1">
            {observations.map((obs, i) => (
              <li key={i} className="text-gray-300 text-sm flex items-start gap-2">
                <span className="text-blue-400 mt-1">•</span>
                <span>{obs}</span>
              </li>
            ))}
          </ul>
        </ResultSection>
      )}
    </>
  );
}

/* ---------- Audio Analysis Results ---------- */
function AudioResults({ result }) {
  const keyEvents = result.key_events || [];
  const witnessStatements = result.witness_statements || [];
  const importantInfo = result.important_information || result.important_info;

  return (
    <>
      {/* Transcript */}
      {result.transcript && (
        <ResultSection icon={<FileText className="w-4 h-4" />} title="Full Transcript">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 max-h-60 overflow-y-auto">
            <p className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap font-mono text-xs">
              {result.transcript}
            </p>
          </div>
        </ResultSection>
      )}

      {/* Key Events */}
      {keyEvents.length > 0 && (
        <ResultSection icon={<Clock className="w-4 h-4" />} title="Key Events">
          <ul className="space-y-2">
            {keyEvents.map((event, i) => {
              const time = typeof event === 'object' ? event.time : 'Time unavailable';
              const text = typeof event === 'object' ? (event.event || event.description) : event;
              return (
                <li key={i} className="text-gray-300 text-sm flex items-start gap-2">
                  <span className="bg-blue-600 text-white text-xs px-2 py-0.5 rounded font-mono shrink-0">
                    {time || 'Time unavailable'}
                  </span>
                  <span>{text}</span>
                </li>
              );
            })}
          </ul>
        </ResultSection>
      )}

      {/* Witness Statements */}
      {witnessStatements.length > 0 && (
        <ResultSection icon={<User className="w-4 h-4 text-amber-400" />} title="Witness Statements" titleColor="text-amber-400">
          <ul className="space-y-2">
            {witnessStatements.map((stmt, i) => (
              <li
                key={i}
                className="bg-amber-500 bg-opacity-10 border border-amber-500 border-opacity-30 rounded-lg p-3 text-amber-200 text-sm"
              >
                {stmt}
              </li>
            ))}
          </ul>
        </ResultSection>
      )}

      {/* Important Information */}
      {importantInfo && (
        <ResultSection
          icon={<AlertTriangle className="w-4 h-4 text-blue-400" />}
          title="Important Information"
        >
          {Array.isArray(importantInfo) ? (
            <ul className="space-y-1">
              {importantInfo.map((info, i) => (
                <li key={i} className="text-gray-300 text-sm flex items-start gap-2">
                  <span className="text-blue-400 mt-1">•</span>
                  <span>{info}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-300 text-sm leading-relaxed">{importantInfo}</p>
          )}
        </ResultSection>
      )}

      {/* Summary if present */}
      {result.summary && (
        <ResultSection icon={<Info className="w-4 h-4" />} title="Audio Summary">
          <p className="text-gray-300 text-sm leading-relaxed">{result.summary}</p>
        </ResultSection>
      )}
    </>
  );
}

/* ---------- Reusable section wrapper ---------- */
function ResultSection({ icon, title, titleColor = 'text-white', children }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-blue-400">{icon}</span>
        <h4 className={`text-sm font-semibold ${titleColor}`}>{title}</h4>
      </div>
      {children}
    </div>
  );
}

export default AnalysisResults;
