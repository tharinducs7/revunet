import React, { useEffect, useRef, useState } from "react";
import { Card } from "@/components/ui";
import axios from "axios";
import SentimentAlert from "@/components/shared/SentimentAlert";
import EmotionAnalysis from "@/components/shared/EmotionAnalysis";

const MapSearchBox = () => {
    const mapRef1 = useRef<HTMLDivElement | null>(null);
    const inputRef1 = useRef<HTMLInputElement | null>(null);
    const mapRef2 = useRef<HTMLDivElement | null>(null);
    const inputRef2 = useRef<HTMLInputElement | null>(null);

    const [selectedPlace1, setSelectedPlace1] = useState<google.maps.places.PlaceResult | null>(
        JSON.parse(localStorage.getItem("selectedPlace1") || "null")
    );
    const [selectedPlace2, setSelectedPlace2] = useState<google.maps.places.PlaceResult | null>(
        JSON.parse(localStorage.getItem("selectedPlace2") || "null")
    );
    const [comparisonResult, setComparisonResult] = useState<any>(
        JSON.parse(localStorage.getItem("comparisonResult") || "null")
    );
    const [loading, setLoading] = useState(false);

    const loadGoogleMapsScript = async (): Promise<void> => {
        if (typeof window.google !== "undefined") return;

        return new Promise((resolve, reject) => {
            const script = document.createElement("script");
            script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyB41DRUbKWJHPxaFjMAwdrzWzbVKartNGg&libraries=places`;
            script.async = true;
            script.defer = true;
            script.onload = () => resolve();
            script.onerror = () => reject(new Error("Failed to load Google Maps script"));
            document.head.appendChild(script);
        });
    };

    const initializeAutocomplete = (
        mapRef: React.RefObject<HTMLDivElement>,
        inputRef: React.RefObject<HTMLInputElement>,
        setSelectedPlace: React.Dispatch<React.SetStateAction<google.maps.places.PlaceResult | null>>
    ) => {
        if (!window.google) return;

        const map = new google.maps.Map(mapRef.current as HTMLElement, {
            center: { lat: 7.2906, lng: 80.6337 },
            zoom: 13,
        });

        const searchBox = new google.maps.places.SearchBox(inputRef.current as HTMLInputElement);
        map.controls[google.maps.ControlPosition.TOP_LEFT].push(inputRef.current as HTMLElement);

        const markers: google.maps.Marker[] = [];
        searchBox.addListener("places_changed", () => {
            const places = searchBox.getPlaces();
            if (!places || places.length === 0) return;

            markers.forEach((marker) => marker.setMap(null));
            const bounds = new google.maps.LatLngBounds();

            places.forEach((place) => {
                if (!place.geometry || !place.geometry.location) return;

                markers.push(new google.maps.Marker({ map, position: place.geometry.location }));
                bounds.extend(place.geometry.location);
                setSelectedPlace(place);
                setComparisonResult(null); // Clear comparison result on new selection
            });

            map.fitBounds(bounds);
        });
    };

    const getTopEmotion = (emotions: any) => {
        const excludedKeys = ["positive", "negative", "trust"];
        const filteredEmotions = Object.entries(emotions).filter(
            ([key]) => !excludedKeys.includes(key)
        );

        const topEmotion = filteredEmotions.reduce<[string, number]>(
            (max, current) =>
                current[1] as number > max[1]
                    ? (current as [string, number])
                    : max,
            ["None", 0]
        );

        return `${topEmotion[0]} (${topEmotion[1]})`;
    };

    const getEmotionsWithEmojis = (emotions: any) => {
        const emotionEmojis: { [key: string]: string } = {
            anger: "😡",
            anticipation: "🤔",
            disgust: "🤢",
            fear: "😨",
            joy: "😊",
            sadness: "😢",
            surprise: "😮",
        };

        const sortedEmotions = Object.entries(emotions)
            .filter(([key]) => key in emotionEmojis)
            .sort((a, b) => (b[1] as number) - (a[1] as number));

        return sortedEmotions.map(
            ([emotion, value]) => `${emotionEmojis[emotion]} ${emotion.charAt(0).toUpperCase() + emotion.slice(1)} (${value})`
        );
    };

    const handleCompare = async () => {
        if (!selectedPlace1?.place_id || !selectedPlace2?.place_id) {
            alert("Please select two places to compare!");
            return;
        }

        setLoading(true);
        try {
            const response = await axios.post("http://127.0.0.1:5000/compare", {
                location_id1: selectedPlace1.place_id,
                location_id2: selectedPlace2.place_id,
            });
            setComparisonResult(response.data);
        } catch (error) {
            console.error("Error fetching comparison data:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadGoogleMapsScript().then(() => {
            initializeAutocomplete(mapRef1, inputRef1, setSelectedPlace1);
            initializeAutocomplete(mapRef2, inputRef2, setSelectedPlace2);
        });
    }, []);

    // Save data to localStorage whenever state changes
    useEffect(() => {
        localStorage.setItem("selectedPlace1", JSON.stringify(selectedPlace1));
        localStorage.setItem("selectedPlace2", JSON.stringify(selectedPlace2));
        localStorage.setItem("comparisonResult", JSON.stringify(comparisonResult));
    }, [selectedPlace1, selectedPlace2, comparisonResult]);

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
            <Card className="p-4">
                <h2 className="text-xl font-semibold mb-4 text-emerald-600">Find Place 1</h2>
                <input
                    ref={inputRef1}
                    type="text"
                    placeholder="Search for a place"
                    className="w-full p-2 border rounded-lg mb-4"
                />
                <div ref={mapRef1} className="h-64 w-full border rounded"></div>
            </Card>

            <Card className="p-4">
                <h2 className="text-xl font-semibold mb-4 text-emerald-600">Find Place 2</h2>
                <input
                    ref={inputRef2}
                    type="text"
                    placeholder="Search for another place"
                    className="w-full p-2 border rounded-lg mb-4"
                />
                <div ref={mapRef2} className="h-64 w-full border rounded"></div>
            </Card>

            <div className="col-span-full text-center">
                <button
                    onClick={handleCompare}
                    className="bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 transition"
                >
                    {loading ? "Comparing..." : "Compare"}
                </button>
            </div>

            {comparisonResult && (
                <div className="col-span-full">
                    <h2 className="text-2xl font-bold mb-6">Comparison Results</h2>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <Card className="p-4">
                            <h3 className="text-xl font-semibold mb-4">{comparisonResult.location1.name}</h3>
                            <p className="text-sm mb-2">
                                <SentimentAlert sentimentScore={comparisonResult.location1.google_sentiment.average_sentiment} />
                            </p>
                            <p className="text-sm mb-2">
                                <strong>Top Emotion:</strong> {getTopEmotion(comparisonResult.location1.emotions)}
                            </p>
                            <div className="text-sm ">
                            <strong>Consumer Emotions:</strong>
                                <ul className="mt-2 space-y-1">
                                    {getEmotionsWithEmojis(comparisonResult.location1.emotions)?.map((emotion, index) => (
                                        <li key={index} className="flex items-center space-x-2">
                                            <span>{emotion}</span>
                                        </li>
                                    ))}
                                </ul>
                                <EmotionAnalysis what_emotions_says={comparisonResult.location1.what_emotions_says1} />
                            </div>
                        </Card>
                        <Card className="p-4">
                            <h3 className="text-xl font-semibold mb-4">{comparisonResult.location2.name}</h3>
                            <p className="text-sm mb-2">
                                <SentimentAlert sentimentScore={comparisonResult.location2.google_sentiment.average_sentiment} />
                            </p>
                            <p className="text-sm mb-2">
                                <strong>Top Emotion:</strong> {getTopEmotion(comparisonResult.location2.emotions)}
                            </p>
                            <div className="text-sm">
                                <strong>Consumer Emotions:</strong>
                                <ul className="mt-2 space-y-1">
                                    {getEmotionsWithEmojis(comparisonResult.location2.emotions)?.map((emotion, index) => (
                                        <li key={index} className="flex items-center space-x-2">
                                            <span>{emotion}</span>
                                        </li>
                                    ))}
                                </ul>
                                <EmotionAnalysis what_emotions_says={comparisonResult.location2.what_emotions_says2} />
                            </div>
                        </Card>
                    </div>

                    <div className="mt-6">
                        <h3 className="text-xl font-semibold mb-4">Aspect Comparison</h3>
                        <div className="overflow-x-auto">
                        <Card className="p-4">
                            <table className="w-full border-collapse border border-gray-300">
                                <thead>
                                    <tr className="bg-gray-200">
                                        <th className="border border-gray-300 px-4 py-2 text-left">Aspect</th>
                                        <th className="border border-gray-300 px-4 py-2 text-left">{comparisonResult.location1.name}</th>
                                        <th className="border border-gray-300 px-4 py-2 text-left">{comparisonResult.location2.name}</th>
                                        <th className="border border-gray-300 px-4 py-2 text-left">Better Business</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {comparisonResult.comparison.aspect_comparison.map((aspect: any, index: number) => (
                                        <tr key={index} className="hover:bg-gray-100">
                                            <td className="border border-gray-300 px-4 py-2">{aspect.aspect}</td>
                                            <td className="border border-gray-300 px-4 py-2">{aspect.business1_score}</td>
                                            <td className="border border-gray-300 px-4 py-2">{aspect.business2_score}</td>
                                            <td className="border border-gray-300 px-4 py-2">{aspect.better_business}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            </Card>

                        </div>
                    </div>


                    {/* Recommendations Section */}
                    <div className="mt-6">
                        <h3 className="text-xl font-semibold mb-4">Recommendations</h3>
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* Recommendations for Business 1 */}
                            <Card className="p-4">
                                <h4 className="text-lg font-semibold mb-4 text-emerald-600">
                                    Recommendations for {comparisonResult.location1.name}
                                </h4>
                                <ul className="space-y-3">
                                    {comparisonResult.recommendations.for_business1?.map((rec: any, index: number) => (
                                        <li key={index} className="p-3 border rounded-lg bg-gray-50">
                                            <strong className="block mb-1 text-sm">{rec.title}</strong>
                                            <span className="text-xs text-gray-600">Priority: {rec.priority}</span>
                                            <p className="mt-1 text-sm">{rec.recommendation}</p>
                                        </li>
                                    ))}
                                </ul>
                            </Card>

                            {/* Recommendations for Business 2 */}
                            <Card className="p-4">
                                <h4 className="text-lg font-semibold mb-4 text-emerald-600">
                                    Recommendations for {comparisonResult.location2.name}
                                </h4>
                                <ul className="space-y-3">
                                    {comparisonResult.recommendations.for_business2?.map((rec: any, index: number) => (
                                        <li key={index} className="p-3 border rounded-lg bg-gray-50">
                                            <strong className="block mb-1 text-sm">{rec.title}</strong>
                                            <span className="text-xs text-gray-600">Priority: {rec.priority}</span>
                                            <p className="mt-1 text-sm">{rec.recommendation}</p>
                                        </li>
                                    ))}
                                </ul>
                            </Card>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MapSearchBox;
