import sqlite3
import pandas as pd
import random
from faker import Faker

# Initialize Faker
fake = Faker()

# Database path
DATABASE_PATH = "data/business_sales.db"

# Connect to SQLite database
conn = sqlite3.connect(DATABASE_PATH)

# Create cursor
cursor = conn.cursor()

# Drop table if already exists
cursor.execute("DROP TABLE IF EXISTS sales")

# Create sales table
cursor.execute("""
CREATE TABLE sales (
    order_id INTEGER PRIMARY KEY,
    order_date TEXT,
    region TEXT,
    product TEXT,
    category TEXT,
    sales REAL,
    profit REAL,
    quantity INTEGER
)
""")

# Sample business data
regions = ["North", "South", "East", "West"]

categories = {
    "Electronics": [
        "Laptop",
        "Mobile Phone",
        "Headphones",
        "Keyboard"
    ],
    "Furniture": [
        "Chair",
        "Table",
        "Desk",
        "Sofa"
    ],
    "Office Supplies": [
        "Notebook",
        "Pen",
        "Printer Paper",
        "Stapler"
    ]
}

# Store rows
data = []

# Generate sample records
for order_id in range(1, 501):

    category = random.choice(list(categories.keys()))
    product = random.choice(categories[category])

    sales = round(random.uniform(50, 5000), 2)

    profit = round(sales * random.uniform(0.05, 0.3), 2)

    quantity = random.randint(1, 10)

    row = {
        "order_id": order_id,
        "order_date": fake.date_between(
            start_date="-1y",
            end_date="today"
        ),
        "region": random.choice(regions),
        "product": product,
        "category": category,
        "sales": sales,
        "profit": profit,
        "quantity": quantity
    }

    data.append(row)

# Convert to DataFrame
df = pd.DataFrame(data)

# Insert data into SQLite
df.to_sql(
    "sales",
    conn,
    if_exists="append",
    index=False
)

# Save changes
conn.commit()

# Close connection
conn.close()

print("Database created successfully.")
print("Table name: sales")
print("Total records inserted:", len(df))