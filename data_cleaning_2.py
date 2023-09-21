# Install packages
# !pip install networkx
# !pip install community
# !pip install openpyxl==3.0.7

#%%``

# Import packages
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import community
from datetime import datetime
import pandas as pd
import pandas as pd
import numpy as np
import glob
from datetime import datetime
import bz2 
import pickle
import _pickle as cPickle


#%%``

# Define a function to decompress the pickle and load the file
def decompress_pickle(file):
    data = bz2.BZ2File(file, 'rb')
    data = cPickle.load(data)
    return data

# read the Excel file
df = decompress_pickle("overall network data YTJ.pbz2")

# select the columns that need cleaning
cols_to_clean = ['Author', 'Mentioned Authors', 'Thread Author', 'Thread Entry Type', 'Full Text']

# check the count of rows where the 'Author' column is same as the 'Thread Author' column
print('Number of rows where the Author column is same as the Thread Author column: ', len(df[df['Author'] == df['Thread Author']]))

# flag - check the count of rows where the 'Author' column is same as the 'Thread Author' column and the 'Thread Entry Type' is 'share'
print('Number of rows where the Author column is same as the Thread Author column and the Thread Entry Type is share: ', len(df[(df['Author'] == df['Thread Author']) & (df['Thread Entry Type'] == 'share')]))

# check the data shape before removing the rows
print('Data shape before removing the rows: ', df.shape)

# remove the rows where the 'Author' column is same as the 'Thread Author' column and the 'Thread Entry Type' is 'share'
df = df[~((df['Author'] == df['Thread Author']) & (df['Thread Entry Type'] == 'share'))]

# check the data shape after removing the rows
print('Data shape after removing the rows: ', df.shape)


#%%

# clean the text data in the selected columns
for col in cols_to_clean:
    # convert the text to lowercase
    df[col] = df[col].str.lower()
    # remove "@" symbol from the author and mentioned authors columns
    if col in ['Author', 'Mentioned Authors']:
        df[col] = df[col].str.replace('@', '')
    # remove leading and trailing whitespaces
    df[col] = df[col].str.strip()
    # replace empty cells with an empty string
    df[col] = df[col].fillna('')


#%%

# split the comma-separated mentioned authors into a list of authors
df['Mentioned Authors'] = df['Mentioned Authors'].str.split(',')

# split the comma-separated mentioned authors into a list of authors
df['Thread Author'] = df['Thread Author'].str.split(',')

# combine the list of mentioned authors and the thread author into a single list and rename the column to 'Mentioned Authors'
df['Mentioned Authors'] = df['Mentioned Authors'] + df['Thread Author']

# remove duplicates from the list of Mentioned Authors using *set(). 
df['Mentioned Authors'] = df['Mentioned Authors'].apply(lambda x: list(set(x)))

# remove the empty string from the list of Mentioned Authors
df['Mentioned Authors'] = df['Mentioned Authors'].apply(lambda x: [i for i in x if i != ''])

# print the list of Mentioned Authors
print(df['Mentioned Authors'].head(50))

#%%
# check the count of rows with empty lists in the 'Mentioned Authors' column
print('Number of rows with empty lists in the Mentioned Authors column: ', len(df[df['Mentioned Authors'].apply(lambda x: len(x) == 0 if isinstance(x, list) else False)]))

# check the total count of rows in the dataframe
print('Total number of rows in the dataframe: ', len(df))

# remove rows with empty lists in the 'Mentioned Authors' column 
df = df[df['Mentioned Authors'].apply(lambda x: len(x) > 0 if isinstance(x, list) else True)]

# check the total count of rows in the dataframe
print('Total new number of rows in the dataframe: ', len(df))


#%%
# Let's see how many unique authors we have
print('Number of unique authors: ', len(df['Author'].unique()))

# Let's see how many mentions we have
print('Number of mentions: ', len(df['Mentioned Authors']))

#%%

# let's choose the relevant columns for network analysis
df_network = df[['Author', 'Mentioned Authors']].copy()

# Print the first 5 rows of the dataframe
df_network.head(20)


#%%

# explote the list of mentioned authors into multiple rows
df_network = df_network.explode('Mentioned Authors')

# print the dataframe
print(df_network.head(50))


#%%

# This function is used to print the content to the console and to a log file
def print_to_file(content):
    print(content)
    with open("log.txt", "a") as f:
        print(content, file=f)

# Print the updated number of rows in the dataframe
print_to_file("Updated Data size: {} rows".format(df_network.shape[0]))

#%%

# List only those columns with 0 values and their count and store those columns in a list
empty_cols = [col for col in df.columns if df[col].isnull().sum() != 0]
print(empty_cols)

# Remove the empty_cols from the dataframe
df = df.drop(empty_cols, axis=1)
df.columns

#%%
# Call the final files to be used for network analysis
df_network.to_csv('df_network.csv', index=False)
df.to_csv('df.csv', index=False)

 