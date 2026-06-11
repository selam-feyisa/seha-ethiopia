"""
SEHA Ethiopia Symptom Prediction Model

Dataset Structure:
- Each row represents a patient case.
- Symptom columns are binary encoded (1 = present, 0 = absent).
- Disease column is the target label.
- Data is split using stratified sampling:
  80% training, 20% testing.
"""

import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import GridSearchCV

from xgboost import XGBClassifier

# ============================================================
# LOAD DATA
# ============================================================

train_df = pd.read_csv("data/processed/symptoms_train.csv")
test_df = pd.read_csv("data/processed/symptoms_test.csv")

# Features
X_train = train_df.drop("disease", axis=1)
X_test = test_df.drop("disease", axis=1)

# Target
y_train = train_df["disease"]
y_test = test_df["disease"]

print("Train Shape:")
print(train_df.shape)

print("\nTest Shape:")
print(test_df.shape)

# ============================================================
# RANDOM FOREST
# ============================================================

rf = RandomForestClassifier(
    random_state=42
)

rf.fit(X_train, y_train)

rf_predictions = rf.predict(X_test)

rf_accuracy = accuracy_score(
    y_test,
    rf_predictions
)

rf_precision = precision_score(
    y_test,
    rf_predictions,
    average="weighted"
)

rf_recall = recall_score(
    y_test,
    rf_predictions,
    average="weighted"
)

rf_f1 = f1_score(
    y_test,
    rf_predictions,
    average="weighted"
)

print("\n=== RANDOM FOREST RESULTS ===")
print("Accuracy :", rf_accuracy)
print("Precision:", rf_precision)
print("Recall   :", rf_recall)
print("F1 Score :", rf_f1)

# ============================================================
# XGBOOST
# ============================================================

encoder = LabelEncoder()

y_train_encoded = encoder.fit_transform(y_train)
y_test_encoded = encoder.transform(y_test)

xgb = XGBClassifier(
    random_state=42,
    eval_metric="mlogloss"
)

xgb.fit(
    X_train,
    y_train_encoded
)

xgb_predictions = xgb.predict(X_test)

xgb_accuracy = accuracy_score(
    y_test_encoded,
    xgb_predictions
)

xgb_precision = precision_score(
    y_test_encoded,
    xgb_predictions,
    average="weighted"
)

xgb_recall = recall_score(
    y_test_encoded,
    xgb_predictions,
    average="weighted"
)

xgb_f1 = f1_score(
    y_test_encoded,
    xgb_predictions,
    average="weighted"
)

print("\n=== XGBOOST RESULTS ===")
print("Accuracy :", xgb_accuracy)
print("Precision:", xgb_precision)
print("Recall   :", xgb_recall)
print("F1 Score :", xgb_f1)

# ============================================================
# MODEL COMPARISON
# ============================================================

print("\n=== MODEL COMPARISON ===")

print(
    f"Random Forest -> Accuracy: {rf_accuracy:.4f}, "
    f"Precision: {rf_precision:.4f}, "
    f"Recall: {rf_recall:.4f}, "
    f"F1: {rf_f1:.4f}"
)

print(
    f"XGBoost       -> Accuracy: {xgb_accuracy:.4f}, "
    f"Precision: {xgb_precision:.4f}, "
    f"Recall: {xgb_recall:.4f}, "
    f"F1: {xgb_f1:.4f}"
)

# ============================================================
# GRID SEARCH
# ============================================================

print("\n=== GRID SEARCH ===")

param_grid = {
    "n_estimators": [50, 100],
    "max_depth": [None, 10, 20],
    "min_samples_split": [2, 5]
}

grid_search = GridSearchCV(
    estimator=RandomForestClassifier(random_state=42),
    param_grid=param_grid,
    cv=3,
    scoring="accuracy",
    n_jobs=-1
)

grid_search.fit(X_train, y_train)

print("\nBest Parameters:")
print(grid_search.best_params_)

print("\nBest Cross Validation Score:")
print(grid_search.best_score_)