import numpy as np
import pandas as pd
from sklearn.utils import compute_class_weight

for month in ["April", "May", "June", "July", "August", "September", "October"]:
    train_path = rf"/Users/juliusjancevicius/Library/CloudStorage/OneDrive-Personal/VGTU/IV Kursas/Classification Libraries/learning_data/training_ground_{month}.csv"
    valid_path = rf"/Users/juliusjancevicius/Library/CloudStorage/OneDrive-Personal/VGTU/IV Kursas/Classification Libraries/learning_data/training_ground_{month}.csv"

    # Load the training CSV
    for path in [train_path, valid_path]:
        df = pd.read_csv(path)
        df = df[df["COD"] != 51]

        # Print out the first few rows and columns to confirm the data structure
        print("Training Data Columns:", df.columns.tolist())

        # Display the original class distribution
        print("Original Training Class Distribution:")
        print(df["COD"].value_counts())
        classes = np.unique(df["COD"])

        computed_weights = compute_class_weight(class_weight="balanced", classes=classes, y=df["COD"])
        class_weights = dict(zip(classes, computed_weights))
        print("Computed Class Weights (before adjustment):")
        for key, value in class_weights.items():
            print(key, value)
        print("")
# ------------------------------------------------------------------------------
# Under-sample the "Urban" class
# ------------------------------------------------------------------------------

# Separate the Urban and non-Urban subsets.
# urban_df = train_df[train_df['COD'] == 51]
# non_urban_df = train_df[train_df['COD'] != 51]
#
# # Display counts before under-sampling
# print("\nCount of Urban samples before under-sampling:", urban_df.shape[0])
# print("Count of Non-Urban samples:", non_urban_df.shape[0])
#
# # Under-sample the Urban class; here we keep 50% of the urban samples.
# # Adjust frac value (0.5) if you need a different under-sampling ratio.
# urban_sampled = urban_df.sample(frac=0.5, random_state=42)
#
# # Combine the non-urban samples with the under-sampled urban samples.
# balanced_train_df = pd.concat([non_urban_df, urban_sampled]).sample(frac=1, random_state=42)
# # The final sample is shuffled to mix the classes.
#
# # Print out the new class distribution after under-sampling
# print("\nBalanced Training Class Distribution:")
# print(balanced_train_df['COD'].value_counts())
#
# # Save the balanced training dataset into a new CSV file.
# balanced_csv_path = path
# balanced_train_df.to_csv(balanced_csv_path, index=False)
# print("\nBalanced training data saved to:", balanced_csv_path)
