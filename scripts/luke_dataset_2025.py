'''
Converts Luke's riistakolmio-data into FinBIF Data Bank secondary data format.
Mikko Heikkinen 2025-10-31
'''

import pandas as pd

'''
Input data has these columns:
['YKJ', 'laji', 'pesimavarmuusindeksi', 'vuosi', 'Aineisto', 'Lähde'],

Output should have these columns:
ID - Submissions
Observers - Global gathering event
Start date@dd - Global gathering event
Start date@mm - Global gathering event
Start date@yyyy - Global gathering event
End date@dd - Global gathering event
End date@mm - Global gathering event
End date@yyyy - Global gathering event
Coordinates@N - Gathering event
Coordinates@E - Gathering event
Coordinates@System - Gathering event
Species - Identification
Data source - Submissions
Breeding index - Specimen
Collection/Keywords - Specimen
'''

file_path = './secret/riistakolmiodata_lintuatlakseen_2025.txt'
df = pd.read_csv(file_path, delimiter='\t', na_values=[], keep_default_na=False)

row_count = len(df)

# List unique values of laji column
print(df['laji'].unique())

# ADD IDENTIFIER
# NOTE: this format must not be changed, otherwise the ID will not be persistent if dataset is updated.

# Add a new "ID" column by concatenating "YKJ", "laji" and "vuosi" with a dash as a separator. This should be persistent if dataset is updated.
df['ID - Submissions'] = df['YKJ'].astype(str) + '-' + df['laji'] + '-' + df['vuosi'].astype(str)
df['ID - Submissions'] = df['ID - Submissions'].str.replace(':', '-') # Replaces coordinate serparator
df['ID - Submissions'] = df['ID - Submissions'].str.lower() # Species names to lowercase

# Fill in date columns based on year column
df['Start date@dd'] = 1
df['Start date@mm'] = 1
df['Start date@yyyy'] = df['vuosi']
df['End date@dd'] = 31
df['End date@mm'] = 10 # Use today, since future dates are not allowed
df['End date@yyyy'] = df['vuosi']

# Split YKJ to coordinates@N and coordinates@E
df['Coordinates@N'] = df['YKJ'].str.split(':').str[0]
df['Coordinates@E'] = df['YKJ'].str.split(':').str[1]
df['Coordinates@System'] = 'ykj'

# Rename columns to match output format
df.rename(columns={
    'laji': 'Species - Identification',
    'pesimavarmuusindeksi': 'Breeding index - Specimen',
    'vuosi': 'Start date@yyyy',
    'Aineisto': 'Data source - Submissions'
}, inplace=True)

# Add standard values to columns that are not present in the input data
df['Observers - Global gathering event'] = 'Anonyymi'
df['Collection/Keywords - Specimen'] = 'riistakolmio'

# Remove original columns
df.drop(columns=['YKJ', 'Lähde'], inplace=True)

# Save the dataframe to a CSV file with UTF-8 encoding with BOM
csv_file_path = './secret/luke_data.csv'
df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
