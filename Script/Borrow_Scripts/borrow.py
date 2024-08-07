# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 23:20:09 2024

@author: Temidayo
"""

import os
import pandas as pd
import tabula
from sqlalchemy import create_engine
from dotenv import dotenv_values
from datetime import datetime

# Function to get the latest file from a directory
def get_latest_file(folder_path):
    files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]
    
    if files:
        latest_file = max(files, key=os.path.getmtime)
        return latest_file
    else:
        return None

# Function to extract tables from a PDF using PyTabula
def extract_tables_from_pdf(pdf_path):
    # Read PDF into DataFrames
    dfs = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
    return dfs

# Function to read the latest file into a DataFrame or extract tables from a PDF
def read_latest_file(folder_path):
    latest_file = get_latest_file(folder_path)

    if latest_file:
        if latest_file.lower().endswith('.csv'):
            df = pd.read_csv(latest_file)
            return [df]  # Return as a list of DataFrames
        elif latest_file.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(latest_file)
            return [df]  # Return as a list of DataFrames
        elif latest_file.lower().endswith('.pdf'):
            # Extract tables from PDF
            tables = extract_tables_from_pdf(latest_file)
            if tables:
                return tables  # Return the list of DataFrames
            else:
                print(f"No tables found in {latest_file}")
                return None
        else:
            print(f"Unsupported file format for {latest_file}")
            return None
    else:
        print(f"No files found in {folder_path}")
        return None

# Function to process the latest file in the folder
def clean_dataframe(df):
    if 'Unnamed: 0' in df.columns:
        df = df.drop('Unnamed: 0', axis=1)
    return df

def process_latest_folder(folder_path):
    extracted_data = read_latest_file(folder_path)
    if isinstance(extracted_data, list) and all(isinstance(df, pd.DataFrame) for df in extracted_data):
        # Clean all DataFrames
        cleaned_data = [clean_dataframe(df) for df in extracted_data]
        
        # If there's only one DataFrame, return it directly
        if len(cleaned_data) == 1:
            return cleaned_data[0]
        # If there are multiple DataFrames, return the list
        return cleaned_data
    else:
        return None

# Usage
base_path = r"C:\Users\Temidayo\Desktop\Test_Question\Borrow_Folder"
df = process_latest_folder(base_path)

if df is not None:
    if isinstance(df, pd.DataFrame):
        print(df)  # or df.head() if you only want to see the first few rows
    else:
        print("Multiple tables found. Using the first one:")
        print(df[0])  # or df[0].head()
else:
    print("No data found.")
    
    
df = process_latest_folder(base_path)


# Adding the ingestion_date column with the current UTC timestamp
df['ingestion_date'] = datetime.utcnow()

# Step 3: Load environment variables from .env file
env_dir = r'C:\Users\Temidayo\Desktop\Test_Question\Credentials'
env_values = dotenv_values(os.path.join(env_dir, '.env'))


# Function to load environment variables from .env file
def get_db_credentials(env_dir):
    env_values = dotenv_values(os.path.join(env_dir, '.env'))
    
    sql_server = env_values.get("sql_server")
    sql_database = env_values.get("sql_database")
    sql_username = env_values.get("sql_username")
    sql_password = env_values.get("sql_password")
    sql_driver = 'ODBC Driver 17 for SQL Server'
    schema_name = 'autocheck'
    table_name = 'borrow'
    
    return {
        'sql_server': sql_server,
        'sql_database': sql_database,
        'sql_username': sql_username,
        'sql_password': sql_password,
        'sql_driver': sql_driver
    }

# Function to load DataFrame to SQL database
def load_data_to_sql(df, table_name, env_dir, schema_name='autocheck'):
    try:
        credentials = get_db_credentials(env_dir)
        connection_string = f"mssql+pyodbc://{credentials['sql_username']}:{credentials['sql_password']}@{credentials['sql_server']}/{credentials['sql_database']}?driver={credentials['sql_driver']}"
        engine = create_engine(connection_string)
        
        # Append DataFrame to SQL table
        df.to_sql(table_name, engine, schema=schema_name, if_exists='append', index=False)
        
        print(f"Data appended to Azure SQL Database table {schema_name}.{table_name} successfully.")
    except Exception as e:
        print(f"Error writing to SQL Database: {str(e)}")

# Check if DataFrame is available before attempting to load it to SQL
if df is not None:
    table_name = 'borrow'  # Define your table name here
    load_data_to_sql(df, table_name, env_dir)