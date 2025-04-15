import pandas as pd
import numpy as np
from sklearn.utils.class_weight import compute_class_weight

# Load your training CSV file
training_path = (
    r"/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/learning_data/training_ground_July.csv"
)
df = pd.read_csv(training_path)

# Make sure 'COD' is in the data columns
print(df["COD"].value_counts())

print("Columns:", df.columns.tolist())

# Compute unique classes from the 'COD' column
classes = np.unique(df["COD"])

# Compute balanced class weights from the training data based on 'COD'
computed_weights = compute_class_weight(class_weight="balanced", classes=classes, y=df["COD"])
class_weights = dict(zip(classes, computed_weights))
print("Computed Class Weights (before adjustment):")
print(class_weights)

# Manually lower the weight for urban areas (class 51)
# Here we multiply by a factor (0.5 in this example); adjust this factor as needed
# if 51 in class_weights:
# class_weights[51] *= 0.2

print("\nAdjusted Class Weights (urban area '51' weight lowered):")
print(class_weights)

for key, value in class_weights.items():
    print(key, value)
