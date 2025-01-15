// Google Maps API Key
// const apiKey = 'AIzaSyAIljBK9Z0_Z24gTwZAkxg6LYlKx19q3G0';
import React, { useEffect, useRef, useState } from 'react';
import Reviews from './Reviews'; // Adjust the path as necessary
import NearbyPlaces from './NearbyPlaces';

const MapSearchBox = () => {
    const mapRef = useRef<HTMLDivElement | null>(null);
    const inputRef = useRef<HTMLInputElement | null>(null);
    const [selectedPlace, setSelectedPlace] = useState<google.maps.places.PlaceResult | null>(null);

    const loadGoogleMapsScript = async (): Promise<void> => {
        if (typeof window.google !== 'undefined') {
            // Google Maps is already loaded
            return;
        }

        return new Promise((resolve, reject) => {
            const existingScript = document.querySelector(
                `script[src*="maps.googleapis.com/maps/api/js"]`
            );

            if (existingScript) {
                existingScript.addEventListener('load', () => resolve());
                existingScript.addEventListener('error', () => reject(new Error('Failed to load Google Maps script')));
                return;
            }

            const script = document.createElement('script');
            script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyB41DRUbKWJHPxaFjMAwdrzWzbVKartNGg&callback=initAutocomplete&libraries=places&v=weekly`;
            script.async = true;
            script.defer = true;
            script.onload = () => resolve();
            script.onerror = () => reject(new Error('Failed to load Google Maps script'));
            document.head.appendChild(script);
        });
    };

    useEffect(() => {
        const initAutocomplete = () => {
            if (!window.google) {
                console.error('Google Maps API not loaded properly.');
                return;
            }

            const map = new google.maps.Map(mapRef.current as HTMLElement, {
                center: { lat: 7.2906, lng: 80.6337 },
                zoom: 13,
                mapTypeId: 'roadmap',
            });

            const searchBox = new google.maps.places.SearchBox(inputRef.current as HTMLInputElement);
            map.controls[google.maps.ControlPosition.TOP_LEFT].push(inputRef.current as HTMLElement);

            map.addListener('bounds_changed', () => {
                searchBox.setBounds(map.getBounds() as google.maps.LatLngBounds);
            });

            const markers: google.maps.Marker[] = [];

            searchBox.addListener('places_changed', () => {
                const places = searchBox.getPlaces();

                if (!places || places.length === 0) {
                    return;
                }

                markers.forEach((marker) => marker.setMap(null));
                markers.length = 0;

                const bounds = new google.maps.LatLngBounds();

                places.forEach((place) => {
                    if (!place.geometry || !place.geometry.location) {
                        console.error('Returned place contains no geometry');
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
                console.error('Google Maps API loading failed:', error);
            });
    }, []);
console.log(selectedPlace, "selectedPlace");

    return (
        <div>
            <input
                ref={inputRef}
                type="text"
                placeholder="Search for a place"
                className="absolute top-2 left-2 z-10 w-80 p-2 border rounded-lg"
            />
            <div ref={mapRef} style={{ height: '500px', width: '100%' }}></div>

            {selectedPlace && (
                <>
                    <Reviews placeId={selectedPlace.place_id} />
                    {selectedPlace.geometry && selectedPlace.types && (
                        <NearbyPlaces
                            location={{
                                lat: selectedPlace?.geometry?.location?.lat() || 0,
                                lng: selectedPlace?.geometry?.location?.lng() || 0,
                            }}
                            types={selectedPlace.types}
                            rating={selectedPlace.rating || 0}
                        />
                    )}
                </>
            )}
        </div>
    );
};

export default MapSearchBox;
