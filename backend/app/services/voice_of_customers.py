from textblob import TextBlob
from collections import Counter
from nltk.tokenize import word_tokenize
import string

def extract_voc_insights(reviews, silent_killer_threshold=-0.2):
    """
    Extract Voice of the Customer (VoC) insights from reviews.
    
    Args:
        reviews (list): List of review texts.
        silent_killer_threshold (float): Sentiment score below which a review is categorized as a "Silent Killer."
    
    Returns:
        dict: Insights including pain points, delight factors, and silent killers.
    """
    # Initialize counters for themes
    pain_points = Counter()
    delight_factors = Counter()
    silent_killers = []

    # Preprocessing setup
    punctuation_table = str.maketrans("", "", string.punctuation)
    
    for review in reviews:
        # Perform sentiment analysis
        analysis = TextBlob(review)
        sentiment_score = analysis.sentiment.polarity
        
        # Tokenize and preprocess review text
        tokens = word_tokenize(review.lower())
        filtered_tokens = [word.translate(punctuation_table) for word in tokens if word.isalpha()]
        
        # Identify themes (noun phrases)
        noun_phrases = analysis.noun_phrases
        
        # Categorize based on sentiment
        if sentiment_score > 0.2:  # Positive sentiment
            delight_factors.update(noun_phrases)
        elif sentiment_score < -0.2:  # Negative sentiment
            pain_points.update(noun_phrases)
        elif sentiment_score < silent_killer_threshold:  # Silent killers
            silent_killers.append({
                "review": review,
                "sentiment_score": sentiment_score,
                "themes": noun_phrases
            })

    # Get top 5 frequent themes for each category
    top_pain_points = pain_points.most_common(5)
    top_delight_factors = delight_factors.most_common(5)
    
    return {
        "pain_points": [{"theme": theme, "count": count} for theme, count in top_pain_points],
        "delight_factors": [{"theme": theme, "count": count} for theme, count in top_delight_factors],
        "silent_killers": silent_killers  # Include full details for silent killers
    }
