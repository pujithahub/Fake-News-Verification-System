import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "training_news.csv")
MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "fake_news_pipeline.joblib")

def main():
    if not os.path.exists(CSV_PATH):
        raise SystemExit("Missing data/training_news.csv. Read README.md for the required format.")
    df = pd.read_csv(CSV_PATH).dropna(subset=["text", "label"])
    df["label"] = df["label"].astype(str).str.upper().str.strip()
    df = df[df["label"].isin(["REAL", "FAKE"])]
    if len(df) < 10 or df["label"].nunique() < 2:
        raise SystemExit("Add at least 10 labelled examples and include both REAL and FAKE.")
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"].astype(str), df["label"], test_size=0.25,
        random_state=42, stratify=df["label"]
    )
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=10000)),
        ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced"))
    ])
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)
    print("Test accuracy:", round(accuracy_score(y_test, predictions), 3))
    print(classification_report(y_test, predictions, zero_division=0))
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print("Saved model to:", MODEL_PATH)

if __name__ == "__main__":
    main()
