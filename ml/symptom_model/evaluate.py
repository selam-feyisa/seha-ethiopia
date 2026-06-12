import pandas as pd
import joblib
import json
from sklearn.metrics import classification_report

# Load test data
test_df = pd.read_csv("data/processed/symptoms_test.csv")

X_test = test_df.drop("disease", axis=1)
y_test = test_df["disease"]

# Load trained model
model = joblib.load("symptom_model.pkl")

# Predictions
predictions = model.predict(X_test)

# Classification report (VERY IMPORTANT for supervisor)
report = classification_report(y_test, predictions, output_dict=True)

print("\n=== CLASSIFICATION REPORT ===")
print(classification_report(y_test, predictions))

# Save results to JSON
with open("data/processed/eval_results.json", "w") as f:
    json.dump(report, f, indent=4)

print("\nEvaluation results saved to eval_results.json")