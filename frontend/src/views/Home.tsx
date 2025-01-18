import React, { useEffect, useRef, useState } from "react";
import { Card } from "@/components/ui";
import axios from "axios";
import ReviewStats from "./ReviewStats";

const MapSearchBox = () => {
  const mapRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [selectedPlace, setSelectedPlace] = useState<google.maps.places.PlaceResult | null>(null);
  const [responseData, setResponseData] = useState<any>(null);

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
    try {
      const response = await axios.post("http://127.0.0.1:5000/analyze", { location_id: placeId });
      setResponseData(response.data);
    } catch (error) {
      console.error("Error fetching sentiment data:", error);
    }
  };

  useEffect(() => {
    if (selectedPlace?.place_id) {
      fetchSentimentData(selectedPlace.place_id);
    }
  }, [selectedPlace]);

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
                <div ref={mapRef} style={{ height: "500px", width: "100%", marginTop: "20px" }}></div>
              </Card>
            </div>
          </div>
          <div className="flex flex-col gap-4 flex-1 xl:col-span-3">
            <div className="max-w-full">
              <Card
                clickable
                className="hover:shadow-lg transition duration-150 ease-in-out dark:border dark:border-gray-600 dark:border-solid"
              >
                <span className="text-emerald-600 font-semibold">
                  Sentiment Analysis with Recommendations
                </span>
                {responseData ? (
                  <div className="space-y-4">
                    <h4 className="font-bold">{responseData.location_name}</h4>
                    <div className="text-sm">
                        <ReviewStats googleSentiment={responseData?.google_sentiment} tripadvisorSentiment={responseData?.tripadvisor_sentiment}/>
                      <p className="font-medium text-gray-700">**Google Sentiment Analysis:**</p>
                      <p>Average Sentiment: {responseData.google_sentiment.average_sentiment.toFixed(2)}</p>
                      <p>Average Star Count: {responseData.google_sentiment.avg_star_count.toFixed(1)}</p>
                      <p>
                        Sentiment Group:
                        <span className="ml-2">
                          {JSON.stringify(responseData.google_sentiment.sentiment_category_group)}
                        </span>
                      </p>
                    </div>
                    <div className="text-sm">
                      <p className="font-medium text-gray-700">**TripAdvisor Sentiment Analysis:**</p>
                      <p>Average Sentiment: {responseData.tripadvisor_sentiment.average_sentiment.toFixed(2)}</p>
                      <p>Average Star Count: {responseData.tripadvisor_sentiment.avg_star_count.toFixed(1)}</p>
                      <p>
                        Sentiment Group:
                        <span className="ml-2">
                          {JSON.stringify(responseData.tripadvisor_sentiment.sentiment_category_group)}
                        </span>
                      </p>
                    </div>
                    <div>
                      <h5 className="font-semibold text-lg">Recommendations</h5>
                      <h6 className="font-bold">For Owners</h6>
                      <ul className="list-disc pl-5">
                        {responseData.recommendations.for_owners.map((rec: any, index: number) => (
                          <li key={index}>
                            <strong>{rec.title}</strong>: {rec.recommendation} (Priority: {rec.priority})
                          </li>
                        ))}
                      </ul>
                      <h6 className="font-bold mt-4">For Customers</h6>
                      <ul className="list-disc pl-5">
                        {responseData.recommendations.for_customers.map((insight: any, index: number) => (
                          <li key={index}>
                            <strong>{insight.title}</strong>: {insight.insights} (Priority: {insight.priority})
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="mt-4">
                      <img
                        src={`data:image/png;base64,${responseData.word_cloud}`}
                        alt="Word Cloud"
                        className="w-full max-h-64 object-contain"
                      />
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500">Select a place to view sentiment analysis.</p>
                )}
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapSearchBox;
