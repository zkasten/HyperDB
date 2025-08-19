import pandas as pd
import numpy as np
import json

# Create a sample DataFrame with NaN values
data = {'col1': [1, 2, np.nan, 4],
        'col2': [np.nan, 6, 7, 8]}
df = pd.DataFrame(data)

print(df.to_json())
print("Original DataFrame:")
print(df)

# Replace NaN with None
df_replaced = df.replace({np.nan: None})
#print(json.dumps(df_replaced))
print(df_replaced.to_json())

print("\nDataFrame after replacing NaN with None:")
print(df_replaced)
