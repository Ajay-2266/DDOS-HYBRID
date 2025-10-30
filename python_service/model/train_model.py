import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from joblib import dump
import numpy as np

# Paths relative to project root
train_file = os.path.join("data", "processed", "train_processed.csv")
test_file  = os.path.join("data", "processed", "test_processed.csv")

print("[INFO] Loading datasets...")
train_df = pd.read_csv(train_file)

# Try loading test file (optional)
if os.path.exists(test_file):
    test_df = pd.read_csv(test_file)
    print(f"[INFO] Test dataset loaded: {test_df.shape}")
else:
    test_df = None
    print("[WARNING] test_processed.csv not found, continuing with train only")

print(f"[INFO] Train dataset loaded: {train_df.shape}")

# ---- Split features/labels ----
# Assuming last column is label
X = train_df.iloc[:, :-1]
y = train_df.iloc[:, -1]

# Train/Validation split
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ---- Train model ----
print("[INFO] Training RandomForest model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ---- Evaluate ----
score = model.score(X_val, y_val)
print(f"[INFO] Validation Accuracy: {score:.4f}")

# ---- Save trained model ----
model_dir = os.path.join("python_service", "model", "saved")
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, "rf_model.joblib")

dump(model, model_path)

print(f"[INFO] Model saved to {model_path}")
