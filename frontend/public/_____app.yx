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
import numpy as np
import json
import spacy
from langdetect import detect, DetectorFactory
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import os

nlp = spacy.load("en_core_web_sm")
nltk.download("stopwords")
nltk.download("punkt")
DetectorFactory.seed = 0

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
# Google Maps API Setup
gmaps = googlemaps.Client(key='AIzaSyAIljBK9Z0_Z24gTwZAkxg6LYlKx19q3G0')

# Load the Restaurant Reviews CSV
file_path = './trip_res_reviews.csv'
reviews_df = pd.read_csv(file_path)

def load_nrc_lexicon():
    """
    Load the NRC Emotion Lexicon into a dictionary.

    Returns:
        dict: A dictionary where keys are words and values are lists of associated emotions.
    """
    # Define the path to the NRC Emotion Lexicon file
    file_path = "NRC-Emotion-Lexicon-Wordlevel-v0.92.txt"
    
    nrc_lexicon = {}
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Emotion Lexicon file not found at: {file_path}")
    
    with open(file_path, "r") as f:
        for line in f:
            # Skip empty lines or invalid lines
            if not line.strip() or len(line.strip().split("\t")) != 3:
                continue
            
            # Parse the line
            word, emotion, association = line.strip().split("\t")
            
            # Add to dictionary if the association is "1"
            if int(association) == 1:  # Only include words with an emotional association
                if word not in nrc_lexicon:
                    nrc_lexicon[word] = []
                nrc_lexicon[word].append(emotion)
    return nrc_lexicon

def detect_emotions(reviews):
    """
    Detect overall emotions from a set of reviews using the NRC Emotion Lexicon.

    Args:
        reviews (list): List of review texts.

    Returns:
        dict: Aggregated count of emotions detected across all reviews.
    """
    # Load the NRC Lexicon inside this function
    nrc_lexicon = load_nrc_lexicon()
    
    # Initialize emotion counter
    emotion_counts = Counter()
    
    # Preprocessing tools
    stop_words = set(stopwords.words("english"))
    punctuation_table = str.maketrans("", "", string.punctuation)
    
    for review in reviews:
        # Tokenize, remove stopwords and punctuation
        tokens = word_tokenize(review.lower())
        filtered_tokens = [word.translate(punctuation_table) for word in tokens if word not in stop_words]
        
        # Match words to emotions in the NRC lexicon
        for word in filtered_tokens:
            if word in nrc_lexicon:
                for emotion in nrc_lexicon[word]:
                    emotion_counts[emotion] += 1
    
    # Return aggregated emotion counts
    return dict(emotion_counts)

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

def language_detection_and_sentiment(reviews):
    """
    Detect the language of reviews and analyze sentiment for each language separately.
    
    Args:
        reviews (list): List of review texts.
    
    Returns:
        dict: Sentiment analysis results grouped by language.
    """
    analysis_results = defaultdict(list)  # Group results by language
    
    for review in reviews:
        try:
            # Detect language of the review
            language = detect(review)
            
            # Perform sentiment analysis
            sentiment_score = TextBlob(review).sentiment.polarity
            
            # Append the result to the language group
            analysis_results[language].append({
                "review": review,
                "sentiment_score": sentiment_score
            })
        except Exception as e:
            # Handle cases where language detection fails
            analysis_results["unknown"].append({
                "review": review,
                "error": str(e)
            })
    
    # Calculate average sentiment per language
    summary = {}
    for language, reviews_data in analysis_results.items():
        sentiments = [entry["sentiment_score"] for entry in reviews_data if "sentiment_score" in entry]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        summary[language] = {
            "average_sentiment": avg_sentiment,
            "reviews": reviews_data
        }
    
    return summary

def frequent_phrases_analysis(reviews, top_n=5):
    """
    Analyze frequent complaint and compliment phrases in reviews.
    
    Args:
        reviews (list): List of review texts.
        top_n (int): Number of top frequent phrases to extract.
    
    Returns:
        dict: Most frequent complaint and compliment phrases.
    """
    compliments = Counter()
    complaints = Counter()

    for review in reviews:
        # Analyze sentiment
        sentiment_score = TextBlob(review).sentiment.polarity
        
        # Extract noun phrases using TextBlob
        blob = TextBlob(review)
        phrases = blob.noun_phrases

        # Classify phrases as complaints or compliments based on sentiment
        if sentiment_score > 0:  # Positive sentiment
            compliments.update(phrases)
        elif sentiment_score < 0:  # Negative sentiment
            complaints.update(phrases)

    # Get top phrases
    top_compliments = compliments.most_common(top_n)
    top_complaints = complaints.most_common(top_n)

    return {
        "top_compliments": [{"phrase": phrase, "count": count} for phrase, count in top_compliments],
        "top_complaints": [{"phrase": phrase, "count": count} for phrase, count in top_complaints]
    }

def post_to_rapidapi(reviews):
    """
    Post Google reviews to RapidAPI for actionable recommendations for owners and customers.
    """
    url = "https://chatgpt-42.p.rapidapi.com/gpt4"
    
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
        "x-rapidapi-key": "b36b632ea3mshfba10ef37270d8fp1afd04jsn9e5f5e25573e__",
        "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        print("Raw RapidAPI Response:", response_data.get("status"))  # Debugging the API response

        # Extract the result key and parse it as JSON
        if response_data.get("status") and "result" in response_data:
            raw_result = response_data["result"]
            if isinstance(raw_result, str):
                try:
                    # Remove backticks and "json" tag if present
                    raw_result_cleaned = raw_result.strip("`").strip()
                    if raw_result_cleaned.startswith("json\n"):
                        raw_result_cleaned = raw_result_cleaned[5:].strip()

                    # Parse the cleaned JSON string
                    parsed_result = json.loads(raw_result_cleaned)
                    return parsed_result
                except json.JSONDecodeError as e:
                    print(f"JSON decoding error: {e}")
                    print("Raw result for debugging:", raw_result)
                    return {
                        "title": "Invalid JSON response",
                        "overall_aspect": "N/A",
                        "for_owners": [],
                        "for_customers": []
                    }
            else:
                return raw_result  # Already parsed
        else:
            print("API responded but status is False or 'result' key is missing.")
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

def combine_reviews(tripadvisor_reviews, google_reviews):
    """
    Combines TripAdvisor and Google reviews into one list with unique entries.
    """
    # Combine reviews from both sources
    combined_reviews = tripadvisor_reviews + google_reviews
    
    # Remove duplicates (optional, in case reviews overlap)
    combined_reviews = list(set(combined_reviews))
    
    return combined_reviews

def most_common_words(reviews, n=10):
    """
    Analyze the most common words in reviews.
    Returns a dictionary with words and their frequency.
    """
    text = ' '.join(reviews)
    vectorizer = CountVectorizer(stop_words='english')
    word_counts = vectorizer.fit_transform([text])
    word_freq = zip(vectorizer.get_feature_names_out(), word_counts.toarray()[0])
    sorted_words = sorted(word_freq, key=lambda x: x[1], reverse=True)[:n]
    return [{"word": word, "count": int(count)} for word, count in sorted_words]

# def negative_feedback_root_cause_analysis(reviews, sentiment_threshold=-0.5):
#     """
#     Analyze negative reviews and extract the root cause of negative feedback using dependency parsing.
    
#     Args:
#         reviews (list): List of review texts.
#         sentiment_threshold (float): Sentiment score below which a review is considered negative.
    
#     Returns:
#         list: Extracted root causes of negative reviews with subjects, verbs, and objects.
#     """
#     negative_reviews = []
    
#     for review in reviews:
#         # Analyze sentiment of the review
#         sentiment_score = TextBlob(review).sentiment.polarity
        
#         # If the sentiment score is below the threshold, analyze the review
#         if sentiment_score < sentiment_threshold:
#             # Parse the review text using spaCy
#             doc = nlp(review)
#             root_causes = []
            
#             for token in doc:
#                 # Look for the subject-verb-object structure
#                 if token.dep_ == "nsubj" and token.head.pos_ == "VERB":  # Subject linked to a verb
#                     subject = token.text
#                     verb = token.head.text
#                     object_ = " ".join([child.text for child in token.head.children if child.dep_ == "dobj"])
#                     root_causes.append({
#                         "subject": subject,
#                         "verb": verb,
#                         "object": object_ if object_ else None
#                     })
            
#             # Append results for this review
#             negative_reviews.append({
#                 "review": review,
#                 "sentiment_score": sentiment_score,
#                 "root_causes": root_causes
#             })
    
#     return negative_reviews

def review_length_analysis(reviews):
    """
    Analyze the length of reviews and categorize them.
    Returns the average length and counts of short, medium, and long reviews.
    """
    lengths = [len(review.split()) for review in reviews]
    short_reviews = len([l for l in lengths if l <= 20])
    medium_reviews = len([l for l in lengths if 21 <= l <= 50])
    long_reviews = len([l for l in lengths if l > 50])

    return {
        "average_length": sum(lengths) / len(lengths) if lengths else 0,
        "short_reviews": short_reviews,
        "medium_reviews": medium_reviews,
        "long_reviews": long_reviews
    }

def customer_retention_risk_analysis(reviews, threshold=-0.5):
    """
    Analyze customer reviews to identify retention risks based on negative sentiment.
    
    Args:
        reviews (list): List of customer reviews.
        threshold (float): Sentiment score below which a review is flagged as high risk.
    
    Returns:
        dict: Reviews categorized by risk levels (high, medium, low).
    """
    risk_analysis = {
        "high_risk": [],
        "medium_risk": [],
        "low_risk": []
    }
    
    for review in reviews:
        # Perform sentiment analysis
        sentiment_score = TextBlob(review).sentiment.polarity
        
        # Categorize risk levels
        if sentiment_score < threshold:
            risk_analysis["high_risk"].append({
                "review": review,
                "sentiment_score": sentiment_score,
                "risk_level": "High"
            })
        elif threshold <= sentiment_score < 0:
            risk_analysis["medium_risk"].append({
                "review": review,
                "sentiment_score": sentiment_score,
                "risk_level": "Medium"
            })
        else:
            risk_analysis["low_risk"].append({
                "review": review,
                "sentiment_score": sentiment_score,
                "risk_level": "Low"
            })
    
    return risk_analysis

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
    # "recommendations": recommendations,
    # Step 5: Generate word cloud for reviews
    word_cloud = generate_word_cloud(google_reviews)

    all_reviews = combine_reviews(tripadvisor_reviews, google_reviews)
    # Step 6: Return results
    return jsonify({
        "location_name": location_name,
        "google_sentiment": google_sentiment,
        "tripadvisor_sentiment": tripadvisor_sentiment,
        "overall_sentiment": overall_sentiment,
        "word_cloud": word_cloud,
        "most_common_words": most_common_words(all_reviews),
        "recommendations": recommendations,
        "frequent_phrases_analysis": frequent_phrases_analysis(all_reviews, top_n=3),
        "customer_retention_risk_analysis": customer_retention_risk_analysis(all_reviews, threshold=-0.5),
        "emotions": detect_emotions(all_reviews)
        #"language_detection_and_sentiment": language_detection_and_sentiment(all_reviews)
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
