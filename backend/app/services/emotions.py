from app.utils.nrc_lexicon import load_nrc_lexicon
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from collections import Counter

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
