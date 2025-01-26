import googlemaps
from fuzzywuzzy import process
import pandas as pd

gmaps = googlemaps.Client(key='AIzaSyAIljBK9Z0_Z24gTwZAkxg6LYlKx19q3G0')
file_path = './trip_res_reviews.csv'
reviews_df = pd.read_csv(file_path)

def fetch_google_reviews(location_id):
    try:
        place_details = gmaps.place(place_id=location_id, fields=['name', 'reviews'])
        reviews = [review['text'] for review in place_details['result'].get('reviews', [])]
        location_name = place_details['result']['name']
        return location_name, reviews
    except Exception as e:
        print(f"Error fetching Google reviews: {e}")
        return None, []

def fetch_tripadvisor_reviews(restaurant_name):
    try:
        match = process.extractOne(restaurant_name, reviews_df['Restaurant'].tolist())
        if match and match[1] > 80:
            matched_name = match[0]
            tripadvisor_reviews = reviews_df[reviews_df['Restaurant'] == matched_name]['Review'].tolist()
            return tripadvisor_reviews
        return []
    except Exception as e:
        print(f"Error fetching TripAdvisor reviews: {e}")
        return []
