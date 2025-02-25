import sqlite3
import random

# Connect to SQLite database (creates file if not exists)
connection = sqlite3.connect("clothing.db")
cursor = connection.cursor()

# Drop existing tables to start fresh
cursor.executescript("""
DROP TABLE IF EXISTS t_shirts;
DROP TABLE IF EXISTS discounts;

-- Create the t_shirts table
CREATE TABLE t_shirts (
    t_shirt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT CHECK (brand IN ('Van Huesen', 'Levi', 'Nike', 'Adidas')) NOT NULL,
    color TEXT CHECK (color IN ('Red', 'Blue', 'Black', 'White')) NOT NULL,
    size TEXT CHECK (size IN ('XS', 'S', 'M', 'L', 'XL')) NOT NULL,
    price INTEGER CHECK (price BETWEEN 10 AND 50),
    stock_quantity INTEGER NOT NULL
);

-- Create the discounts table
CREATE TABLE discounts (
    discount_id INTEGER PRIMARY KEY AUTOINCREMENT,
    t_shirt_id INTEGER NOT NULL,
    pct_discount DECIMAL(5,2) CHECK (pct_discount BETWEEN 0 AND 100),
    FOREIGN KEY (t_shirt_id) REFERENCES t_shirts(t_shirt_id)
);
""")

# Insert sample data into t_shirts table
brands = ['Van Huesen', 'Levi', 'Nike', 'Adidas']
colors = ['Red', 'Blue', 'Black', 'White']
sizes = ['XS', 'S', 'M', 'L', 'XL']

tshirt_data = [
    (random.choice(brands), random.choice(colors), random.choice(sizes), random.randint(10, 50), random.randint(5, 100))
    for _ in range(20)  # Insert 20 random records
]

cursor.executemany("INSERT INTO t_shirts (brand, color, size, price, stock_quantity) VALUES (?, ?, ?, ?, ?)", tshirt_data)

# Insert sample data into discounts table
discounts_data = [(i + 1, random.randint(5, 50)) for i in range(10)]  # Insert 10 discounts
cursor.executemany("INSERT INTO discounts (t_shirt_id, pct_discount) VALUES (?, ?)", discounts_data)

# Commit changes and close connection
connection.commit()
connection.close()

print("✅ Database setup complete!")
