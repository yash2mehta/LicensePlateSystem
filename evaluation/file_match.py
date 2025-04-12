import pandas as pd
import os

# Create output directory if it doesn't exist
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Load the Excel files
print("Loading Excel files...")
recognized_df = pd.read_excel("recognized_plates.xlsx")
truth_df = pd.read_excel("truth_label_format.xlsx")

# Format the Image Number column to include .jpg extension in truth_df if not present
truth_df["Image Number (Filename)"] = truth_df["Image Number (Filename)"].astype(str).apply(
    lambda x: f"{x.strip()}.jpg" if not x.strip().endswith('.jpg') else x.strip()
)

# Strip any whitespace from recognized_df filenames
recognized_df["Image Number (Filename)"] = recognized_df["Image Number (Filename)"].astype(str).str.strip()

# Take only first 45 rows from each dataframe
truth_df = truth_df.head(45)
recognized_df = recognized_df.head(45)

# Print sample data for debugging
print("\nSample truth data after formatting:")
print(truth_df["Image Number (Filename)"].head())
print("\nSample recognized data:")
print(recognized_df["Image Number (Filename)"].head())

# Merge on Image Filename
print("\nMerging dataframes...")
merged_df = pd.merge(truth_df, recognized_df, on="Image Number (Filename)", suffixes=('_truth', '_pred'))
print(f"Number of rows after merge: {len(merged_df)}")

# Handle NaN values by converting to empty strings
for col in ['License Plate_truth', 'License Plate_pred', 'Make_truth', 'Make_pred', 'Model_truth', 'Model_pred']:
    merged_df[col] = merged_df[col].fillna('')

# License Plate and Make: case-insensitive exact match
print("\nCalculating matches...")
merged_df['License Plate Match'] = merged_df.apply(
    lambda row: row['License Plate_truth'].upper() == row['License Plate_pred'].upper(),
    axis=1
)
merged_df['Make Match'] = merged_df.apply(
    lambda row: row['Make_truth'].lower() == row['Make_pred'].lower(),
    axis=1
)

# Model: partial (substring) match, case-insensitive
merged_df['Model Match'] = merged_df.apply(
    lambda row: (
        isinstance(row['Model_truth'], str) and isinstance(row['Model_pred'], str)
        and (
            row['Model_truth'].lower() in row['Model_pred'].lower()
            or row['Model_pred'].lower() in row['Model_truth'].lower()
        )
    ),
    axis=1
)

# Create evaluation dataframe with spacing and renamed columns
evaluation = pd.DataFrame()

# Add image number column
evaluation['Image Number (Filename)'] = merged_df['Image Number (Filename)']

# Add license plate section
evaluation['License Plate (Truth)'] = merged_df['License Plate_truth']
evaluation['License Plate (Plate Recognizer)'] = merged_df['License Plate_pred']
evaluation['License Plate Match'] = merged_df['License Plate Match']

# Add empty column for spacing
evaluation[''] = ''

# Add make section
evaluation['Make (Truth)'] = merged_df['Make_truth']
evaluation['Make (Plate Recognizer)'] = merged_df['Make_pred']
evaluation['Make Match'] = merged_df['Make Match']

# Add empty column for spacing
evaluation[' '] = ''

# Add model section
evaluation['Model (Truth)'] = merged_df['Model_truth']
evaluation['Model (Plate Recognizer)'] = merged_df['Model_pred']
evaluation['Model Match'] = merged_df['Model Match']

# Print summary statistics
print("\nSummary of matches:")
print(f"License Plate Matches: {evaluation['License Plate Match'].sum()} out of {len(evaluation)}")
print(f"Make Matches: {evaluation['Make Match'].sum()} out of {len(evaluation)}")
print(f"Model Matches: {evaluation['Model Match'].sum()} out of {len(evaluation)}")

# Save the results
print("\nSaving results...")

try:
    output_path = os.path.join(output_dir, "evaluation_results_new.xlsx")
    evaluation.to_excel(output_path, index=False)
    print(f"✅ Evaluation saved to '{output_path}'")
except PermissionError:
    print("❌ Could not save file - please close any open Excel files and try again")
    backup_path = os.path.join(output_dir, "evaluation_results_backup.xlsx")
    evaluation.to_excel(backup_path, index=False)
    print(f"✅ Evaluation saved to '{backup_path}' instead")