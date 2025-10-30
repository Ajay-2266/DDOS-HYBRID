import os
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler

# -----------------------------
# Paths
# -----------------------------
# BASE_DIR = project root, not inside python_service
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw", "NSL-KDD")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

raw_train = os.path.join(RAW_DIR, "KDDTrain+.csv")
raw_test  = os.path.join(RAW_DIR, "KDDTest+.csv")

print("loading for train file at:", raw_train)
print("Exists?,", os.path.exists(raw_train))
# -----------------------------
# Load datasets
# -----------------------------
print("[INFO] Loading raw datasets...")
train_df = pd.read_csv(raw_train)
test_df  = pd.read_csv(raw_test)
print(f"[INFO] Train shape: {train_df.shape}, Test shape: {test_df.shape}")

# -----------------------------
# Standardize label column
# -----------------------------
train_df.rename(columns={train_df.columns[-1]: "label"}, inplace=True)
test_df.rename(columns={test_df.columns[-1]: "label"}, inplace=True)
label_col = "label"
print(f"[INFO] Label column set to '{label_col}'")

# -----------------------------
# Identify categorical columns
# -----------------------------
categorical_cols = train_df.select_dtypes(include=["object"]).columns.tolist()
categorical_cols = [c for c in categorical_cols if c != label_col]
print("[INFO] Categorical columns:", categorical_cols)

# -----------------------------
# Encode categorical columns
# -----------------------------
encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    train_df[col] = le.fit_transform(train_df[col])
    encoders[col] = le

# Save encoders dict
encoders_path = os.path.join(BASE_DIR, "python_service", "model", "saved", "encoders.joblib")
joblib.dump(encoders, encoders_path)
print(f"[INFO] Encoders saved -> {encoders_path}")

# -----------------------------
# Encode label column
# -----------------------------
label_encoder = LabelEncoder()
train_df[label_col] = label_encoder.fit_transform(train_df[label_col])
test_df[label_col] = label_encoder.transform(test_df[label_col])
label_encoder_path = os.path.join(BASE_DIR, "python_service", "model", "saved", "label_encoder.joblib")
joblib.dump(label_encoder, label_encoder_path)
print(f"[INFO] Label encoder saved -> {label_encoder_path}")

# -----------------------------
# Transform test categorical columns safely
# -----------------------------
for col in categorical_cols:
    le = encoders[col]
    if col in test_df.columns:
        test_df[col] = test_df[col].apply(lambda x: x if x in le.classes_ else "UNK")
        if "UNK" not in le.classes_:
            le.classes_ = np.append(le.classes_, "UNK")
        test_df[col] = le.transform(test_df[col])
    else:
        test_df[col] = 0

# -----------------------------
# Prepare features
# -----------------------------
X_train = train_df.drop(columns=[label_col])
X_test  = test_df.drop(columns=[label_col])

# Ensure all columns in test
for col in X_train.columns:
    if col not in X_test.columns:
        X_test[col] = 0

# Match column order
X_test = X_test[X_train.columns]

# -----------------------------
# Scale numeric columns only
# -----------------------------
numeric_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
scaler = StandardScaler()
X_train_scaled = X_train.copy()
X_test_scaled  = X_test.copy()
X_train_scaled[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
X_test_scaled[numeric_cols]  = scaler.transform(X_test[numeric_cols])

# -----------------------------
# Preserve feature names
# -----------------------------
feature_columns = X_train.columns.tolist()
train_processed = pd.DataFrame(X_train_scaled, columns=feature_columns)
train_processed[label_col] = train_df[label_col]

test_processed = pd.DataFrame(X_test_scaled, columns=feature_columns)
test_processed[label_col] = test_df[label_col]

# -----------------------------
# Save processed CSVs
# -----------------------------
train_out = os.path.join(PROCESSED_DIR, "train_processed.csv")
test_out  = os.path.join(PROCESSED_DIR, "test_processed.csv")
train_processed.to_csv(train_out, index=False)
test_processed.to_csv(test_out, index=False)

print(f"[INFO] Processed train saved -> {train_out}")
print(f"[INFO] Processed test saved  -> {test_out}")
print("[INFO] Preprocessing complete.")
