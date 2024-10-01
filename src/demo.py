import pandas as pd

# Step 1: Read the CSV file
file_path = "/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/learning_data/training_ground_July copy.csv"  # replace with your CSV file path
df = pd.read_csv(file_path)

# Step 2: Take 5000 random rows
df_sampled = df.sample(n=5000, random_state=42)  # random_state for reproducibility

# Step 3: Save the sampled data to another CSV file
output_file = (
    "/Users/juliusjancevicius/Desktop/2ND_Intelektualios/csv/july.csv"  # replace with your desired output file path
)
df_sampled.to_csv(output_file, index=False)

print(f"Random sample saved to {output_file}")
