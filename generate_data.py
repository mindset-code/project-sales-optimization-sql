import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set seed for reproducibility
np.random.seed(42)

# Number of sales records
n_records = 10000

# Generate synthetic data
start_date = datetime(2024, 1, 1)
dates = [start_date + timedelta(days=random.randint(0, 364)) for _ in range(n_records)]

data = {
    'SaleID': range(10000, 10000 + n_records),
    'SaleDate': dates,
    'Region': np.random.choice(['North America', 'Europe', 'Asia', 'LATAM'], n_records, p=[0.35, 0.30, 0.20, 0.15]),
    'ProductCategory': np.random.choice(['Software', 'Hardware', 'Service'], n_records, p=[0.5, 0.3, 0.2]),
    'Revenue': np.random.uniform(100, 5000, n_records).round(2),
    'Cost': np.random.uniform(50, 2000, n_records).round(2),
    'SalesPersonID': np.random.randint(1, 21, n_records), # 20 Sales people
    'CustomerType': np.random.choice(['SMB', 'Enterprise', 'Individual'], n_records, p=[0.4, 0.3, 0.3])
}

df = pd.DataFrame(data)

# Calculate Profit
df['Profit'] = df['Revenue'] - df['Cost']

# Save the dataset as CSV
df.to_csv('/home/ubuntu/project3_sales_sql/sales_data.csv', index=False)

print("Synthetic Sales Data generated successfully.")
