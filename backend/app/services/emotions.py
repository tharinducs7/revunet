from app.utils.nrc_lexicon import load_nrc_lexicon
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from collections import Counter
import requests
import json

def detect_emotions(reviews):
    """
    Detect emotions in a list of reviews using the NRC Emotion Lexicon.

    Args:
        reviews (list): List of review texts.

    Returns:
        dict: Emotion counts aggregated across all reviews.
    """
    nrc_lexicon = load_nrc_lexicon()
    emotion_counts = Counter()
    stop_words = set(stopwords.words("english"))
    punctuation_table = str.maketrans("", "", string.punctuation)

    for review in reviews:
        tokens = word_tokenize(review.lower())
        filtered_tokens = [word.translate(punctuation_table) for word in tokens if word not in stop_words]
        for word in filtered_tokens:
            if word in nrc_lexicon:
                for emotion in nrc_lexicon[word]:
                    emotion_counts[emotion] += 1

    return dict(emotion_counts)

def post_emotions_to_chatgpt(emotions):
    """
    Sends emotions data to ChatGPT via RapidAPI and generates a summary of customer sentiments.

    Args:
        emotions (dict): Emotion counts aggregated across customer reviews.

    Returns:
        str: A paragraph summarizing customer sentiments toward the business.
    """
    url = "https://chatgpt-42.p.rapidapi.com/gpt4"
    prompt = (
        f"The following emotion analysis was detected from customer reviews:\n\n"
        f"{emotions}\n\n"
        f"Based on this data, summarize how customers currently feel about the business. "
        f"Focus on key aspects customers are highlighting and provide a brief analysis. "
        f"Write the summary in simple, clear English."
    )
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "web_access": False
    }
    headers = {
        "x-rapidapi-key": "b36b632ea3mshfba10ef37270d8fp1afd04jsn9e5f5e25573e",
        "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        if response_data.get("status") and "result" in response_data:
            return response_data["result"]
        else:
            print("API responded but status is False or 'result' key is missing.")
            return "Unable to generate a summary. Please try again later."

    except Exception as e:
        print(f"Error posting to RapidAPI: {e}")
        return "Failed to connect to the API. Please check your setup."