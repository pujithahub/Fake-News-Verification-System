import os
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "fake_news_pipeline.joblib")

def predict_news(text):
    if not os.path.exists(MODEL_PATH):
        return None
    model = joblib.load(MODEL_PATH)
    label = model.predict([text])[0]
    confidence = None
    if hasattr(model, "predict_proba"):
        confidence = round(float(max(model.predict_proba([text])[0])) * 100, 1)
    return {"label": str(label).upper(), "confidence": confidence}
