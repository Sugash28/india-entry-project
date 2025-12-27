import sqlite3
import os

# Connect to the database
# We moved it to the parent directory in the previous step
db_path = os.path.join("..", "sql_app.db")

print(f"Connecting to database at: {os.path.abspath(db_path)}")

try:
    conn = sqlite3.connect(db_path)
    # Configure row factory to access columns by name
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    table_names = [t[0] for t in tables]
    print(f"\nTables found: {', '.join(table_names)}")

    for table_name in table_names:
        print(f"\n--- Data in '{table_name}' table ---")
        try:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            if not rows:
                print("No data found.")
                continue

            # Get column names
            columns = [description[0] for description in cursor.description]
            
            # Calculate column widths for pretty printing
            col_widths = [len(col) for col in columns]
            for row in rows:
                for i, value in enumerate(row):
                    col_widths[i] = max(col_widths[i], len(str(value)))
            
            # Print headers
            header = " | ".join(f"{col:<{width}}" for col, width in zip(columns, col_widths))
            print("-" * len(header))
            print(header)
            print("-" * len(header))
            
            # Print rows
            for row in rows:
                print(" | ".join(f"{str(val):<{width}}" for val, width in zip(row, col_widths)))
                
        except Exception as e:
            print(f"Error reading table {table_name}: {e}")

    conn.close()

except FileNotFoundError:
    print("Database file not found.")
except Exception as e:
    print(f"An error occurred: {e}")
