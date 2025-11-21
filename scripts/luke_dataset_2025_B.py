'''
Converts Luke's metsähanhi-data into FinBIF Data Bank secondary data format.
Mikko Heikkinen 2025-11-21

NOTE:
Add observer MA-code on row ~78.

'''

import pandas as pd

'''
Input data has these columns:
Ruutu;Laji;Pesimävarmuusindeksi;Vuosi;Aineisto;Lähde;Havainnoijat

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

file_path = './secret/input.csv'
df = pd.read_csv(file_path, delimiter=';', na_values=[], keep_default_na=False)

row_count = len(df)

# List unique values of laji column
print(df['Laji'].unique())

# ADD IDENTIFIER
# NOTE: this format must not be changed, otherwise the ID will not be persistent if dataset is updated.

# Add a new "ID" column by concatenating "YKJ", "laji" and "vuosi" with a dash as a separator. This should be persistent if dataset is updated.
df['ID - Submissions'] = df['Ruutu'].astype(str) + '-' + df['Laji'] + '-' + df['Vuosi'].astype(str)
df['ID - Submissions'] = df['ID - Submissions'].str.replace(':', '-') # Replaces coordinate serparator
df['ID - Submissions'] = df['ID - Submissions'].str.lower() # Species names to lowercase

# Fill in date columns based on year column
df['Start date@dd'] = 1
df['Start date@mm'] = 1
df['Start date@yyyy'] = df['Vuosi']
df['End date@dd'] = 21
df['End date@mm'] = 11 # Use today, since future dates are not allowed
df['End date@yyyy'] = df['Vuosi']

# Split YKJ to coordinates@N and coordinates@E
df['Coordinates@N'] = df['Ruutu'].str.split(':').str[0]
df['Coordinates@E'] = df['Ruutu'].str.split(':').str[1]
df['Coordinates@System'] = 'ykj'

# Rename columns to match output format
df.rename(columns={
    'Laji': 'Species - Identification',
    'Pesimävarmuusindeksi': 'Breeding index - Specimen',
    'Aineisto': 'Data source - Submissions',
    'Havainnoijat': 'Observers - Global gathering event'
}, inplace=True)

# Add standard values to columns that are not present in the input data
df['Collection/Keywords - Specimen'] = df['Data source - Submissions']

# Fix observer names
df['Observers - Global gathering event'] = df['Observers - Global gathering event'].str.replace(',', ';')

# Todo: add observer MA-codes
df['Observers - Global gathering event'] = df['Observers - Global gathering event'].str.replace('NAME', 'NAME (MA.code)')

# Remove original columns
df.drop(columns=['Ruutu', 'Lähde', 'Vuosi'], inplace=True)

# Save the dataframe to a CSV file with UTF-8 encoding with BOM
csv_file_path = './secret/output.csv'
df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
