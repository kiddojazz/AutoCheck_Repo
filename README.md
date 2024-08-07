# Data Engineering Assessment Documentation

## Introduction
Autochek Africa is an Automotive Technology development company that builds solutions aimed at enabling and enhancing commerce within the automotive sector. We focus on solutions that improve access to Auto loans, quality maintenance / after-sales services, warranty solutions, and transactional marketplaces.

## Project Architecture
We are tasked to create an ETL pipeline that reads data from a particular folder. Data are dropped on a daily, we need to create a logic that picks the latest file based on the last modified data, performs all necessary transformations, and loads the data into an Azure SQL Database (Data Warehouse).

The entire process needs to be automated and monitored. We are going to create a CRON job in a Windows Server (VM) and automate the Python script using a .bat file in the process.
![alt text]([image.jpg](https://github.com/kiddojazz/AutoCheck_Repo/blob/master/Images/arc_1.png)

## Alternative Architecture
The IaaS approach was used due to cost saving, you can consider other approaches like modern data stack or Platform as a Service (AWS, Azure, or GCP).
![alt text]([image.jpg](https://github.com/kiddojazz/AutoCheck_Repo/blob/master/Images/arc_2.png)

# Data Gathering
## Introduction
We are expected to perform data by scraping data from an auto-mobile site and getting the necessary fields. The scrapped data are standardized and loaded into the Azure SQL Database.

Using the required Libraries, we need to automate the entire process. For this, we will be using the IaaS approach where all the necessary components are stored in a Virtual Machine of Azure Infrastructure as a Service.

## Project Architecture
The image below explains the entire process that will be carried out. A CRON job process is done on the Batch file which is used to run the Web scraping script and push the data into Azure SQL Database and at the same create a log file for the entire process.
![alt text](https://github.com/kiddojazz/AutoCheck_Repo/blob/master/Images/arc_3.png)

# Alternative
An alternative model can be done depending on the level of expertise and cost the organization is willing to take on.
![alt text](https://github.com/kiddojazz/AutoCheck_Repo/blob/master/Images/arc_4.png)
