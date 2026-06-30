import pandas as pd
import os

df = pd.read_csv("shoe_dataset.csv")
df['image'] = df['image'].apply(lambda x: os.path.basename(x))
df.to_csv("shoe_dataset.csv", index=False)
