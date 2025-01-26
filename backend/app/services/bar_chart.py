import matplotlib
matplotlib.use('Agg')  # Non-GUI backend for Matplotlib

from matplotlib import pyplot as plt
import io
import base64

def get_relevant_aspects(aspect_summary):
    """
    Extract the top 3 most relevant aspects based on sentiment magnitude.

    Args:
        aspect_summary (dict): Summary of aspect sentiments.

    Returns:
        dict: Top 3 relevant aspects.
    """
    # Calculate relevance (e.g., absolute sentiment or frequency, if available)
    sorted_aspects = sorted(
        aspect_summary.items(),
        key=lambda x: abs(x[1]["average_sentiment"]),  # Sort by magnitude of sentiment
        reverse=True
    )

    # Get the top 3 relevant aspects
    top_aspects = dict(sorted_aspects[:3])
    return top_aspects

def generate_bar_chart(aspect_summary):
    """
    Generate a bar chart for the top 3 aspects as a base64-encoded image.

    Args:
        aspect_summary (dict): Summary of aspect sentiments.

    Returns:
        str: Base64-encoded image of the bar chart.
    """
    # Extract the top 3 aspects
    top_aspects = get_relevant_aspects(aspect_summary)

    # Prepare data for the bar chart
    aspects = list(top_aspects.keys())
    sentiment_scores = [top_aspects[aspect]["average_sentiment"] for aspect in aspects]

    # Create a bar chart
    plt.figure(figsize=(8, 5))
    plt.bar(aspects, sentiment_scores, color="skyblue")
    plt.xlabel("Aspects")
    plt.ylabel("Average Sentiment")
    plt.title("Top 3 Aspect Sentiment Scores")
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

def generate_aspect_summary(aspect_summary):
    """
    Generate a textual summary of the top 3 relevant aspects.

    Args:
        aspect_summary (dict): Summary of aspect sentiments.

    Returns:
        str: A ranked summary of the top 3 aspects with sentiment icons.
    """
    sentiment_icons = {
        "Positive": "😃",
        "Neutral": "😕",
        "Negative": "😡",
    }

    # Get the top 3 relevant aspects
    top_aspects = sorted(
        aspect_summary.items(),
        key=lambda x: abs(x[1]["average_sentiment"]),
        reverse=True
    )[:3]

    summary = "Top Aspects:\n"
    for rank, (aspect, data) in enumerate(top_aspects, 1):
        sentiment_score = data["average_sentiment"]
        category = (
            "Positive" if sentiment_score > 0.5 else
            "Neutral" if -0.5 <= sentiment_score <= 0.5 else
            "Negative"
        )
        summary += f"{rank}. {aspect}: {sentiment_icons[category]} ({category}, {sentiment_score:.2f})\n"

    return summary
