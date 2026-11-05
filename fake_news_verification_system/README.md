# Fake News Verification System Using Machine Learning

A beginner-friendly Flask + SQLite + scikit-learn college project.

## Features
- User registration and login
- Admin login and verified-news record management
- Checks submitted text against admin records
- TF-IDF + Logistic Regression text classifier
- Shows VERIFIED NEWS, LIKELY FAKE, or UNVERIFIED NEWS

## Requirements
Python 3.10 or newer is recommended.

## Run the project (Windows PowerShell)
1. Open this folder in VS Code.
2. Open Terminal > New Terminal.
3. Create a virtual environment:
   `python -m venv venv`
4. Activate it:
   `.\venv\Scripts\Activate.ps1`
   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate again.
5. Install packages:
   `pip install -r requirements.txt`
6. Train the model:
   `python train_model.py`
7. Start the website:
   `python app.py`
8. Open `http://127.0.0.1:5000` in your browser.

## Demo admin
Username: `admin`
Password: `Admin@123`

Change the demo password and secret key before any public deployment. This is a classroom demo, not a production security setup.

## Training data
The included `data/training_news.csv` contains only a tiny illustrative dataset to demonstrate the training pipeline. It is NOT a reliable or representative fake-news dataset, and its accuracy must not be presented as real-world performance.

For a meaningful project, replace or expand it with a properly sourced, legally usable, labelled dataset. Keep the columns:
- `text`: headline or article text
- `label`: `REAL` or `FAKE`

Use a balanced dataset with many examples in both classes. Record the dataset source and explain its limitations in your report. Then run `python train_model.py` again.

## Important limitations
- The model learns text patterns from training examples; it does not independently verify facts.
- “LIKELY FAKE” means the model predicts the text resembles the FAKE training examples. It is not proof.
- A REAL prediction without an admin-record match is displayed as UNVERIFIED NEWS.
- Admin verification is only as trustworthy as the source checked and the admin's entry.
- This project does not automatically fetch posts from Instagram, YouTube, or other platforms.
