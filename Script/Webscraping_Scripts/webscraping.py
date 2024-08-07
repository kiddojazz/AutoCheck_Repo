# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 08:06:53 2024

@author: Temidayo
"""

import time
from functools import wraps
from typing import Dict, List
import re
import uuid
from datetime import datetime
from dotenv import dotenv_values
import os
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from sqlalchemy import create_engine
import json

BASE_URL = "https://www.autorama.ca/vehicles/"

def retry_on_failure(retries=3, delay=2, exceptions=(requests.exceptions.RequestException,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(f'Attempt {attempt + 1} failed: {e}')
                    attempt += 1
                    time.sleep(delay)
            raise Exception(f'Failed after {retries} retries')
        return wrapper
    return decorator


@retry_on_failure(retries=3, delay=3)  # Retries 5 times with a 3-second delay
def fetch_page_html(*, url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    return response.content


def parse_html_as_beautifulsoup(*, html_content: bytes)-> bs:
    soup_content = bs(html_content, "lxml")
    return soup_content



def get_cars_info_soup(*, soup_page_content: bs)-> List:
    main_content_list = soup_page_content.find_all(name="main")
    cars_content_soup = [car for main_content in main_content_list 
                         for car in main_content.find_all(attrs={"class": "row Vehicle py-4"})]
    
    return cars_content_soup


def get_car_image_url(*, car_info_soup: bs)-> str:
    image_info_list = car_info_soup.find_all(name= "img")
    
    image_urls = [img_tag.get("src", "") for img_tag in image_info_list if "src" in img_tag.attrs]
    
    return " ".join(image_urls)


def get_car_full_description_url(*, car_info_soup: bs)-> str:
    anchor_tag_content = car_info_soup.find_all("a")
    anchor_links = [anchor_tag.get("href", "") for anchor_tag in anchor_tag_content]
    description_urls = list(set(anchor_links))
    return " ".join(description_urls)


def get_car_name(*, car_info_soup: bs)-> str:
    name_unparsed = car_info_soup.h4.text
    car_name = " ".join(name_unparsed.split())
    return car_name


def get_car_interior_features(*, car_info_soup: bs)-> str:
    return car_info_soup.small.text


def get_car_price(*, car_info_soup: bs)-> float:
    pattern = r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?"
    price_list = re.findall(pattern, car_info_soup.p.text)
    if price_list:
        unparsed_price = price_list[0]
        price = unparsed_price.replace("$", "").replace(",", "")
        return price
    
    return 0.00
    

def get_car_current_mileage(*, car_info_soup: bs) -> float:
    pattern = r"\d{1,3}(?:,\d{3})*"
    mileage_list = car_info_soup.find_all(name="p", attrs={"class": "h5"})

    mileage_val = []
    for mileage in mileage_list:
        # Find all mileage values in the text and flatten the list
        found_mileage = re.findall(pattern, mileage.text)
        mileage_val.extend(found_mileage)

    # Convert to floats after removing commas
    mileage_val = [float(m.replace(',', '')) for m in mileage_val]
    
    if mileage_val:
        return mileage_val[0]
    return 0.00


def get_car_exterior_features(*, car_info_soup: bs)-> Dict[str, str]:
    features_soup_list = car_info_soup.find_all(name = "p", attrs = {"class": "mb-1"})
    features_text_list = [feature_soup.text for feature_soup in features_soup_list]
    features_dict = {feature.split(":")[0] : feature.split(":")[1] for feature in features_text_list}
    features_dict = {feature.replace("\n", "").strip() : value.replace("\n", "").strip() for feature, value in features_dict.items()}
    return features_dict


def get_finance_promise(*, car_info_soup: bs)-> str:
    promise_soup_list = car_info_soup.find_all(name = "ul")
    promise_text_list = [soup_text.text.replace("\n", "") for soup_text in promise_soup_list]
    promise_text_list = [text.replace("check icon", "").replace("\n", "") for text in promise_text_list]
    promise_text = "".join(promise_text_list)
    return " ".join(promise_text.split())


def initialize_data_dict()->Dict[str, List]:
    data_dict = {
        "id": [],
        "car_name": [],
        "car_price": [],
        "car_image_url": [],
        "full_description_url": [],
        "interior_features": [],
        "exterior_features": [],
        "current_mileage": [],
        "finance_promise": [],
        "creation_time": []
                       }
    return data_dict

def get_last_page(*, soup_page_content: bs) -> int:
    page_numbers_soup_list = soup_page_content.find_all(name="a", attrs={"class": "page-numbers"})
    
    page_numbers = [int(soup.text) if soup.text.isdigit() else 0 for soup in page_numbers_soup_list]
    
    last_page = max(page_numbers, default=0)
    
    return int(last_page)


def fill_data_dict_with_page_content(*, data_dict: Dict[str, List], cars_info: List[bs])-> Dict[str, List]:
    for car_info in cars_info:
        data_dict["id"].append(str(uuid.uuid4()))
        
        data_dict["car_name"].append(get_car_name(car_info_soup = car_info))
        
        data_dict["car_price"].append(get_car_price(car_info_soup = car_info))
        
        data_dict["current_mileage"].append(get_car_price(car_info_soup = car_info))
        
        data_dict["car_image_url"].append(get_car_image_url(car_info_soup = car_info))
        
        data_dict["full_description_url"].append(get_car_full_description_url(car_info_soup = car_info))
        
        data_dict["interior_features"].append(get_car_interior_features(car_info_soup = car_info))
        
        data_dict["exterior_features"].append(get_car_exterior_features(car_info_soup = car_info))
        
        data_dict["finance_promise"].append(get_finance_promise(car_info_soup = car_info))
        
        data_dict["creation_time"].append(datetime.now())
    
    return data_dict

"""PAGE CONTENT EXTRACTION"""

data_dict = initialize_data_dict()

html_page_content = fetch_page_html(url = BASE_URL)

soup_page_content = parse_html_as_beautifulsoup(html_content=html_page_content)

last_page = get_last_page(soup_page_content= soup_page_content)

for page_num in range(1, last_page + 1):
    print(f"Working on content for page {page_num}")
    
    page_url = BASE_URL + f"?dsp_page={page_num}"
    
    html_page_content = fetch_page_html(url = page_url)

    soup_page_content = parse_html_as_beautifulsoup(html_content=html_page_content)
    print(f"Content on page {page_num} extracted successfully")
    
    print("Parsing the data and extracting car content")
    page_cars_info = get_cars_info_soup(soup_page_content = soup_page_content)
    
    fill_data_dict_with_page_content(data_dict= data_dict, cars_info= page_cars_info)
    print(f"Page {page_num} completed\n")


final_df = pd.DataFrame(data_dict)



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
    table_name = 'website'
    
    return {
        'sql_server': sql_server,
        'sql_database': sql_database,
        'sql_username': sql_username,
        'sql_password': sql_password,
        'sql_driver': sql_driver
    }

# Function to load DataFrame to SQL database
def load_data_to_sql(final_df, table_name, env_dir, schema_name='autocheck'):
    try:
        # Convert the exterior_features column to a JSON string
        final_df['exterior_features'] = final_df['exterior_features'].apply(json.dumps)

        credentials = get_db_credentials(env_dir)
        connection_string = f"mssql+pyodbc://{credentials['sql_username']}:{credentials['sql_password']}@{credentials['sql_server']}/{credentials['sql_database']}?driver={credentials['sql_driver']}"
        engine = create_engine(connection_string)
        
        # Append DataFrame to SQL table
        final_df.to_sql(table_name, engine, schema=schema_name, if_exists='append', index=False)
        
        print(f"Data appended to Azure SQL Database table {schema_name}.{table_name} successfully.")
    except Exception as e:
        print(f"Error writing to SQL Database: {str(e)}")

# Check if DataFrame is available before attempting to load it to SQL
if final_df is not None:
    table_name = 'website'  # Define your table name here
    load_data_to_sql(final_df, table_name, env_dir)
