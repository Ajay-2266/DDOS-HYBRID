import pandas as pd

def arff_to_csv(arff_path, csv_path):
    with open(arff_path, 'r') as f:
        lines = f.readlines()

    # Skip header until @DATA
    data_start = False
    data = []
    for line in lines:
        if data_start:
            if line.strip():  # ignore empty lines
                data.append(line.strip().split(','))
        elif line.strip().lower() == "@data":
            data_start = True

    # Convert to DataFrame (no headers, because ARFF headers failed)
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False, header=False)
    print(f"✅ Converted {arff_path} → {csv_path}")

# Paths
train_arff = "../data/raw/NSL-KDD/KDDTrain+.arff"
test_arff = "../data/raw/NSL-KDD/KDDTest+.arff"

train_csv = "../data/raw/NSL-KDD/KDDTrain+.csv"
test_csv = "../data/raw/NSL-KDD/KDDTest+.csv"

# Run conversions
arff_to_csv(train_arff, train_csv)
arff_to_csv(test_arff, test_csv)
