import os
import time
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from joblib import load
from scapy.all import sniff, IP, TCP, UDP

# -----------------------------
# Load trained ML artifacts
# -----------------------------
MODEL = load("python_service/model/saved/rf_model.joblib")
ENCODERS = load("python_service/model/saved/encoders.joblib")
print("[INFO] Loaded encoders for columns:", list(ENCODERS.keys()))
LABEL_ENCODER = load("python_service/model/saved/label_encoder.joblib")

# Define NSL-KDD features (41 features)
TRAIN_FEATURE_COLUMNS = [
    "duration","protocol_type","service","flag","src_bytes","dst_bytes","land",
    "wrong_fragment","urgent","hot","num_failed_logins","logged_in",
    "num_compromised","root_shell","su_attempted","num_root","num_file_creations",
    "num_shells","num_access_files","num_outbound_cmds","is_host_login",
    "is_guest_login","count","srv_count","serror_rate","srv_serror_rate",
    "rerror_rate","srv_rerror_rate","same_srv_rate","diff_srv_rate",
    "srv_diff_host_rate","dst_host_count","dst_host_srv_count",
    "dst_host_same_srv_rate","dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate","dst_host_srv_diff_host_rate",
    "dst_host_serror_rate","dst_host_srv_serror_rate",
    "dst_host_rerror_rate","dst_host_srv_rerror_rate"
]

CATEGORICAL_COLS = ["protocol_type", "service", "flag"]

# -----------------------------
# Flask app
# -----------------------------
app = Flask(__name__)

# -----------------------------
# Index route
# -----------------------------
@app.route("/", methods=["GET"])
def index():
    return {"message": "Flask Detection Service running. Use /predict or /live."}

# -----------------------------
# Health check route
# -----------------------------
@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint to verify the service is running.
    """
    try:
        status = {
            "status": "ok",
            "model_loaded": MODEL is not None,
            "encoders_loaded": ENCODERS is not None,
            "label_encoder_loaded": LABEL_ENCODER is not None,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return jsonify(status), 200
    except Exception as ex:
        return jsonify({"status": "failed", "details": str(ex)}), 500

# -----------------------------
# Helper: preprocess dataframe
# -----------------------------
def preprocess_dataframe(df):
    # Ensure all columns exist
    for col in TRAIN_FEATURE_COLUMNS:
        if col not in df.columns:
            if col in CATEGORICAL_COLS:
                df[col] = "other"
            else:
                df[col] = 0

    # Reorder columns exactly
    df = df[TRAIN_FEATURE_COLUMNS].copy()

    # Encode categorical columns
    for col in CATEGORICAL_COLS:
        if col in ENCODERS:
            df[col] = df[col].map(lambda x: x if x in ENCODERS[col].classes_ else "UNK")
            if "UNK" not in ENCODERS[col].classes_:
                ENCODERS[col].classes_ = np.append(ENCODERS[col].classes_, "UNK")
            df[col] = ENCODERS[col].transform(df[col])

    # Ensure numeric columns are numeric
    numeric_cols = df.columns.difference(CATEGORICAL_COLS)
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

    return df


# -----------------------------
# /predict route (CSV upload)
# -----------------------------
@app.route("/predict", methods=["GET","POST"])
def predict():
    if request.method == "GET":
        return jsonify({"message": "Send a POST request with a CSV file to get predictions."}),200
    try:
        if "file" not in request.files:
            return jsonify({"error": "no file uploaded"}), 400

        df = pd.read_csv(request.files["file"])
        if df.empty:
            return jsonify({"error": "empty CSV uploaded"}), 400

        df_processed = preprocess_dataframe(df)

        print(df_processed.head())
        print(df_processed.dtypes)

        preds = MODEL.predict(df_processed)
        probs = MODEL.predict_proba(df_processed)

        unique_vals, counts = np.unique(preds, return_counts=True)
        human_names = LABEL_ENCODER.inverse_transform(unique_vals)
        counts_map = {str(human_names[i]): int(counts[i]) for i in range(len(unique_vals))}
        attack_types = {name: cnt for name, cnt in counts_map.items() if name.lower() != "normal"}

        summary = {
            "total_records": int(len(preds)),
            "counts": counts_map,
            "attack_types": attack_types,
            "avg_confidence_pct": round(float(np.mean(np.max(probs, axis=1)) * 100), 2)
        }

        return jsonify(summary), 200

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


# -----------------------------
# /live route (packet sniffing)
# -----------------------------
@app.route("/live", methods=["GET"])
def live():
    try:
        CAPTURE_COUNT = 200
        CAPTURE_TIMEOUT = 6

        packets = sniff(count=CAPTURE_COUNT, timeout=CAPTURE_TIMEOUT)
        if not packets:
            return jsonify({"error": "no packets captured"}), 200

        # Build flows keyed by 5-tuple
        flows = {}
        for pkt in packets:
            ts = float(getattr(pkt, "time", time.time()))
            src_ip = pkt[IP].src if IP in pkt else "0.0.0.0"
            dst_ip = pkt[IP].dst if IP in pkt else "0.0.0.0"
            proto = "other"
            sport = 0
            dport = 0
            tcp_flags = 0

            if TCP in pkt:
                proto = "tcp"
                sport = int(getattr(pkt[TCP], "sport", 0))
                dport = int(getattr(pkt[TCP], "dport", 0))
                tcp_flags = int(getattr(pkt[TCP], "flags", 0))
            elif UDP in pkt:
                proto = "udp"
                sport = int(getattr(pkt[UDP], "sport", 0))
                dport = int(getattr(pkt[UDP], "dport", 0))

            key = (src_ip, dst_ip, sport, dport, proto)
            length = len(pkt)

            if key not in flows:
                flows[key] = {
                    "first_ts": ts,
                    "last_ts": ts,
                    "pkt_count": 0,
                    "src_bytes": 0,
                    "dst_bytes": 0,
                    "tcp_flags_list": [],
                    "service": "other",
                    "proto": proto,
                    "src_ip": src_ip,
                    "dst_ip": dst_ip,
                    "sport": sport,
                    "dport": dport,
                }

            f = flows[key]
            f["pkt_count"] += 1
            f["last_ts"] = max(f["last_ts"], ts)

            if src_ip == f["src_ip"]:
                f["src_bytes"] += length
            else:
                f["dst_bytes"] += length

            if proto == "tcp":
                f["tcp_flags_list"].append(tcp_flags)

            # approximate service based on port
            if dport in (80, 8080, 8000, 443):
                f["service"] = "http"
            elif dport in (20, 21, 22):
                f["service"] = "ftp"
            elif dport == 53:
                f["service"] = "domain_u"
            elif dport in (25, 587):
                f["service"] = "smtp"
            elif dport == 123:
                f["service"] = "ntp_u"

        # Build flow records
        flow_records = []
        for f in flows.values():
            duration = max(0.0, f["last_ts"] - f["first_ts"])
            avg_flag = int(np.mean(f["tcp_flags_list"])) if f["tcp_flags_list"] else 0
            flow_records.append({
                "duration": duration,
                "protocol_type": f["proto"],
                "service": f["service"],
                "flag": str(avg_flag),
                "src_bytes": f["src_bytes"],
                "dst_bytes": f["dst_bytes"],
                "land": 1 if f["src_ip"] == f["dst_ip"] else 0,
                "wrong_fragment": 0,
                "urgent": 0,
                "hot": 0,
                "num_failed_logins": 0,
                "logged_in": 0,
                "num_compromised": 0,
                "root_shell": 0,
                "su_attempted": 0,
                "num_root": 0,
                "num_file_creations": 0,
                "num_shells": 0,
                "num_access_files": 0,
                "num_outbound_cmds": 0,
                "is_host_login": 0,
                "is_guest_login": 0,
                "count": f["pkt_count"],
                "srv_count": f["pkt_count"],
                "serror_rate": 0.0,
                "srv_serror_rate": 0.0,
                "rerror_rate": 0.0,
                "srv_rerror_rate": 0.0,
                "same_srv_rate": 1.0,
                "diff_srv_rate": 0.0,
                "srv_diff_host_rate": 0.0,
                "dst_host_count": 0,
                "dst_host_srv_count": 0,
                "dst_host_same_srv_rate": 0.0,
                "dst_host_diff_srv_rate": 0.0,
                "dst_host_same_src_port_rate": 0.0,
                "dst_host_srv_diff_host_rate": 0.0,
                "dst_host_serror_rate": 0.0,
                "dst_host_srv_serror_rate": 0.0,
                "dst_host_rerror_rate": 0.0,
                "dst_host_srv_rerror_rate": 0.0,
            })
        
        df_live = pd.DataFrame(flow_records)
        if df_live.empty:
            return jsonify({"error": "no flows constructed"}), 200
        #df_live = preprocess_dataframe(df_live)
        print("DEBUG: df_live columns =>", df_live.columns.tolist())
        print("DEBUG: df_live head =>\n", df_live.head())

        
        # --- Inline preprocessing ---
        for col in TRAIN_FEATURE_COLUMNS:
            if col not in df_live.columns:
                if col in ["protocol_type", "service", "flag"]:
                    df_live[col] = "other"
                else:
                    df_live[col] = 0

        df_live = df_live[TRAIN_FEATURE_COLUMNS].copy()

        # Encode categoricals safely
        for col in ["protocol_type", "service", "flag"]:
            if col in df_live.columns and col in ENCODERS:
                df_live[col] = df_live[col].map(
                    lambda x: x if x in ENCODERS[col].classes_ else "UNK"
                )
                if "UNK" not in ENCODERS[col].classes_:
                    ENCODERS[col].classes_ = np.append(ENCODERS[col].classes_, "UNK")
                df_live[col] = ENCODERS[col].transform(df_live[col])
            else:
                df_live[col] = 0
        valid_classes = set(LABEL_ENCODER.classes_)
        preds = MODEL.predict(df_live)

        # Any predections not in Label_Encoder classes mapped to "unknown"
        safe_preds = []
        for p in preds:
            if p in valid_classes:
                safe_preds.append(p)
            else:
                safe_preds.append("unknown")
        preds = np.array(safe_preds)

        # ----save debug sample for inspection ----
        df_live.to_csv("debug_live.csv",index=False)
        print("[DEBUG] Saved df_live to debug_live.csv with shape:", df_live.shape)

        # now continue with probabilities & summary
        probs = MODEL.predict_proba(df_live)
        #df_live = df_live.fillna(0)

       
        preds = MODEL.predict(df_live)
        probs = MODEL.predict_proba(df_live)

        unique_vals, counts = np.unique(preds, return_counts=True)
        human_names = LABEL_ENCODER.inverse_transform(unique_vals)
        counts_map = {str(human_names[i]): int(counts[i]) for i in range(len(unique_vals))}
        attack_types = {name: cnt for name, cnt in counts_map.items() if name.lower() != "normal"}

        summary = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_flows": int(len(preds)),
            "counts": counts_map,
            "attack_types": attack_types,
            "avg_confidence_pct": round(float(np.mean(np.max(probs, axis=1)) * 100), 2)
        }

        return jsonify(summary), 200

    except Exception as ex:
        return jsonify({"error": "live capture failed", "details": str(ex)}), 500


# -----------------------------
# Run Flask
# -----------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
