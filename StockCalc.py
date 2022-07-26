from fileinput import close
import requests
import json
import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
import datetime as dt
import os
import csv
from csv import writer
from csv import reader
from urllib.request import urlretrieve
from sqlalchemy import true

from api_keys import alpha_key

# Delete csv files
for folder, subfolders, files in os.walk('Stock_Growth/csv_files/'):        
    for file in files: 
        if file.endswith('.csv'): 
            path = os.path.join(folder, file) 
            os.remove(path)

# Create temp.csv file for headers
header = ['timestamp' , 'open' , 'high' , 'low' , 'close' , 'adjusted close' , 'volume' , 'dividend amount' , 'ticker' , 'current value' , 'sort' , 'value' , 'inflation' , 'value_afi']

with open('Stock_Growth/csv_files/temp.csv', 'w', encoding='UTF8') as f:
    writer1 = csv.writer(f)

    # write the header
    writer1.writerow(header)


def add_column_in_csv(input_file, output_file, transform_row):
    """ Append a column in existing csv using csv.reader / csv.writer classes"""
    # Open the input_file in read mode and output_file in write mode
    with open(input_file, 'r') as read_obj, \
            open(output_file, 'w', newline='') as write_obj:
        # Create a csv.reader object from the input file object
        csv_reader = reader(read_obj)
        # Create a csv.writer object from the output file object
        csv_writer = writer(write_obj)
        # Read each row of the input csv file as list
        for row in csv_reader:
            # Pass the list / row in the transform function to add column text for this row
            transform_row(row, csv_reader.line_num)
            # Write the updated row / list to the output file
            csv_writer.writerow(row)

# Define desired stocks with ticker. Loop until input equals "null"
SYMBs = []
SYMB_Input = []
while SYMB_Input != "":
    SYMB_Input = input("Enter stock symbol. Press Enter/Return key when finished:")
    SYMBs.append(SYMB_Input)

# //////////////////////////INFLATION\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#

# Inflation USD - Pull and save inflation data for US as "temp_inf.csv"
infl = pd.read_csv("https://www.alphavantage.co/query?function=INFLATION&apikey=" + alpha_key + "&datatype=csv")   
infl.head()

infl.to_csv('Stock_Growth/csv_files/temp_inf.csv')

#Change Date Formatting
with open("Stock_Growth/csv_files/temp_inf.csv", 'r') as source:
    with open("Stock_Growth/csv_files/temp_inf1.csv", 'w') as result:
        writer1 = csv.writer(result, lineterminator='\n')
        reader1 = csv.reader(source)
        source.readline()
        for row in reader1:
            ts = dt.datetime.strptime(row[1], "%Y-%m-%d").strftime("%Y-%m")
            
            row[1]=ts
            if ts != "":
                writer1.writerow(row)
source.close()
result.close()

# read contents of csv file
file = pd.read_csv("Stock_Growth/csv_files/temp_inf1.csv")  
# adding header
headerList = ['sort' , 'timestamp' , 'value']  
# converting data frame to csv
file.to_csv("Stock_Growth/csv_files/temp_inf3.csv", header=headerList, index=False)

# ////////////////////// STOCKS \\\\\\\\\\\\\\\\\\\\\\\\\\\

# Stock performance - Loop through user defined stocks
for SYMB in SYMBs:
    if SYMB == "":
        break
    # Pull csv and save as "temp_stk"
    stk = pd.read_csv("https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol=" + SYMB +"&apikey=" + alpha_key + "&datatype=csv")  
    stk.head()
    stk.to_csv('Stock_Growth/csv_files/temp_stk.csv', index=False)

    # Add column with stocks' ticker
    ticker = SYMB
    add_column_in_csv('Stock_Growth/csv_files/temp_stk.csv', 'Stock_Growth/csv_files/temp_stk1.csv', lambda row, line_num: row.append(ticker))
    
    # Sort by date
    csvData = pd.read_csv("Stock_Growth/csv_files/temp_stk1.csv")
    csvData['timestamp'] = csvData['timestamp'].astype('datetime64[ns]')
    csvData.sort_values(by='timestamp', inplace=True)

    csvData.to_csv("Stock_Growth/csv_files/temp_stk2.csv", index=False)

#Change Date Formatting
    with open("Stock_Growth/csv_files/temp_stk2.csv", 'r') as source:
        with open("Stock_Growth/csv_files/temp_stk3.csv", 'w') as result:
            writer2 = csv.writer(result, lineterminator='\n')
            reader2 = csv.reader(source)
            source.readline()
            for row in reader2:
                ts = dt.datetime.strptime(row[0], "%Y-%m-%d").strftime("%Y-%m")
            
                row[0]=ts
                if ts != "":
                    writer2.writerow(row)
    source.close()
    result.close()

    # read contents of csv file
    file = pd.read_csv("Stock_Growth/csv_files/temp_stk3.csv")  
    # adding header
    headerList = ['timestamp' , 'open' , 'high' , 'low' , 'close' , 'adjusted close' , 'volume' ,'dividend amount' , 'ticker']  
    # converting data frame to csv
    file.to_csv("Stock_Growth/csv_files/temp_stk4.csv", header=headerList, index=False)

    # Calculate Divident Growth
    base_value = 1
    c = []
    df1 = pd.read_csv('Stock_Growth/csv_files/temp_stk4.csv')
    for i in range(len(df1['dividend amount'])):
        base_value = base_value / df1['close'][i] * df1['dividend amount'][i]  + base_value
        c.append(base_value)
    df1['current value'] = c
    df1.to_csv('Stock_Growth/csv_files/temp_stk5.csv', index=False)

    # Merge Stock and Inflation data
    data1 = pd.read_csv('Stock_Growth/csv_files/temp_stk5.csv')
    data2 = pd.read_csv('Stock_Growth/csv_files/temp_inf3.csv')
  
    # using merge function by setting how='left'
    output2 = pd.merge(data1, data2, 
                    on='timestamp', 
                    how='left')

    # converting data frame to csv
    output2.to_csv('Stock_Growth/csv_files/temp_stk6.csv', index=False)

    # conver NaN values to 0
    df3 = pd.read_csv('Stock_Growth/csv_files/temp_stk6.csv')
    df3.fillna(0,inplace=True)
    df3.to_csv('Stock_Growth/csv_files/temp_stk7.csv', index=False)

    # Calculate inflation
    base_value = 1
    c = []
    df1 = pd.read_csv('Stock_Growth/csv_files/temp_stk7.csv')
    for i in range(len(df1['current value'])):
        base_value = base_value - (df1['value'][i] / 100)
        c.append(base_value)
    df1['inflation'] = c
    df1.to_csv('Stock_Growth/csv_files/temp_stk8.csv', index=False)

    # Calculate value_afi
    base_value = 0
    c = []
    df1 = pd.read_csv('Stock_Growth/csv_files/temp_stk8.csv')
    for i in range(len(df1['current value'])):
        base_value = df1['current value'][i] * df1['inflation'][i]
        c.append(base_value)
    df1['value_afi'] = c
    df1.to_csv('Stock_Growth/csv_files/temp_stk9.csv', index=False)

    # Append each individual stock pull to master "temp.csv" file
    csv_list = ['Stock_Growth/csv_files/temp_stk9.csv']
   
    for csv_file in csv_list:
        df = pd.read_csv(csv_file)
        df.to_csv('Stock_Growth/csv_files/temp.csv', mode ='a', header=False, index=False)

