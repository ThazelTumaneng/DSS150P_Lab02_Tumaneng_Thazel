"""Week 2 starter: profile CSV, JSON, Parquet, API payload, and PostgreSQL table.
Complete the TODOs. Do not hard-code expected counts.
"""
from pathlib import Path
import json, csv
import pandas as pd
import os
DATA_DIR=Path(__file__).resolve().parents[1]/'data'

def profile_csv(path):
    print(f"--- Profiling CSV file: {path.name} ---")

    # File Size
    file_size = os.path.getsize(path)
    print(f"File Size: {file_size} bytes")

    # Load dataset using pandas
    df = pd.read_csv(path)

    # Number of Rows and Columns
    print(f"Number of Rows: {len(df)}, Number of Columns: {len(df.columns)}")

    # List columns and inferred logical types
    print("\nColumns and Inferred Logical Types:")
    print(df.dtypes)

    # Count missing values by column
    print("\nMissing Values by Column:")
    print(df.isnull().sum())

    # Detect Exact duplicate rows
    exact_duplicates = df.duplicated().sum()
    print(f"\nExact Duplicate Rows: {exact_duplicates}")

    # Detect whether customer_id is unique
    if 'customer_id' in df.columns:
        is_unique = df['customer_id'].is_unique
        print(f"\nIs 'customer_id' Unique: {is_unique}")

        #Checking total duplicate customer_ids to see the scale of the issues 
        dup_ids = df.duplicated(subset=['customer_id']).sum()
        print(f"Total Duplicate 'customer_id' Entries: {dup_ids}")

    print("\n--- End of CSV Profiling ---\n")
    print("-" * 50)
    
    pass

def profile_json(path):
    print(f"--- Profiling JSON file: {path.name} ---")

    # File size
    file_size = os.path.getsize(path)
    print(f"File Size: {file_size} bytes")

    #Open and load JSON content
    with open(path, 'r') as f:
        data = json.load(f)

    # Confirm root structure is a list of records & count records
    is_list = isinstance(data, list)
    print(f"Root structure is a list: {is_list}")
    record_count = len(data) if is_list else 0
    column_count = len(data[0]) if len(data) > 0 else 0
    print(f"Number of Records: {record_count}")
    print(f"Top-level key count: {column_count}")

    if is_list and record_count > 0:
        # list top-level keys and identify nested fields
        first_record = data[0]
        top_keys = list(first_record.keys())
        print(f"Top-level keys: {top_keys}")

        nested_fields = [k for k, v in first_record.items() if isinstance(v, dict)]
        print(f"Identified nested fields: {nested_fields}")

        df = pd.DataFrame(data)
        print("\nInferred Data Types:")
        print(df.dtypes)

        print("\nNull Value Counts:")
        print(df.isnull().sum())

        unique_keys = set(key for record in data for key in record.keys())
        column_count2 = len(unique_keys)
        print(f"\nTotal unique key count: {column_count2}")

        # Check for exact duplicate records (where every key-value pair matches)
        serialized_records = [json.dumps(record, sort_keys=True) for record in data]
        exact_duplicates = len(serialized_records) - len(set(serialized_records))
        print(f"Exact Duplicate Records: {exact_duplicates}")

        # Check for duplicate unique identifiers
        order_ids = [record.get('order_id') for record in data]
        duplicate_orders = len(order_ids) - len(set(order_ids))
        print(f"Duplicate order_id entries: {duplicate_orders}")

        # requirement note on nested shipping objects 
        print("\n[Note for Report] Nested shipping object can be represented downstream by: "
              "1) Flattening fields into scalar columns, or 2) Preserving as a nested JSON/Struct type.")
              
    print("-" * 40 + "\n")
    pass

def profile_parquet(path):

    # File Size
    file_size = os.path.getsize(path)
    print(f"File Size;: {file_size} bytes")

    # read file with pandas
    df = pd.read_parquet(path)

    # report shape and data types
    print(f"Shape (Rows, Columns): {df.shape}")
    print("\n Data Types: ")
    print(df.dtypes)

    # count missing values
    print("\nNUll Value Counts:")
    print(df.isnull().sum())

    # exact duplicates
    exact_duplicates = df.duplicated().sum()
    print(f"Exact Duplicate Rows: {exact_duplicates}")

    # Detect whether product_id is unique
    if 'product_id' in df.columns:
        is_unique = df['product_id'].is_unique
        print(f"\nIs 'product_id' Unique: {is_unique}")

        #Checking total duplicate customer_ids to see the scale of the issues 
        dup_ids = df.duplicated(subset=['product_id']).sum()
        print(f"Total Duplicate 'product_id' Entries: {dup_ids}")

    print("\n--- End of Parquet Profiling ---\n")
    print("-" * 50)
    pass

if __name__=='__main__':
    profile_csv(DATA_DIR/'customers.csv')
    profile_json(DATA_DIR/'orders.json')
    profile_parquet(DATA_DIR/'products.parquet')
