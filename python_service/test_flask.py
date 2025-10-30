import requests

url = "http://127.0.0.1:5000/predict"
file_path = r"C:\Users\ajayk\DDoS-Hybrid\data\sample\train_sample.csv"

with open(file_path, "rb") as f:
    response = requests.post(url, files={"file": f})

print("Status:", response.status_code)
print("Response:", response.json())
# Note: Ensure the Flask app is running before executing this script.
