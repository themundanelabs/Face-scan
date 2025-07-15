import React from "react";

const FaceOverlay = ({ faceDetected, step }) => {
  return (
    <div className="absolute inset-0 pointer-events-none">
      {/* Face Guide Overlay */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="relative">
          {/* Dotted oval outline */}
          <div 
            className={`w-64 h-80 border-4 rounded-full transition-all duration-500 ${
              faceDetected 
                ? 'border-green-400 border-dashed animate-pulse' 
                : 'border-white border-dashed'
            }`}
            style={{
              borderStyle: 'dashed',
              borderDasharray: '10 5',
              animation: faceDetected ? 'pulse 2s ease-in-out infinite' : 'none'
            }}
          />
          
          {/* Center guideline for front view */}
          {step === 0 && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-px h-full bg-white/50" />
            </div>
          )}
          
          {/* Profile indicators */}
          {step === 1 && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-white text-4xl opacity-75">👈</div>
            </div>
          )}
          
          {step === 2 && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-white text-4xl opacity-75">👉</div>
            </div>
          )}
          
          {/* Status indicator */}
          <div className="absolute -bottom-12 left-1/2 transform -translate-x-1/2">
            <div className={`px-4 py-2 rounded-full text-sm font-medium ${
              faceDetected 
                ? 'bg-green-500 text-white' 
                : 'bg-red-500 text-white'
            }`}>
              {faceDetected ? 'Face Detected' : 'Position Your Face'}
            </div>
          </div>
        </div>
      </div>
      
      {/* Grid overlay for better positioning */}
      <div className="absolute inset-0 opacity-20">
        <div className="w-full h-full grid grid-cols-3 grid-rows-3 gap-0">
          {Array.from({ length: 9 }).map((_, i) => (
            <div key={i} className="border border-white/30" />
          ))}
        </div>
      </div>
    </div>
  );
};

export default FaceOverlay;