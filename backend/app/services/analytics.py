import io
import os
import re
import base64
from collections import Counter
from pathlib import Path

import numpy as np
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ---------------- DistilBERT loader (lazy singletons) ----------------
_BERT_DIR = Path("models/bert_sentiment")
_FALLBACK = "distilbert-base-uncased"   # only used if local fine-tuned model not found
_USE_CPU_INFERENCE = True               # avoids MPS/GPU OOM on Macs

_tokenizer = None
_model = None
_infer_device = torch.device("cpu") if _USE_CPU_INFERENCE else (
    torch.device("cuda") if torch.cuda.is_available()
    else torch.device("mps") if torch.backends.mps.is_available()
    else torch.device("cpu")
)

def _load_bert_once():
    global _tokenizer, _model
    if _tokenizer is not None and _model is not None:
        return _tokenizer, _model

    if (_BERT_DIR / "config.json").exists():
        _tokenizer = AutoTokenizer.from_pretrained(_BERT_DIR.as_posix())
        _model = AutoModelForSequenceClassification.from_pretrained(_BERT_DIR.as_posix())
    else:
        # still works, but not fine-tuned on your data
        _tokenizer = AutoTokenizer.from_pretrained(_FALLBACK)
        _model = AutoModelForSequenceClassification.from_pretrained(_FALLBACK, num_labels=3)

    _model.eval()
    _model.to(_infer_device)
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["WANDB_DISABLED"] = "true"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    os.environ["DISABLE_TQDM"] = "1"
    return _tokenizer, _model

def _bert_predict_labels(texts, batch_size=16, max_len=256):
    """
    Returns a list of string labels: 'pos' | 'neu' | 'neg'
    """
    tok, mdl = _load_bert_once()
    preds = []
    try:
        tok.model_max_length = max_len
    except Exception:
        pass

    for i in range(0, len(texts), batch_size):
        chunk = [str(t) if t is not None else "" for t in texts[i:i+batch_size]]
        enc = tok(chunk, truncation=True, padding=True, return_tensors='pt')
        enc = {k: v.to(_infer_device) for k, v in enc.items()}
        with torch.no_grad():
            logits = mdl(**enc).logits
            ids = logits.argmax(dim=-1).cpu().numpy().tolist()
        preds.extend(ids)
        del enc, logits
        if torch.backends.mps.is_available():
            try:
                torch.mps.empty_cache()
            except Exception:
                pass

    id2label = {0: 'neg', 1: 'neu', 2: 'pos'}
    return [id2label[int(i)] for i in preds]

# ---------------- Existing features ----------------
def generate_word_cloud(reviews):
    text = ' '.join(map(str, reviews))
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    img = io.BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode('utf-8')

def most_common_words(reviews, n=10):
    text = ' '.join(map(str, reviews))
    vectorizer = CountVectorizer(stop_words='english')
    word_counts = vectorizer.fit_transform([text])
    word_freq = zip(vectorizer.get_feature_names_out(), word_counts.toarray()[0])
    sorted_words = sorted(word_freq, key=lambda x: x[1], reverse=True)[:n]
    return [{"word": w, "count": int(c)} for w, c in sorted_words]

# ---------------- Replaced TextBlob logic with BERT ----------------
def _clean_for_ngrams(s: str) -> str:
    s = re.sub(r"http\S+", " ", s)
    s = re.sub(r"[^A-Za-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s

def _top_phrases_ngram(docs, top_n=5):
    """
    Fallback phrase extractor: top 1–2 gram phrases using CountVectorizer.
    """
    if not docs:
        return []
    vec = CountVectorizer(stop_words='english', ngram_range=(1,2), min_df=1, max_features=5000)
    X = vec.fit_transform([_clean_for_ngrams(t) for t in docs])
    sums = np.asarray(X.sum(axis=0)).ravel()
    vocab = np.array(vec.get_feature_names_out())
    order = np.argsort(-sums)[:top_n]
    return [(vocab[i], int(sums[i])) for i in order]

def frequent_phrases_analysis(reviews, top_n=5, use_spacy=False):
    """
    Uses DistilBERT to split reviews into positive vs negative buckets,
    then extracts top phrases from each bucket.

    If use_spacy=True and spaCy is installed with en_core_web_sm,
    we extract noun chunks; otherwise we fall back to 1–2 gram phrases.
    """
    if not reviews:
        return {"top_compliments": [], "top_complaints": []}

    labels = _bert_predict_labels(reviews)
    pos_docs = [r for r, lab in zip(reviews, labels) if lab == 'pos']
    neg_docs = [r for r, lab in zip(reviews, labels) if lab == 'neg']

    # spaCy noun-chunk extraction (optional)
    if use_spacy:
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            def noun_chunks(docs):
                counts = Counter()
                for d in docs:
                    for nc in nlp(str(d)).noun_chunks:
                        phrase = re.sub(r"\s+", " ", nc.text.strip().lower())
                        if 2 <= len(phrase) <= 80:
                            counts[phrase] += 1
                return counts.most_common(top_n)
            pos_phr = noun_chunks(pos_docs)
            neg_phr = noun_chunks(neg_docs)
        except Exception:
            # fallback to n-grams if spaCy not available
            pos_phr = _top_phrases_ngram(pos_docs, top_n=top_n)
            neg_phr = _top_phrases_ngram(neg_docs, top_n=top_n)
    else:
        pos_phr = _top_phrases_ngram(pos_docs, top_n=top_n)
        neg_phr = _top_phrases_ngram(neg_docs, top_n=top_n)

    return {
        "top_compliments": [{"phrase": p, "count": c} for p, c in pos_phr],
        "top_complaints":  [{"phrase": p, "count": c} for p, c in neg_phr]
    }
