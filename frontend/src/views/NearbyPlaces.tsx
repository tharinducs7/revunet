import React, { useEffect, useState } from 'react';

interface NearbyPlacesProps {
    location: google.maps.LatLngLiteral;
    types: string[]; // All relevant types from the selected place
    rating: number; // Selected place rating
}

const NearbyPlaces: React.FC<NearbyPlacesProps> = ({ location, types, rating }) => {
    const [higherRatings, setHigherRatings] = useState<google.maps.places.PlaceResult[]>([]);
    const [lowerRatings, setLowerRatings] = useState<google.maps.places.PlaceResult[]>([]);
    const [similarRatings, setSimilarRatings] = useState<google.maps.places.PlaceResult[]>([]);
    const [bestPlace, setBestPlace] = useState<google.maps.places.PlaceResult | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
console.log(types, "types");

    useEffect(() => {
        const fetchNearbyPlaces = () => {
            if (!window.google) {
                console.error('Google Maps API not loaded properly.');
                return;
            }

            const service = new google.maps.places.PlacesService(
                document.createElement('div') // Create an off-screen div for the PlacesService
            );

            const request: google.maps.places.PlaceSearchRequest = {
                location: new google.maps.LatLng(location.lat, location.lng),
                radius: 10000, // 10 km
                keyword: 'hotel in kandy', // Use first type as fallback
            };

            service.nearbySearch(request, (results, status) => {
                if (status === google.maps.places.PlacesServiceStatus.OK && results) {
                    const filteredResults = results.filter((place) =>
                        place.types?.some((type) => types.includes(type))
                    );

                    const sortedResults = filteredResults.sort(
                        (a, b) => (b.rating || 0) - (a.rating || 0) // Sort by rating descending
                    );

                    const higher = sortedResults.filter((place) => (place.rating || 0) > rating).slice(0, 2);
                    const lower = sortedResults.filter((place) => (place.rating || 0) < rating).slice(0, 2);
                    const similar = sortedResults.filter(
                        (place) =>
                            Math.abs((place.rating || 0) - rating) <= 0.2 &&
                            (place.rating || 0) !== rating
                    ).slice(0, 2);

                    setHigherRatings(higher);
                    setLowerRatings(lower);
                    setSimilarRatings(similar);

                    const highestRated = sortedResults[0];
                    if (highestRated && (highestRated.rating || 0) <= rating) {
                        setBestPlace(highestRated);
                    }
                } else {
                    console.error('Failed to fetch nearby places:', status);
                }
                setLoading(false);
            });
        };

        fetchNearbyPlaces();
    }, [location, types, rating]);

    if (loading) {
        return <p>Loading nearby places...</p>;
    }

    if (!higherRatings.length && !lowerRatings.length && !similarRatings.length) {
        return <p>No similar places found within 10 km.</p>;
    }

    return (
        <div className="mt-4">
            {bestPlace && (
                <div className="mt-4 p-4 bg-green-100 rounded-lg">
                    <h4 className="font-bold text-green-700">Best Place:</h4>
                    <p>{bestPlace.name}</p>
                    <p>Rating: {bestPlace.rating}</p>
                </div>
            )}

            <div className="mt-4">
                <h4 className="text-lg font-bold">Higher Performing Places:</h4>
                {higherRatings.length > 0 ? (
                    <ul className="mt-2">
                        {higherRatings.map((place, index) => (
                            <li key={index} className="mb-2 p-2 border rounded-lg">
                                <h4 className="font-semibold">{place.name}</h4>
                                <p>Rating: {place.rating || 'N/A'}</p>
                                <p>{place.vicinity}</p>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p>No higher-performing places found.</p>
                )}
            </div>

            <div className="mt-4">
                <h4 className="text-lg font-bold">Lower Performing Places:</h4>
                {lowerRatings.length > 0 ? (
                    <ul className="mt-2">
                        {lowerRatings.map((place, index) => (
                            <li key={index} className="mb-2 p-2 border rounded-lg">
                                <h4 className="font-semibold">{place.name}</h4>
                                <p>Rating: {place.rating || 'N/A'}</p>
                                <p>{place.vicinity}</p>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p>No lower-performing places found.</p>
                )}
            </div>

            <div className="mt-4">
                <h4 className="text-lg font-bold">Similar Performing Places:</h4>
                {similarRatings.length > 0 ? (
                    <ul className="mt-2">
                        {similarRatings.map((place, index) => (
                            <li key={index} className="mb-2 p-2 border rounded-lg">
                                <h4 className="font-semibold">{place.name}</h4>
                                <p>Rating: {place.rating || 'N/A'}</p>
                                <p>{place.vicinity}</p>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p>No similar-performing places found.</p>
                )}
            </div>
        </div>
    );
};

export default NearbyPlaces;
