import SentimentAlert from "@/components/shared/SentimentAlert";
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

const getSentimentLabel = (score: any) => {
  if (score <= -0.5) return "Very Negative";
  if (score > -0.5 && score <= -0.1) return "Negative";
  if (score > -0.1 && score <= 0.1) return "Neutral";
  if (score > 0.1 && score <= 0.5) return "Positive";
  if (score > 0.5) return "Very Positive";
  return "Unknown";
};

const ReviewStats: React.FC<ReviewStatsProps> = ({ googleSentiment, tripadvisorSentiment }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-1 gap-4 rounded-2xl mt-4"  style={{ maxWidth: 360 }}>
      {/* Google Sentiment Card */}
      <div className="rounded-2xl p-4 flex flex-col justify-center bg-white dark:bg-opacity-75">
        <div className="flex justify-between items-center relative">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <span
                className="avatar avatar-circle bg-transparent"
                style={{
                  width: "28px",
                  height: "28px",
                  minWidth: "28px",
                  lineHeight: "28px",
                  fontSize: "12px",
                }}
              >
                <img
                  className="avatar-img avatar-circle"
                  loading="lazy"
                  src="/img/logo/google.png"
                  alt="google"
                />
              </span>
              <div className="heading-text font-bold">Google Sentiment </div>
            </div>
            <p className="mb-2">
              <SentimentAlert sentimentScore={googleSentiment?.average_sentiment} />
            </p>
          </div>
        </div>
      </div>

      {/* TripAdvisor Sentiment Card */}
        <div className="rounded-2xl p-4 flex flex-col justify-center bg-white dark:bg-opacity-75">
          <div className="flex justify-between relative">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span
                  className="avatar avatar-circle bg-transparent"
                  style={{
                    width: "28px",
                    height: "28px",
                    minWidth: "28px",
                    lineHeight: "28px",
                    fontSize: "12px",
                  }}
                >
                  <img
                    className="avatar-img avatar-circle"
                    loading="lazy"
                    src="/img/logo/trip.png"
                    alt="TripAdvisor"
                  />
                </span>
                <div className="heading-text font-bold">TripAdvisor Sentiment </div>
              </div>

              <p className="mb-2">
                <SentimentAlert sentimentScore={tripadvisorSentiment?.average_sentiment} />
              </p>
            </div>
          </div>
        </div>
    </div>
  );
};

export default ReviewStats;
