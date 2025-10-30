import pandas as pd
import random
import os
from joblib import load
from sklearn.preprocessing import LabelEncoder

# ---- Paths ----
MODEL_PATH = "python_service/model/saved/rf_model.joblib"
TEST_DATA_PATH = "data/processed/test_processed.csv"
RAW_TRAIN_PATH = "data/raw/NSL-KDD/KDDTrain+.csv"

# ---- Check files exist ----
for path in [MODEL_PATH, TEST_DATA_PATH, RAW_TRAIN_PATH]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

# ---- Load trained model ----
model = load(MODEL_PATH)
print("[TEST] Model loaded successfully.")

# ---- Load test dataset ----
test_df = pd.read_csv(TEST_DATA_PATH)
print(f"[TEST] Test dataset loaded: {test_df.shape}")

# ---- Load original raw train labels to restore human-readable labels ----
raw_train_df = pd.read_csv(RAW_TRAIN_PATH)
original_labels = raw_train_df.iloc[:, -1]  # last column
label_encoder = LabelEncoder()
label_encoder.fit(original_labels)
print("[TEST] Label encoder fitted successfully.")

# ---- Predict multiple random samples ----
NUM_SAMPLES = 5
samples = test_df.sample(n=NUM_SAMPLES, random_state=random.randint(0, 1000))

for idx, row in samples.iterrows():
    # Convert to 1-row DataFrame to keep feature names
    X_sample = row.drop(labels=["label"], errors="ignore").to_frame().T

    # Prediction
    pred_num = model.predict(X_sample)[0]
    pred_label = label_encoder.inverse_transform([pred_num])[0]

    # Actual label (cast to int to avoid float issue)
    actual_num = int(row["label"])
    actual_label = label_encoder.inverse_transform([actual_num])[0]

    # Confidence
    conf = max(model.predict_proba(X_sample)[0]) * 100

    print(f"\n[TEST] Sample index: {idx}")
    print(f"[TEST] Predicted: {pred_label}")
    print(f"[TEST] Actual   : {actual_label}")
    print(f"[TEST] Confidence: {conf:.2f}%")

print("\n[TEST] All samples processed successfully.")
