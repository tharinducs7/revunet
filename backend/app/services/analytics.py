import io
import base64
from wordcloud import WordCloud
from collections import Counter
from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer

def generate_word_cloud(reviews):
    text = ' '.join(reviews)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    img = io.BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode('utf-8')

def frequent_phrases_analysis(reviews, top_n=5):
    compliments = Counter()
    complaints = Counter()

    for review in reviews:
        sentiment_score = TextBlob(review).sentiment.polarity
        blob = TextBlob(review)
        phrases = blob.noun_phrases

        if sentiment_score > 0:
            compliments.update(phrases)
        elif sentiment_score < 0:
            complaints.update(phrases)

    top_compliments = compliments.most_common(top_n)
    top_complaints = complaints.most_common(top_n)

    return {
        "top_compliments": [{"phrase": phrase, "count": count} for phrase, count in top_compliments],
        "top_complaints": [{"phrase": phrase, "count": count} for phrase, count in top_complaints]
    }

def most_common_words(reviews, n=10):
    text = ' '.join(reviews)
    vectorizer = CountVectorizer(stop_words='english')
    word_counts = vectorizer.fit_transform([text])
    word_freq = zip(vectorizer.get_feature_names_out(), word_counts.toarray()[0])
    sorted_words = sorted(word_freq, key=lambda x: x[1], reverse=True)[:n]
    return [{"word": word, "count": int(count)} for word, count in sorted_words]
