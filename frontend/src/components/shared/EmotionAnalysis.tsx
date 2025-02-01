import React from "react";

interface EmotionResponse {
  what_emotions_says: string;
}

const EmotionAnalysis: React.FC<EmotionResponse> = ({ what_emotions_says }) => {
  return (
    <div className="p-6 bg-white max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-4">Emotion Analysis Summary</h1>
      <p
        className="text-gray-700 mb-6 whitespace-pre-wrap"
        dangerouslySetInnerHTML={{
          __html: what_emotions_says.replace(
            /(\*\*.*?\*\*)/g,
            (match) => `<span class="font-bold">${match.replace(/\*\*/g, "")}</span>`
          ),
        }}
      ></p>
    </div>
  );
};

export default EmotionAnalysis;
