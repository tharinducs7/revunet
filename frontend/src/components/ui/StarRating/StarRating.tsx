import React from "react";

type StarRatingProps = {
    rating: number; // Average star rating (e.g., 2.8, 4.5)
    maxStars?: number; // Maximum number of stars (default: 5)
};

const StarRating: React.FC<StarRatingProps> = ({ rating, maxStars = 5 }) => {
    const fullStars = Math.floor(rating); // Number of fully filled stars
    const hasHalfStar = rating % 1 >= 0.5; // Check if a half star is needed
    const emptyStars = maxStars - fullStars - (hasHalfStar ? 1 : 0); // Remaining empty stars

    return (
        <div className="flex items-center space-x-1">
            {/* Render full stars */}
            {Array.from({ length: fullStars }).map((_, index) => (
                <span key={`full-${index}`} className="text-yellow-500 text-xl">★</span>
            ))}
            {/* Render half star if applicable */}
            {hasHalfStar && <span className="text-yellow-500 text-xl">★</span>}
            {/* Render empty stars */}
            {Array.from({ length: emptyStars }).map((_, index) => (
                <span key={`empty-${index}`} className="text-gray-300 text-xl">★</span>
            ))}
        </div>
    );
};

export default StarRating;
