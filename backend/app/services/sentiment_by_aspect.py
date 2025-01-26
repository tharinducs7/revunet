import spacy
from collections import defaultdict
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64

# Load SpaCy's English model
nlp = spacy.load("en_core_web_sm")

def aspect_based_sentiment_analysis(reviews):
    """
    Perform Aspect-Based Sentiment Analysis (ABSA) on reviews using SpaCy for aspect extraction.
    
    Args:
        reviews (list): List of review texts.
    
    Returns:
        dict: Sentiment scores grouped by aspect, including thresholds.
    """
    # Initialize results
    aspect_sentiments = defaultdict(list)

    for review in reviews:
        # Extract aspects (noun chunks) using SpaCy
        doc = nlp(review)
        aspects = [chunk.text.lower() for chunk in doc.noun_chunks]
        
        # Analyze sentiment for each aspect
        for aspect in aspects:
            sentiment_score = doc.sentiment
            aspect_sentiments[aspect].append(sentiment_score)
    
    # Aggregate results: Calculate average sentiment per aspect and classify them
    aspect_sentiment_summary = {
        aspect: {
            "average_sentiment": sum(scores) / len(scores),
            "mention_count": len(scores),
            "sentiment_category": categorize_sentiment(sum(scores) / len(scores))
        }
        for aspect, scores in aspect_sentiments.items()
    }

    return aspect_sentiment_summary

def categorize_sentiment(score):
    """
    Categorize sentiment score into human-readable labels.
    
    Args:
        score (float): Sentiment score.
    
    Returns:
        str: Sentiment category.
    """
    if score >= 0.5:
        return "Highly Positive"
    elif 0.1 <= score < 0.5:
        return "Positive"
    elif -0.1 <= score < 0.1:
        return "Neutral"
    elif -0.5 <= score < -0.1:
        return "Negative"
    else:
        return "Highly Negative"

def generate_bar_chart(aspect_summary):
    """
    Generate a bar chart as a base64-encoded image.
    
    Args:
        aspect_summary (dict): Summary of aspect sentiments.
    
    Returns:
        str: Base64-encoded image of the bar chart.
    """
    aspects = list(aspect_summary.keys())
    sentiment_scores = [aspect_summary[aspect]["average_sentiment"] for aspect in aspects]
    
    # Create a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(aspects, sentiment_scores, color="skyblue")
    plt.xlabel("Aspects")
    plt.ylabel("Average Sentiment")
    plt.title("Aspect Sentiment Scores")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    
    # Save the figure to a BytesIO object
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format="png", bbox_inches="tight")
    img_buffer.seek(0)
    plt.close()
    
    # Encode the image as base64
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
    return img_base64

def generate_word_cloud(aspect_summary):
    """
    Generate a word cloud as a base64-encoded image.
    
    Args:
        aspect_summary (dict): Summary of aspect sentiments.
    
    Returns:
        str: Base64-encoded image of the word cloud.
    """
    # Prepare data for the word cloud
    word_frequencies = {
        aspect: aspect_summary[aspect]["mention_count"] for aspect in aspect_summary
    }
    
    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(word_frequencies)
    
    # Save the figure to a BytesIO object
    img_buffer = io.BytesIO()
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(img_buffer, format="png", bbox_inches="tight")
    img_buffer.seek(0)
    plt.close()
    
    # Encode the image as base64
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
    return img_base64

# Main Function to Test
if __name__ == "__main__":
    # Sample Reviews
    reviews = [
        "The food was amazing, but the service was slow.",
        "I loved the ambiance and the food, but the service was terrible.",
        "The ambiance was wonderful, and the staff were very friendly.",
        "The food was cold, and the service was the worst I've experienced."
    ]
    
    # Perform Aspect-Based Sentiment Analysis
    results = aspect_based_sentiment_analysis(reviews)
    
    # Generate visualizations
    bar_chart_base64 = generate_bar_chart(results)
    word_cloud_base64 = generate_word_cloud(results)
    
    # Print base64 strings
    print("Bar Chart Base64:", bar_chart_base64[:100], "...")  # Truncated for readability
    print("Word Cloud Base64:", word_cloud_base64[:100], "...")

    # To verify in a local environment, save the base64 image as a file:
    with open("bar_chart.png", "wb") as f:
        f.write(base64.b64decode(bar_chart_base64))
    with open("word_cloud.png", "wb") as f:
        f.write(base64.b64decode(word_cloud_base64))
