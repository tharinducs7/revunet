import React, { useEffect, useState } from 'react';

interface ReviewsProps {
    placeId: string | undefined;
}

const Reviews: React.FC<ReviewsProps> = ({ placeId }) => {
    const [reviews, setReviews] = useState<google.maps.places.PlaceReview[]>([]);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!placeId) return;

        const fetchReviews = () => {
            const service = new google.maps.places.PlacesService(document.createElement('div'));
     
            
            service.getDetails(
                {
                    placeId,
                    fields: ['reviews'],
                },
                (place, status) => {
                    if (status === google.maps.places.PlacesServiceStatus.OK && place?.reviews) {
                        setReviews(place.reviews);
                    } else {
                        setError('Failed to fetch reviews.');
                        console.error('Place Details request failed:', status);
                    }
                }
            );
        };

        fetchReviews();
    }, [placeId]);

    if (!placeId) {
        return null;
    }
    console.log(reviews, "reviews");
    return (
        <div className="mt-4 p-4 bg-gray-100 rounded-lg">
            <h3 className="text-lg font-bold">Reviews</h3>
            {error && <p className="text-red-500">{error}</p>}
            {reviews.length > 0 ? (
                <ul>
                    {reviews.map((review, index) => (
                        <li key={index} className="mb-4 border-b pb-2">
                            <p className="font-bold">{review.author_name}</p>
                            <p>Rating: {review.rating}</p>
                            <p>{review.text}</p>
                        </li>
                    ))}
                </ul>
            ) : (
                <p>No reviews available.</p>
            )}
        </div>
    );
};

export default Reviews;
