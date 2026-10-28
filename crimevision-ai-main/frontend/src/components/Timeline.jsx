import React from 'react';
import { Image, Mic, Clock } from 'lucide-react';

function Timeline({ events }) {
  // Normalize events list if passed as { timeline: [...] } or null
  const eventList = Array.isArray(events) ? events : events?.timeline || [];

  // Show a message if there are no timeline events
  if (!eventList || eventList.length === 0) {
    return (
      <div className="text-center py-12">
        <Clock className="w-12 h-12 text-gray-600 mx-auto mb-3" />
        <p className="text-gray-400">No timeline data available.</p>
        <p className="text-gray-500 text-sm mt-1">Analyze evidence to build a timeline.</p>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* Vertical connecting line */}
      <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-700" />

      <div className="space-y-6">
        {eventList.map((event, index) => {
          const isImage = event.source?.toLowerCase() === 'image';
          const isAudio = event.source?.toLowerCase() === 'audio';

          return (
            <div key={index} className="relative flex items-start gap-4 pl-2">
              {/* Timeline dot */}
              <div className="relative z-10 flex items-center justify-center w-9 h-9 rounded-full bg-gray-800 border-2 border-blue-500 shrink-0">
                {isImage ? (
                  <Image className="w-4 h-4 text-purple-400" />
                ) : isAudio ? (
                  <Mic className="w-4 h-4 text-amber-400" />
                ) : (
                  <Clock className="w-4 h-4 text-blue-400" />
                )}
              </div>

              {/* Event card */}
              <div className="flex-1 bg-gray-800 border border-gray-700 rounded-lg p-4 shadow-lg">
                {/* Time */}
                <div className="flex items-center gap-2 mb-2">
                  <Clock className="w-3 h-3 text-gray-500" />
                  <span className="text-xs text-gray-400 font-mono">
                    {event.time || 'Time unavailable'}
                  </span>

                  {/* Source badge */}
                  {event.source && (
                    <span
                      className={`text-xs px-2 py-0.5 rounded ${
                        isImage
                          ? 'bg-purple-500 bg-opacity-20 text-purple-400'
                          : 'bg-amber-500 bg-opacity-20 text-amber-400'
                      }`}
                    >
                      {event.source}
                    </span>
                  )}
                </div>

                {/* Description */}
                <p className="text-gray-300 text-sm">{event.event || event.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default Timeline;
