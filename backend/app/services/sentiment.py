# DistilBERT-backed sentiment (keeps original return shape)
# -------------------------------------------------------------------
# Replaces TextBlob scoring with a batched transformer predictor.
# Loads your fine-tuned model from models/bert_sentiment if present,
# otherwise falls back to the base distilbert checkpoint.
# -------------------------------------------------------------------

from collections import Counter
from pathlib import Path
import os
import torch
from torch.nn.functional import softmax
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ---- Config ----
_MODEL_DIR = Path("models/bert_sentiment")   # your fine-tuned model directory
_HF_FALLBACK = "distilbert-base-uncased"     # fallback if no local model
_LABELS = ["Negative", "Neutral", "Positive"]
_ID2LAB = {0: "Negative", 1: "Neutral", 2: "Positive"}

# Optional: force CPU for inference to be memory-safe on Mac MPS
_USE_CPU_INFERENCE = True
_INFER_DEVICE = torch.device("cpu") if _USE_CPU_INFERENCE else (
    torch.device("cuda") if torch.cuda.is_available()
    else torch.device("mps") if torch.backends.mps.is_available()
    else torch.device("cpu")
)

# Lazy singletons
_tokenizer = None
_model = None


def _load_model_once():
    """Load tokenizer & model once (lazy)."""
    global _tokenizer, _model
    if _tokenizer is not None and _model is not None:
        return _tokenizer, _model

    if (_MODEL_DIR / "config.json").exists():
        # load your fine-tuned model
        _tokenizer = AutoTokenizer.from_pretrained(_MODEL_DIR.as_posix())
        _model = AutoModelForSequenceClassification.from_pretrained(_MODEL_DIR.as_posix())
    else:
        # fallback to base model (still works, but not fine-tuned on your data)
        _tokenizer = AutoTokenizer.from_pretrained(_HF_FALLBACK)
        _model = AutoModelForSequenceClassification.from_pretrained(_HF_FALLBACK, num_labels=3)

    _model.eval()
    _model.to(_INFER_DEVICE)
    return _tokenizer, _model


def _predict_batched(texts, batch_size=16, max_len=256):
    """
    Predict class-probs in small batches. Returns a list of dicts with
    keys: {'neg': p0, 'neu': p1, 'pos': p2} for each text.
    """
    tokenizer, model = _load_model_once()

    # ensure safe max length
    try:
        tokenizer.model_max_length = max_len
    except Exception:
        pass

    probs_out = []
    for i in range(0, len(texts), batch_size):
        chunk = [str(t) if t is not None else "" for t in texts[i:i + batch_size]]
        enc = tokenizer(chunk, truncation=True, padding=True, return_tensors='pt')
        enc = {k: v.to(_INFER_DEVICE) for k, v in enc.items()}
        with torch.no_grad():
            logits = model(**enc).logits  # [B, 3]
            ps = softmax(logits, dim=-1).cpu().numpy()
        for row in ps:
            # map to consistent keys (neg, neu, pos)
            probs_out.append({
                "neg": float(row[0]),
                "neu": float(row[1]),
                "pos": float(row[2]),
            })
        # free
        del enc, logits
        if torch.backends.mps.is_available():
            try:
                torch.mps.empty_cache()
            except Exception:
                pass

    return probs_out


def analyze_sentiment(reviews):
    """
    DistilBERT-based sentiment analysis.

    Args:
        reviews (list[str])

    Returns:
        dict with keys:
        - average_sentiment (float in [-1, 1])
        - avg_star_count (float in [0, 5])
        - sentiment_category_group (dict counts per {Positive, Neutral, Negative})
        - detailed_sentiments (list of {review_text, sentiment_score, sentiment_category})
    """
    if not reviews:
        return {
            "average_sentiment": 0.0,
            "avg_star_count": 2.5,
            "sentiment_category_group": {"Positive": 0, "Neutral": 0, "Negative": 0},
            "detailed_sentiments": []
        }

    # Predict
    probs = _predict_batched(reviews, batch_size=16, max_len=256)

    detailed = []
    cats = []
    scores = []

    for text, p in zip(reviews, probs):
        # decision: argmax
        if p["pos"] >= p["neu"] and p["pos"] >= p["neg"]:
            cat = "Positive"
        elif p["neu"] >= p["pos"] and p["neu"] >= p["neg"]:
            cat = "Neutral"
        else:
            cat = "Negative"

        # continuous sentiment score in [-1, 1] using (p_pos - p_neg)
        score = float(p["pos"] - p["neg"])

        detailed.append({
            "review_text": text,
            "sentiment_score": score,
            "sentiment_category": cat
        })
        cats.append(cat)
        scores.append(score)

    # aggregate
    avg_sentiment = float(sum(scores) / max(1, len(scores)))  # [-1,1]
    # map score to 0..5 stars (as original code did: (score+1)*2.5 )
    avg_star_count = float((avg_sentiment + 1.0) * 2.5)

    sentiment_category_group = dict(Counter(cats))

    return {
        "average_sentiment": avg_sentiment,
        "avg_star_count": avg_star_count,
        "sentiment_category_group": sentiment_category_group,
        "detailed_sentiments": detailed
    }
