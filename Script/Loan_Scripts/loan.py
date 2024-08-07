# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 08:01:03 2024

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
folder_path = r"C:\Users\Temidayo\Desktop\Test_Question\Loan_folder"
latest_df = read_latest_file_into_dataframe(folder_path)

if latest_df is not None:
    print("DataFrame created from the latest file: File Available")
    

latest_df.head(10)


def transformation(latest_df):
    # List of date columns to be transformed
    date_columns = ['Date_of_release', 'Maturity_date']

    # Step 2: Convert each date column to datetime with time component
    for date_col in date_columns:
        if date_col in latest_df.columns:
            try:
                # Convert to datetime using the correct format
                latest_df[date_col] = pd.to_datetime(latest_df[date_col], format='%m/%d/%Y', errors='coerce')
                
                # Set the time to 00:00:00
                latest_df[date_col] = latest_df[date_col].dt.normalize()
                
                print(f"Column '{date_col}' converted to datetime with time component.")
            except Exception as e:
                print(f"Error converting '{date_col}': {str(e)}")
        else:
            print(f"Column '{date_col}' not found in DataFrame.")
    
    return latest_df

# Apply the transformation function
transformed_df = transformation(latest_df)

# Display the first few rows of the transformed date columns
print(transformed_df[['Date_of_release', 'Maturity_date']].head(10))

# Verify the datatype of the transformed columns
print(transformed_df[['Date_of_release', 'Maturity_date']].dtypes)

# Check for any null values in the transformed columns
print(transformed_df[['Date_of_release', 'Maturity_date']].isnull().sum())

# Display a sample value in the desired format
print(transformed_df['Date_of_release'].iloc[0].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
print(transformed_df['Maturity_date'].iloc[0].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])


# Adding the ingestion_date column with the current UTC timestamp
transformed_df['ingestion_date'] = datetime.utcnow()

# Display the updated DataFrame
transformed_df.head()

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
    table_name = 'loan'
    
    return {
        'sql_server': sql_server,
        'sql_database': sql_database,
        'sql_username': sql_username,
        'sql_password': sql_password,
        'sql_driver': sql_driver
    }

# Function to load DataFrame to SQL database
def load_data_to_sql(transformed_df, table_name, env_dir, schema_name='autocheck'):
    try:
        credentials = get_db_credentials(env_dir)
        connection_string = f"mssql+pyodbc://{credentials['sql_username']}:{credentials['sql_password']}@{credentials['sql_server']}/{credentials['sql_database']}?driver={credentials['sql_driver']}"
        engine = create_engine(connection_string)
        
        # Append DataFrame to SQL table
        transformed_df.to_sql(table_name, engine, schema=schema_name, if_exists='append', index=False)
        
        print(f"Data appended to Azure SQL Database table {schema_name}.{table_name} successfully.")
    except Exception as e:
        print(f"Error writing to SQL Database: {str(e)}")

# Check if DataFrame is available before attempting to load it to SQL
if transformed_df is not None:
    table_name = 'loan'  # Define your table name here
    load_data_to_sql(transformed_df, table_name, env_dir)