import React from "react";
import { Alert } from "@/components/ui"; // Assuming you're using a custom Alert component

type Status = "success" | "danger" | "info";

const getSentimentType = (score: number): { type: Status; label: string } => {
    if (score > 0.1) return { type: "success", label: "positive" }; // Positive sentiment
    if (score < -0.1) return { type: "danger", label: "negative" }; // Negative sentiment
    return { type: "info", label: "neutral" }; // Neutral sentiment
};

const SentimentAlert = ({ sentimentScore }: { sentimentScore: any }) => {
    const { type, label } = getSentimentType(sentimentScore);

    return sentimentScore ? (
        <Alert showIcon className="mb-4" type={type}>
            The overall sentiment score is {sentimentScore.toFixed(2)}, indicating a {label} sentiment.
        </Alert>
    ): <small> N/A </small>;
};

export default SentimentAlert;
