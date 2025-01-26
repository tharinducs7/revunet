from textblob import TextBlob
from collections import Counter

def analyze_sentiment(reviews):
    sentiments = []
    sentiment_categories = []

    for review in reviews:
        analysis = TextBlob(review)
        sentiment_score = analysis.sentiment.polarity
        sentiment_category = (
            "Positive" if sentiment_score > 0.5 else
            "Neutral" if -0.5 <= sentiment_score <= 0.5 else
            "Negative"
        )
        sentiment_categories.append(sentiment_category)
        sentiments.append({
            "review_text": review,
            "sentiment_score": sentiment_score,
            "sentiment_category": sentiment_category
        })

    avg_sentiment = sum(s['sentiment_score'] for s in sentiments) / len(sentiments)
    star_counts = [(s['sentiment_score'] + 1) * 2.5 for s in sentiments]
    avg_star_count = sum(star_counts) / len(star_counts)

    sentiment_category_group = Counter(sentiment_categories)

    return {
        'average_sentiment': avg_sentiment,
        'avg_star_count': avg_star_count,
        'sentiment_category_group': dict(sentiment_category_group),
        'detailed_sentiments': sentiments
    }
