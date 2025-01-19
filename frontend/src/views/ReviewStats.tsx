import React from "react";

interface ReviewStatsProps {
  googleSentiment: {
    average_sentiment: number;
    avg_star_count: number;
    sentiment_category_group: any;
  };
  tripadvisorSentiment: {
    average_sentiment: number;
    avg_star_count: number;
    sentiment_category_group: any;
  };
}

const ReviewStats: React.FC<ReviewStatsProps> = ({ googleSentiment, tripadvisorSentiment }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-1 gap-4 rounded-2xl mt-4">
      {/* Google Sentiment Card */}
      <div className="rounded-2xl p-4 flex flex-col justify-center bg-sky-100 dark:bg-opacity-75">
        <div className="flex justify-between items-center relative">
          <div>
            <div className="mb-4 text-gray-900 font-bold">Google Sentiment</div>
            <h4 className="mb-1 text-gray-900">
              Average Sentiment: {googleSentiment?.average_sentiment?.toFixed(2)}
            </h4>
            <h4 className="text-gray-700">
              Avg Star Count: {googleSentiment?.avg_star_count?.toFixed(2)}
            </h4>
          </div>
          <div className="flex items-center justify-center min-h-12 min-w-12 max-h-12 max-w-12 bg-white text-white rounded-full text-2xl">
            <img
              src="/img/logo/google.png" // Replace with your actual image path
              alt="Google Logo"
              className="h-8 w-8"
            />
          </div>
        </div>
      </div>

      {/* TripAdvisor Sentiment Card */}
      <div className="rounded-2xl p-4 flex flex-col justify-center bg-emerald-100 dark:bg-opacity-75">
        <div className="flex justify-between items-center relative">
          <div>
            <div className="mb-4 text-gray-900 font-bold">TripAdvisor Sentiment</div>
            <h4 className="mb-1 text-gray-900">
              Average Sentiment: {tripadvisorSentiment?.average_sentiment?.toFixed(2)}
            </h4>
            <h4 className="text-gray-700">
              Avg Star Count: {tripadvisorSentiment?.avg_star_count?.toFixed(2)}
            </h4>
          </div>
          <div className="flex items-center justify-center min-h-12 min-w-12 max-h-12 max-w-12 bg-white text-white rounded-full text-2xl">
            <img
              src="/img/logo/trip.png" // Replace with your actual image path
              alt="TripAdvisor Logo"
              className="h-8 w-8"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReviewStats;
