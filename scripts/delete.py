'''
Script for deleting all occurrences for a given observer from the FinBIF data warehouse, based on a citable data download file.

First get the citable data download file from FinBIF with filters defining what you want to remove, then unzip it and place the occurrences.txt file to ./data.

This needs a token that has rights to submit DELETE commands for the dataset (collection) these observations are from.
'''

from pathlib import Path
import sys

import pandas as pd
import requests

token = "TOKEN HERE"

url = "https://api.laji.fi/warehouse/push"

ids_file_path = Path(__file__).resolve().parent / "data" / "occurrences.txt"

OBSERVER = "USERNAME HERE"
LIMIT = 100000
BATCH_SIZE = 5_000

# FinBIF data file: English field names, then Finnish labels, then English labels
occurrences = pd.read_csv(
    ids_file_path, sep="\t", dtype=str, skiprows=[1, 2], usecols=["recordedBy", "parentEventID"]
)

unexpected = occurrences[occurrences["recordedBy"] != OBSERVER]
if not unexpected.empty:
    print(f"Error: {len(unexpected)} records have recordedBy other than {OBSERVER}")
    print(unexpected["recordedBy"].value_counts().to_string())
    sys.exit(1)

print(f"Matching records for observer {OBSERVER}: {len(occurrences)}")

parent_ids = occurrences["parentEventID"].dropna().drop_duplicates().head(LIMIT)

print(parent_ids)

identifiers = [f"DELETE {parent_event_id}" for parent_event_id in parent_ids]

if not identifiers:
    print("No parentEventID values to delete")
    sys.exit(1)

if not token:
    print("Error: API token is empty")
    sys.exit(1)

headers = {
    "Content-Type": "text/plain",
    "Authorization": f"Bearer {token}",
    "API-Version": "1",
}

for i in range(0, len(identifiers), BATCH_SIZE):
    batch = identifiers[i : i + BATCH_SIZE]
    payload = "\n".join(batch)
    print(f"Sending batch {i // BATCH_SIZE + 1}: {len(batch)} identifiers")

    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to send DELETE commands: {e}")
        sys.exit(1)

    if response.status_code == 200:
        print(f"Successfully sent DELETE commands for {len(batch)} identifiers")
    else:
        print(f"Failed to send DELETE commands: {response.status_code} - {response.text}")
        sys.exit(1)
