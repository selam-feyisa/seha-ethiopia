import pandas as pd

# Load dataset
df = pd.read_csv("data/raw/disease_symptoms.csv")

# Standardize column names
df.columns = df.columns.str.lower()

# Remove completely empty rows
df = df.dropna(how="all")

# Get symptom columns
symptom_cols = [col for col in df.columns if col.startswith("symptom_")]

# Collect all unique symptoms
all_symptoms = set()

for col in symptom_cols:
    symptoms = df[col].dropna().str.strip()
    all_symptoms.update(symptoms)

print("Total unique symptoms:", len(all_symptoms))

# Create encoded dataframe
encoded_df = pd.DataFrame(0, index=df.index, columns=sorted(all_symptoms))

# Mark symptom presence
for col in symptom_cols:
    for idx, symptom in df[col].dropna().items():
        encoded_df.at[idx, symptom.strip()] = 1

# Add disease column back
encoded_df["disease"] = df["disease"]

print("\nEncoded Shape:")
print(encoded_df.shape)

print("\nFirst 5 Rows:")
print(encoded_df.head())
print("\nUnique Diseases:")
print(sorted(df["disease"].unique()))
print("\nTotal Diseases:")
print(df["disease"].nunique())

# Save processed dataset
encoded_df.to_csv(
    "data/processed/symptoms_cleaned.csv",
    index=False
)

print("\nProcessed dataset saved successfully!")