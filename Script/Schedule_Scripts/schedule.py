# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 08:05:09 2024

@author: Temidayo
"""

import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import dotenv_values
from datetime import datetime

def get_latest_file(folder_path):
    files = [os.path.join(folder_path, file) for file in os.listdir(folder_path)]
    
    if files:
        latest_file = max(files, key=os.path.getmtime)
        return latest_file
    else:
        return None

def read_latest_file_into_dataframe(folder_path):
    latest_file = get_latest_file(folder_path)

    if latest_file:
        if latest_file.lower().endswith('.csv'):
            df = pd.read_csv(latest_file)
        elif latest_file.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(latest_file)
        else:
            print(f"Unsupported file format for {latest_file}")
            return None

        return df
    else:
        print(f"No files found in {folder_path}")
        return None
    
# Define the folder path
folder_path = r"C:\Users\Temidayo\Desktop\Test_Question\Schedule_Folder"
latest_df = read_latest_file_into_dataframe(folder_path)

if latest_df is not None:
    print("DataFrame created from the latest file: File Available")
    

latest_df.head(10)

# Adding the ingestion_date column with the current UTC timestamp
latest_df['ingestion_date'] = datetime.utcnow()

# Display the updated DataFrame
latest_df.head()

# Step 3: Load environment variables from .env file
env_dir = r'C:\Users\Temidayo\Desktop\Test_Question\Credentials'
env_values = dotenv_values(os.path.join(env_dir, '.env'))

# Azure SQL Database details
sql_server = env_values.get("sql_server")
sql_database = env_values.get("sql_database")
sql_username = env_values.get("sql_username")
sql_password = env_values.get("sql_password")
sql_driver = 'ODBC Driver 17 for SQL Server'
schema_name = 'autocheck'
table_name = 'schedule'

# Function to load DataFrame to SQL database
def load_data_to_sql(latest_df, table_name):
    try:
        connection_string = f"mssql+pyodbc://{sql_username}:{sql_password}@{sql_server}/{sql_database}?driver={sql_driver}"
        engine = create_engine(connection_string)
        
        # Append DataFrame to SQL table
        latest_df.to_sql(table_name, engine, schema=schema_name, if_exists='append', index=False)
        
        print(f"Data appended to Azure SQL Database table {schema_name}.{table_name} successfully.")
    except Exception as e:
        print(f"Error writing to SQL Database: {str(e)}")

# Check if DataFrame is available before attempting to load it to SQL
if latest_df is not None:
    load_data_to_sql(latest_df, table_name)