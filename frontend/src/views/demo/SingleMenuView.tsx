import React, { useEffect, useRef, useState } from "react";
import { Card } from "@/components/ui";
import axios from "axios";

const MapSearchBox = () => {
    const mapRef1 = useRef<HTMLDivElement | null>(null);
    const inputRef1 = useRef<HTMLInputElement | null>(null);
    const mapRef2 = useRef<HTMLDivElement | null>(null);
    const inputRef2 = useRef<HTMLInputElement | null>(null);

    const [selectedPlace1, setSelectedPlace1] = useState<google.maps.places.PlaceResult | null>(null);
    const [selectedPlace2, setSelectedPlace2] = useState<google.maps.places.PlaceResult | null>(null);
    const [responseData1, setResponseData1] = useState<any>(null);
    const [responseData2, setResponseData2] = useState<any>(null);

    // Load Google Maps Script
    const loadGoogleMapsScript = async (): Promise<void> => {
        if (typeof window.google !== "undefined") return;

        return new Promise((resolve, reject) => {
            const existingScript = document.querySelector(`script[src*="maps.googleapis.com/maps/api/js"]`);
            if (existingScript) {
                existingScript.addEventListener("load", () => resolve());
                existingScript.addEventListener("error", () => reject(new Error("Failed to load Google Maps script")));
                return;
            }

            const script = document.createElement("script");
            script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&libraries=places&v=weekly`;
            script.async = true;
            script.defer = true;
            script.onload = () => resolve();
            script.onerror = () => reject(new Error("Failed to load Google Maps script"));
            document.head.appendChild(script);
        });
    };

    // Initialize Google Map and SearchBox
    const initializeAutocomplete = (mapRef: React.RefObject<HTMLDivElement>, inputRef: React.RefObject<HTMLInputElement>, setSelectedPlace: React.Dispatch<React.SetStateAction<google.maps.places.PlaceResult | null>>) => {
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
            if (!places || places.length === 0) return;

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

                if (place.geometry.viewport) bounds.union(place.geometry.viewport);
                else bounds.extend(place.geometry.location);

                setSelectedPlace(place);
            });

            map.fitBounds(bounds);
        });
    };

    useEffect(() => {
        loadGoogleMapsScript().then(() => {
            initializeAutocomplete(mapRef1, inputRef1, setSelectedPlace1);
            initializeAutocomplete(mapRef2, inputRef2, setSelectedPlace2);
        });
    }, []);

    // Fetch sentiment analysis data
    const fetchSentimentData = async (placeId: string, setResponseData: React.Dispatch<React.SetStateAction<any>>) => {
        try {
            const response = await axios.post("http://127.0.0.1:5000/analyze", { location_id: placeId });
            setResponseData(response.data);
        } catch (error) {
            console.error("Error fetching sentiment data:", error);
        }
    };

    useEffect(() => {
        if (selectedPlace1?.place_id) fetchSentimentData(selectedPlace1.place_id, setResponseData1);
        if (selectedPlace2?.place_id) fetchSentimentData(selectedPlace2.place_id, setResponseData2);
    }, [selectedPlace1, selectedPlace2]);

    return (
        <div className="flex flex-col gap-4 max-w-full overflow-x-hidden">
            {/* Card 1 */}
            <Card
                clickable
                className="hover:shadow-lg transition duration-150 ease-in-out dark:border dark:border-gray-600"
            >
                <span className="text-emerald-600 font-semibold">Find The Place 1</span>
                <input
                    ref={inputRef1}
                    type="text"
                    placeholder="Search for a place"
                    className="z-10 w-80 p-2 border rounded-lg mb-3"
                />
                <div ref={mapRef1} style={{ height: "300px", width: "100%", marginTop: "20px" }}></div>
            </Card>

            {/* Card 2 */}
            <Card
                clickable
                className="hover:shadow-lg transition duration-150 ease-in-out dark:border dark:border-gray-600"
            >
                <span className="text-emerald-600 font-semibold">Find The Place 2</span>
                <input
                    ref={inputRef2}
                    type="text"
                    placeholder="Search for another place"
                    className="z-10 w-80 p-2 border rounded-lg mb-3"
                />
                <div ref={mapRef2} style={{ height: "300px", width: "100%", marginTop: "20px" }}></div>
            </Card>

            {/* Sentiment Analysis Results */}
            {responseData1 && (
                <Card className="hover:shadow-lg transition duration-150 ease-in-out dark:border dark:border-gray-600">
                    <span className="text-emerald-600 font-semibold">
                        Sentiment Analysis for Place 1: {responseData1.location_name}
                    </span>
                    <div className="space-y-4 mt-3">
                        <p><strong>Sentiment:</strong> {responseData1.sentiment}</p>
                        <p><strong>Recommendations:</strong> {responseData1.recommendations}</p>
                    </div>
                </Card>
            )}

            {responseData2 && (
                <Card className="hover:shadow-lg transition duration-150 ease-in-out dark:border dark:border-gray-600">
                    <span className="text-emerald-600 font-semibold">
                        Sentiment Analysis for Place 2: {responseData2.location_name}
                    </span>
                    <div className="space-y-4 mt-3">
                        <p><strong>Sentiment:</strong> {responseData2.sentiment}</p>
                        <p><strong>Recommendations:</strong> {responseData2.recommendations}</p>
                    </div>
                </Card>
            )}
        </div>
    );
};

export default MapSearchBox;
