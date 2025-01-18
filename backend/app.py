from flask import Flask, request, jsonify
import pandas as pd
import requests
from textblob import TextBlob
import googlemaps
from fuzzywuzzy import process
from sklearn.feature_extraction.text import CountVectorizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
from collections import Counter
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
# Google Maps API Setup
gmaps = googlemaps.Client(key='AIzaSyAIljBK9Z0_Z24gTwZAkxg6LYlKx19q3G0')

# Load the Restaurant Reviews CSV
file_path = './trip_res_reviews.csv'
reviews_df = pd.read_csv(file_path)

def analyze_sentiment(reviews):
    """
    Perform sentiment analysis on a list of reviews.
    Returns average sentiment score, average star count, and detailed scores.
    Also returns a count of reviews by sentiment category.
    """
    sentiments = []
    sentiment_categories = []
    
    for review in reviews:
        analysis = TextBlob(review)
        sentiment_score = analysis.sentiment.polarity
        
        # Determine sentiment category
        if sentiment_score > 0.5:
            sentiment_category = "Positive"
        elif -0.5 <= sentiment_score <= 0.5:
            sentiment_category = "Neutral"
        else:
            sentiment_category = "Negative"
        
        sentiment_categories.append(sentiment_category)
        sentiments.append({
            "review_text": review,
            "sentiment_score": sentiment_score,
            "sentiment_category": sentiment_category
        })
    
    # Calculate average sentiment score
    avg_sentiment = sum([s['sentiment_score'] for s in sentiments]) / len(sentiments) if sentiments else 0
    
    # Calculate star count (map sentiment score to star rating out of 5)
    star_counts = [(s['sentiment_score'] + 1) * 2.5 for s in sentiments]  # Map -1 to 1 range to 0 to 5
    avg_star_count = sum(star_counts) / len(star_counts) if star_counts else 0

    # Aggregate sentiment category counts
    sentiment_category_group = Counter(sentiment_categories)
    
    return {
        'average_sentiment': avg_sentiment,
        'avg_star_count': avg_star_count,
        'sentiment_category_group': dict(sentiment_category_group),
        'detailed_sentiments': sentiments
    }
    
def fetch_google_reviews(location_id):
    """
    Fetch reviews for a location using Google Places API.
    """
    try:
        place_details = gmaps.place(place_id=location_id, fields=['name', 'reviews'])
        reviews = [review['text'] for review in place_details['result'].get('reviews', [])]
        location_name = place_details['result']['name']
        return location_name, reviews
    except Exception as e:
        print(f"Error fetching Google reviews: {e}")
        return None, []

def fetch_tripadvisor_reviews(restaurant_name):
    """
    Fetch reviews for a restaurant from TripAdvisor CSV using fuzzy matching.
    """
    try:
        match = process.extractOne(restaurant_name, reviews_df['Restaurant'].tolist())
        if match and match[1] > 80:  # Match confidence threshold
            matched_name = match[0]
            tripadvisor_reviews = reviews_df[reviews_df['Restaurant'] == matched_name]['Review'].tolist()
            return tripadvisor_reviews
        return []
    except Exception as e:
        print(f"Error fetching TripAdvisor reviews: {e}")
        return []

def generate_word_cloud(reviews):
    """
    Generate a word cloud image from reviews.
    """
    text = ' '.join(reviews)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    img = io.BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    return img_base64

# def post_to_rapidapi(reviews):
#     """
#     Post Google reviews to RapidAPI for actionable recommendations for owners and customers.
#     """
#     url = "https://chatgpt-42.p.rapidapi.com/chatgpt"
    
#     # Detailed prompt for recommendations
#     content = (
#         f"Based on the following reviews:\n\n{reviews}\n\n"
#         "Provide actionable recommendations for improvement (owners) and highlight insights for customers."
#         "Separate recommendations for owners and customers clearly."
#     )
    
#     payload = {
#         "messages": [
#             {
#                 "role": "user",
#                 "content": content
#             }
#         ],
#         "web_access": False
#     }
#     headers = {
#         "x-rapidapi-key": "9d443f0279mshdebd82de2c89274p1c4e01jsn4b7d142ea901",
#         "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
#         "Content-Type": "application/json"
#     }
    
#     try:
#         response = requests.post(url, json=payload, headers=headers)
#         response_data = response.json()
#         print("Raw RapidAPI Response:", response_data)  # Debugging the API response
#         return response_data
#     except Exception as e:
#         print(f"Error posting to RapidAPI: {e}")
#         return {
#             "owners": ["Failed to fetch recommendations from RapidAPI."],
#             "customers": ["Failed to fetch insights from RapidAPI."]
#         }
import json  # Import the JSON module to parse JSON strings

def post_to_rapidapi(reviews):
    """
    Post Google reviews to RapidAPI for actionable recommendations for owners and customers.
    """
    url = "https://chatgpt-42.p.rapidapi.com/chatgpt"
    
    # Prompt the AI to return recommendations in JSON format
    content = (
        f"Based on the following reviews:\n\n{reviews}\n\n"
        "Provide actionable recommendations in JSON format as follows:\n\n"
        "{\n"
        "  \"title\": \"A summary title\",\n"
        "  \"overall_aspect\": \"A summary of overall insights and improvements\",\n"
        "  \"for_owners\": [\n"
        "    {\n"
        "      \"title\": \"Title of the recommendation for owners\",\n"
        "      \"recommendation\": \"The specific recommendation for improvement\",\n"
        "      \"priority\": \"High/Medium/Low\"\n"
        "    },\n"
        "    ...\n"
        "  ],\n"
        "  \"for_customers\": [\n"
        "    {\n"
        "      \"title\": \"Title of the insight for customers\",\n"
        "      \"insights\": \"The specific insight for customers\"\n"
        "    },\n"
        "    ...\n"
        "  ]\n"
        "}\n\n"
        "Make sure the response strictly follows this JSON structure. only send 5 Recomendations, in recomendations mention that reviews mentioned this issue like wise for owners"
    )
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "web_access": False
    }
    headers = {
        "x-rapidapi-key": "9d443f0279mshdebd82de2c89274p1c4e01jsn4b7d142ea901",
        "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        print("Raw RapidAPI Response:", response_data)  # Debugging the API response

        # Extract the result key and parse it as JSON
        if response_data.get("status"):
            raw_result = response_data.get("result", "{}")
            parsed_result = json.loads(raw_result)  # Convert JSON string to a Python dictionary
            return parsed_result
        else:
            return {
                "title": "Failed to fetch recommendations",
                "overall_aspect": "N/A",
                "for_owners": [],
                "for_customers": []
            }
    except Exception as e:
        print(f"Error posting to RapidAPI: {e}")
        return {
            "title": "Failed to fetch recommendations",
            "overall_aspect": "N/A",
            "for_owners": [],
            "for_customers": []
        }

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyze reviews and provide recommendations based on input Google location ID.
    """
    data = request.json
    location_id = data.get('location_id')
    if not location_id:
        return jsonify({"error": "location_id is required"}), 400

    # Step 1: Fetch Google reviews
    location_name, google_reviews = fetch_google_reviews(location_id)
    if not google_reviews:
        return jsonify({"error": "No reviews found for the given location ID"}), 404

    # Step 2: Check if location exists in TripAdvisor dataset
    tripadvisor_reviews = fetch_tripadvisor_reviews(location_name)

    # Step 3: Perform sentiment analysis
    google_sentiment = analyze_sentiment(google_reviews)
    if tripadvisor_reviews:
        tripadvisor_sentiment = analyze_sentiment(tripadvisor_reviews)
        overall_sentiment = (google_sentiment['average_sentiment'] + tripadvisor_sentiment['average_sentiment']) / 2
    else:
        tripadvisor_sentiment = {"average_sentiment": 0, "detailed_sentiments": []}
        overall_sentiment = google_sentiment['average_sentiment']

    # Step 4: Get recommendations from RapidAPI
    recommendations = post_to_rapidapi(google_reviews)

    # Step 5: Generate word cloud for reviews
    word_cloud = generate_word_cloud(google_reviews)

    # Step 6: Return results
    return jsonify({
        "location_name": location_name,
        "google_sentiment": google_sentiment,
        "tripadvisor_sentiment": tripadvisor_sentiment,
        "overall_sentiment": overall_sentiment,
        "recommendations": recommendations,
        "word_cloud": word_cloud
    })

@app.route('/compare', methods=['POST'])
def compare():
    """
    Compare the sentiment of the location with nearby competitors.
    """
    data = request.json
    location_id = data.get('location_id')
    radius = data.get('radius', 5000)  # Default radius: 5 km

    if not location_id:
        return jsonify({"error": "location_id is required"}), 400

    # Fetch the location details
    location_details = gmaps.place(place_id=location_id, fields=['geometry', 'name'])
    if not location_details:
        return jsonify({"error": "Invalid location ID"}), 404

    location_coords = location_details['result']['geometry']['location']

    # Search nearby places
    nearby_places = gmaps.places_nearby(
        location=(location_coords['lat'], location_coords['lng']),
        radius=radius,
        type='restaurant'
    )

    competitor_data = []
    for place in nearby_places['results']:
        competitor_name = place['name']
        competitor_reviews = fetch_google_reviews(place['place_id'])[1]
        sentiment = analyze_sentiment(competitor_reviews)
        competitor_data.append({
            "name": competitor_name,
            "average_sentiment": sentiment['average_sentiment']
        })

    return jsonify({
        "competitors": competitor_data
    })

@app.route('/word-cloud', methods=['POST'])
def word_cloud():
    """
    Generate a word cloud image for a given list of reviews.
    """
    data = request.json
    reviews = data.get('reviews', [])

    if not reviews:
        return jsonify({"error": "Reviews are required"}), 400

    word_cloud_img = generate_word_cloud(reviews)

    return jsonify({
        "word_cloud": word_cloud_img
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
