# train_distilbert_sentiment.py
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)
import torch
from datasets import Dataset

# --------------------------
# 1) Load & prepare dataset
# --------------------------
DATA_PATH = "trip_res_reviews.csv"   # <-- your CSV file
SAVE_DIR  = "models/bert_sentiment" # <-- output folder

assert os.path.exists(DATA_PATH), f"CSV not found at {DATA_PATH}"
df = pd.read_csv(DATA_PATH).dropna(subset=["Review", "Rating"]).copy()
df["Review"] = df["Review"].astype(str).str.strip()

# Convert ratings → labels
def rating_to_label(r):
    r = float(r)
    if r >= 4: return "pos"
    if r <= 2: return "neg"
    return "neu"

df["label"] = pd.to_numeric(df["Rating"], errors="coerce").dropna().apply(rating_to_label)
df = df.dropna(subset=["label"]).reset_index(drop=True)

# Map labels to integers
label2id = {"neg":0, "neu":1, "pos":2}
id2label = {v:k for k,v in label2id.items()}
df["label_id"] = df["label"].map(label2id)

# Train/validation split
train_texts, val_texts, train_labels, val_labels = train_test_split(
    df["Review"].tolist(),
    df["label_id"].tolist(),
    test_size=0.2,
    stratify=df["label_id"],
    random_state=42
)

# --------------------------
# 2) Tokenization
# --------------------------
tok = AutoTokenizer.from_pretrained("distilbert-base-uncased")

train_ds = Dataset.from_dict({"text": train_texts, "label": train_labels})
val_ds   = Dataset.from_dict({"text": val_texts, "label": val_labels})

def tokenize(batch):
    return tok(batch["text"], padding="max_length", truncation=True, max_length=128)

train_ds = train_ds.map(tokenize, batched=True)
val_ds   = val_ds.map(tokenize, batched=True)

train_ds.set_format("torch", columns=["input_ids", "attention_mask", "label"])
val_ds.set_format("torch", columns=["input_ids", "attention_mask", "label"])

# --------------------------
# 3) Model
# --------------------------
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=3,
    id2label=id2label,
    label2id=label2id
)

# --------------------------
# 4) Training
# --------------------------
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=2,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=50,
    save_total_limit=1,
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
)

def compute_metrics(eval_pred):
    from sklearn.metrics import accuracy_score, f1_score
    logits, labels = eval_pred
    preds = logits.argmax(-1)
    acc = accuracy_score(labels, preds)
    f1m = f1_score(labels, preds, average="macro")
    return {"accuracy": acc, "macro_f1": f1m}

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_ds,
    eval_dataset=val_ds,
    tokenizer=tok,
    compute_metrics=compute_metrics,
)

trainer.train()

# --------------------------
# 5) Save model
# --------------------------
model.save_pretrained(SAVE_DIR)
tok.save_pretrained(SAVE_DIR)
print(f"[✅] Model saved to {SAVE_DIR}")
