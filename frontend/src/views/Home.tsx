import React, { useEffect, useRef, useState } from "react";
import { Card } from "@/components/ui";
import axios from "axios";
import ReviewStats from "./ReviewStats";
import Recommendations from "./Recommendations";
import Tabs from '@/components/ui/Tabs'
import TabList from "@/components/ui/Tabs/TabList";
import TabNav from "@/components/ui/Tabs/TabNav";
import TabContent from "@/components/ui/Tabs/TabContent";
import EmotionAnalysis from "@/components/shared/EmotionAnalysis";
import Loading from "@/components/shared/Loading";

const MapSearchBox = () => {
    const mapRef = useRef<HTMLDivElement | null>(null);
    const inputRef = useRef<HTMLInputElement | null>(null);
    const [selectedPlace, setSelectedPlace] = useState<google.maps.places.PlaceResult | null>(null);
    const [responseData, setResponseData] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<any>(false);

    const loadGoogleMapsScript = async (): Promise<void> => {
        if (typeof window.google !== "undefined") {
            return;
        }

        return new Promise((resolve, reject) => {
            const existingScript = document.querySelector(
                `script[src*="maps.googleapis.com/maps/api/js"]`
            );

            if (existingScript) {
                existingScript.addEventListener("load", () => resolve());
                existingScript.addEventListener("error", () => reject(new Error("Failed to load Google Maps script")));
                return;
            }

            const script = document.createElement("script");
            script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyB41DRUbKWJHPxaFjMAwdrzWzbVKartNGg&callback=initAutocomplete&libraries=places&v=weekly`;
            script.async = true;
            script.defer = true;
            script.onload = () => resolve();
            script.onerror = () => reject(new Error("Failed to load Google Maps script"));
            document.head.appendChild(script);
        });
    };

    useEffect(() => {
        const initAutocomplete = () => {
            if (!window.google) {
                console.error("Google Maps API not loaded properly.");
                return;
            }

            const map = new google.maps.Map(mapRef.current as HTMLElement, {
                center: { lat: 7.2906, lng: 80.6337 },
                zoom: 13,
                mapTypeId: "roadmap",
                mapTypeControl: false,
                fullscreenControl: false,
                streetViewControl: false,
                zoomControl: false,
            });

            const searchBox = new google.maps.places.SearchBox(inputRef.current as HTMLInputElement);
            map.controls[google.maps.ControlPosition.TOP_LEFT].push(inputRef.current as HTMLElement);

            map.addListener("bounds_changed", () => {
                searchBox.setBounds(map.getBounds() as google.maps.LatLngBounds);
            });

            const markers: google.maps.Marker[] = [];

            searchBox.addListener("places_changed", () => {
                const places = searchBox.getPlaces();

                if (!places || places.length === 0) {
                    return;
                }

                markers.forEach((marker) => marker.setMap(null));
                markers.length = 0;

                const bounds = new google.maps.LatLngBounds();

                places.forEach((place) => {
                    if (!place.geometry || !place.geometry.location) {
                        console.error("Returned place contains no geometry");
                        return;
                    }

                    markers.push(
                        new google.maps.Marker({
                            map,
                            title: place.name,
                            position: place.geometry.location,
                        })
                    );

                    if (place.geometry.viewport) {
                        bounds.union(place.geometry.viewport);
                    } else {
                        bounds.extend(place.geometry.location);
                    }

                    setSelectedPlace(place);
                    setResponseData(null);
                });

                map.fitBounds(bounds);
            });
        };

        loadGoogleMapsScript()
            .then(() => {
                initAutocomplete();
            })
            .catch((error) => {
                console.error("Google Maps API loading failed:", error);
            });
    }, []);

    const fetchSentimentData = async (placeId: string) => {
        setIsLoading(true)
        try {
            const response = await axios.post("http://127.0.0.1:5000/analyze", { location_id: placeId });
            setResponseData(response.data);
            setIsLoading(false)
        } catch (error) {
            console.error("Error fetching sentiment data:", error);
        }
    };

    useEffect(() => {
        if (selectedPlace?.place_id) {
            fetchSentimentData(selectedPlace.place_id);
        }
    }, [selectedPlace]);

    const getEmotionsWithEmojis = (emotions: any) => {
        // Map of emotions to emojis
        const emotionEmojis: { [key: string]: string } = {
            anger: "😡",
            anticipation: "🤔",
            disgust: "🤢",
            fear: "😨",
            joy: "😊",
            sadness: "😢",
            surprise: "😮",
            trust: "🤝",
        };
    
        // Filter and sort emotions in descending order of values
        const sortedEmotions = Object.entries(emotions)
            .filter(([key]) => key in emotionEmojis) // Only include emotions with emojis
            .sort((a, b) => (b[1] as number) - (a[1] as number)); // Sort by value (highest to lowest)
    
        // Return sorted emotions with emojis
        return sortedEmotions.map(
            ([emotion, value]) => `${emotionEmojis[emotion]} ${emotion.charAt(0).toUpperCase() + emotion.slice(1)} (${value})`
        );
    };

    
    return (
        <div>
            <div className="flex flex-col gap-4 max-w-full overflow-x-hidden">
                <div className="flex flex-col xl:flex-row gap-4">
                    <div className="flex flex-col gap-4 2xl:min-w-[360px]">
                        <div className="max-w-full">
                            <Card
                                clickable
                                className="hover:shadow-lg transition duration-150 ease-in-out dark:border dark:border-gray-600 dark:border-solid"
                            >
                                <span className="text-emerald-600 font-semibold">Find The Place</span>
                                <h4 className="font-bold my-3">
                                    <input
                                        ref={inputRef}
                                        type="text"
                                        placeholder="Search for a place"
                                        className="absolute top-2 left-2 z-10 w-80 p-2 border rounded-lg mb-3"
                                    />
                                </h4>
                                <div ref={mapRef} style={{ height: "300px", width: "100%", marginTop: "20px" }}></div>
                            </Card>
                        </div>
                        <ReviewStats googleSentiment={responseData?.google_sentiment} tripadvisorSentiment={responseData?.tripadvisor_sentiment} />
                    </div>
                    <div className="flex flex-col gap-4 flex-1 xl:col-span-3">
                        <Loading loading={isLoading}>
                        <div className="max-w-full">
                            <Card
                                clickable
                                className="hover:shadow-lg transition duration-150 ease-in-out dark:border dark:border-gray-600 dark:border-solid"
                            >
                                <span className="text-emerald-600 font-semibold">
                                    Sentiment Analysis with Recommendations: {responseData?.location_name}
                                </span>
                                {responseData ? (
                                    <div className="space-y-4">

                                        <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
                                            <div className="lg:col-span-2">
                                                <div className="">
                                                    <div className="mt-8">
                                                        <h5 className="mb-4">{responseData?.recommendations?.title}</h5>
                                                        <div
                                                            className="mt-2 prose max-w-full cursor-pointer"
                                                            role="button"
                                                        >
                                                            <div className="prose-p:text-sm prose-p:dark:text-gray-400">
                                                                <p>
                                                                    {responseData?.recommendations?.overall_aspect}
                                                                </p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="mt-8">
                                                        <Tabs className="mt-6" defaultValue="comments">
                                                            <TabList>
                                                                <TabNav value="comments">Owners Recomendations</TabNav>
                                                                <TabNav value="attachments">Customer Insights</TabNav>
                                                            </TabList>
                                                            <div className="p-4">
                                                                <TabContent value="comments">
                                                                    <div className="w-full">
                                                                        <Recommendations data={responseData.recommendations.for_owners} />
                                                                    </div>
                                                                </TabContent>
                                                                <TabContent value="attachments">
                                                                    <div className="w-full">
                                                                        <ul className="list-disc pl-5">
                                                                            {responseData.recommendations.for_customers.map((insight: any, index: number) => (
                                                                                <li key={index} className="mb-2">
                                                                                    <strong>{insight.title}</strong>: {insight.insights}
                                                                                </li>
                                                                            ))}
                                                                        </ul>
                                                                    </div>
                                                                </TabContent>
                                                            </div>
                                                        </Tabs>
                                                        <EmotionAnalysis what_emotions_says={responseData?.what_emotions_says} />
                                                    </div>
                                                </div>
                                            </div>
                                            <div>
                                                <img
                                                    src={`data:image/png;base64,${responseData.word_cloud}`}
                                                    alt="Word Cloud"
                                                    className="w-full max-h-64 object-contain"
                                                />
                                                <div className="text-sm m-2">
                                                    <strong>Emotions:</strong>
                                                    <ul className="mt-2 space-y-1">
                                                        {getEmotionsWithEmojis(responseData?.emotions).map((emotion, index) => (
                                                            <li key={index} className="flex items-center space-x-2">
                                                                <span>{emotion}</span>
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                                <div className="text-sm m-2">
                                              
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    <p className="text-gray-500">Select a place to view sentiment analysis.</p>
                                )}
                            </Card>
                        </div>
                        </Loading>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MapSearchBox;
