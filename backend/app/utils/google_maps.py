import googlemaps

gmaps = googlemaps.Client(key='AIzaSyAIljBK9Z0_Z24gTwZAkxg6LYlKx19q3G0')

def fetch_google_reviews(location_id):
    try:
        place_details = gmaps.place(place_id=location_id, fields=['name', 'reviews'])
        reviews = [review['text'] for review in place_details['result'].get('reviews', [])]
        location_name = place_details['result']['name']
        return location_name, reviews
    except Exception as e:
        print(f"Error fetching Google reviews: {e}")
        return None, []
