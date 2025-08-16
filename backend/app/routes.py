from flask import Blueprint, jsonify, request
from app.services.sentiment import analyze_sentiment
from app.services.reviews import fetch_google_reviews, fetch_tripadvisor_reviews
from app.services.sentiment_by_aspect import aspect_based_sentiment_analysis
from app.services.bar_chart import generate_aspect_summary
from app.services.recommendations import post_to_rapidapi, post_comparison_to_rapidapi
from app.services.analytics import generate_word_cloud, frequent_phrases_analysis
from app.utils.helpers import combine_reviews
from app.services.emotions import detect_emotions, post_emotions_to_chatgpt

main_bp = Blueprint('main', __name__)

@main_bp.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    location_id = data.get('location_id')
    if not location_id:
        return jsonify({"error": "location_id is required"}), 400

    location_name, google_reviews = fetch_google_reviews(location_id)
    if not google_reviews:
        return jsonify({"error": "No reviews found for the given location ID"}), 404

    # Clean reviews
    google_reviews = [str(review) if review is not None else "" for review in google_reviews]
    tripadvisor_reviews = fetch_tripadvisor_reviews(location_name)

    google_sentiment = analyze_sentiment(google_reviews)
    overall_sentiment = google_sentiment['average_sentiment']
    if tripadvisor_reviews:
        tripadvisor_sentiment = analyze_sentiment(tripadvisor_reviews)
        overall_sentiment = (google_sentiment['average_sentiment'] + tripadvisor_sentiment['average_sentiment']) / 2
    else:
        tripadvisor_sentiment = {"average_sentiment": 0, "detailed_sentiments": []}
        overall_sentiment = google_sentiment['average_sentiment']
    
    all_reviews = combine_reviews(tripadvisor_reviews, google_reviews)

    emotions = detect_emotions(all_reviews)
    recommendations = post_to_rapidapi(google_reviews)
    word_cloud = generate_word_cloud(all_reviews)
    aspect_results = aspect_based_sentiment_analysis(all_reviews)
    summary_ascepct = generate_aspect_summary(aspect_results)
    aspect_word_cloud_base64 = generate_word_cloud(aspect_results)
    what_emotions_says = post_emotions_to_chatgpt(emotions)

    return jsonify({
        "aspect_analysis": {
            "summary": aspect_results,
            "summary_ascepct": summary_ascepct,
            "word_cloud": aspect_word_cloud_base64
        },
        "location_name": location_name,
        "google_sentiment": google_sentiment,
        "tripadvisor_sentiment": tripadvisor_sentiment,
        "overall_sentiment": overall_sentiment,
        "word_cloud": word_cloud,
        "recommendations": recommendations,
        "frequent_phrases_analysis": frequent_phrases_analysis(all_reviews),
        "emotions": emotions,
        "what_emotions_says": what_emotions_says,
    })

@main_bp.route('/compare', methods=['POST'])
def compare():
    data = request.json
    location_id1 = data.get('location_id1')
    location_id2 = data.get('location_id2')
    print(location_id1, location_id2)
    if not location_id1 or not location_id2:
        return jsonify({"error": "Both location_id1 and location_id2 are required"}), 400

    
    location_name1, google_reviews1 = fetch_google_reviews(location_id1)
    if not google_reviews1:
        return jsonify({"error": f"No reviews found for location_id1: {location_id1}"}), 404

    tripadvisor_reviews1 = fetch_tripadvisor_reviews(location_name1)
    all_reviews1 = combine_reviews(tripadvisor_reviews1, google_reviews1)

    
    location_name2, google_reviews2 = fetch_google_reviews(location_id2)
    if not google_reviews2:
        return jsonify({"error": f"No reviews found for location_id2: {location_id2}"}), 404

    tripadvisor_reviews2 = fetch_tripadvisor_reviews(location_name2)
    all_reviews2 = combine_reviews(tripadvisor_reviews2, google_reviews2)

    
    comparison_result = post_comparison_to_rapidapi(
        reviews1=all_reviews1,
        reviews2=all_reviews2,
        location_name1=location_name1,
        location_name2=location_name2
    )

    
    google_sentiment1 = analyze_sentiment(google_reviews1)
    overall_sentiment1 = google_sentiment1['average_sentiment']
    if tripadvisor_reviews1:
        tripadvisor_sentiment1 = analyze_sentiment(tripadvisor_reviews1)
        overall_sentiment1 = (google_sentiment1['average_sentiment'] + tripadvisor_sentiment1['average_sentiment']) / 2
    emotions1 = detect_emotions(all_reviews1)
    what_emotions_says1 = post_emotions_to_chatgpt(emotions1)

    google_sentiment2 = analyze_sentiment(google_reviews2)
    overall_sentiment2 = google_sentiment2['average_sentiment']
    if tripadvisor_reviews2:
        tripadvisor_sentiment2 = analyze_sentiment(tripadvisor_reviews2)
        overall_sentiment2 = (google_sentiment2['average_sentiment'] + tripadvisor_sentiment2['average_sentiment']) / 2
    emotions2 = detect_emotions(all_reviews2)
    what_emotions_says2 = post_emotions_to_chatgpt(emotions2)

    
    comparison_result["location1"] = {
        "name": location_name1,
        "google_sentiment": google_sentiment1,
        "overall_sentiment": overall_sentiment1,
        "emotions": emotions1,
        "what_emotions_says1": what_emotions_says1
    }
    comparison_result["location2"] = {
        "name": location_name2,
        "google_sentiment": google_sentiment2,
        "overall_sentiment": overall_sentiment2,
        "emotions": emotions2,
        "what_emotions_says2": what_emotions_says2
    }

    return jsonify(comparison_result)
