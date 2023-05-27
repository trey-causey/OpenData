import pandas as pd
import requests
import json
# import credentials as cred
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

# Setting header and data components for API request
headers = {
    'Authorization': os.environ.get('AUTHORIZATION'),
    'Accept': 'application/json',
    'Content-type': 'application/json',
}

data = {
    'app_token': os.environ.get('APPTOKEN'),
}

# Performing API call to ChattaData's TN Child Care dataset. If an error occurs, the program exits
try:
    response = requests.get('https://www.chattadata.org/resource/3gj8-3ijm.json?county=HAMILTON', data=data)
    response.raise_for_status()
except requests.exceptions.RequestException as err:
    print(f'The following error occurred while making the get request: {err}')
    raise SystemExit()

tnchildcare_df = pd.json_normalize(response.json())

u_count = tnchildcare_df.value_counts('agency_name')
print(u_count.to_string())

def tnchildcare_dfMods(tnchildcare_df):

    # Converting date fields to a date/time format
    tnchildcare_df[['license_approval_date', 'date_open']] = tnchildcare_df[['license_approval_date', 'date_open']].apply(pd.to_datetime, yearfirst=True, unit='ns', errors='coerce') #Some dates are invalid so set errors to 'coerce' to fill with NaN

    # Separating the Location Point column into individual Latitude and Longitude fields
    tnchildcare_df[['long', 'lat']] = tnchildcare_df['location_point.coordinates'].apply(lambda x: pd.Series(x))

    # Extracting the alpha interavals from the age columns to create number and category columns
    tnchildcare_df[['minimum_age_num', 'minimum_age_cat']] = tnchildcare_df['minimum_age'].str.extract(r'(\d+)([a-zA-Z]+)')
    tnchildcare_df[['maximim_age_num', 'maximum_age_cat']] = tnchildcare_df['maximum_age'].str.extract(r'(\d+)([a-zA-Z]+)')

    # Standardizing minimum age into a yearly basis
    tnchildcare_df.loc[tnchildcare_df['minimum_age_cat'] == 'WK', 'minimum_age_num'] = tnchildcare_df['minimum_age_num'].astype(int) / 52
    tnchildcare_df.loc[tnchildcare_df['minimum_age_cat'] == 'MO', 'minimum_age_num'] = tnchildcare_df['minimum_age_num'].astype(int) / 12
    tnchildcare_df.loc[tnchildcare_df['minimum_age_cat'] == 'YR', 'minimum_age_num'] = tnchildcare_df['minimum_age_num'].astype(int)

    # Standardizing the format of Agency Name
    tnchildcare_df['agency_name'] = tnchildcare_df['agency_name'].str.title()

    # Converting Open and Close Times into military format for future analysis
    tnchildcare_df['open_time'] = pd.to_datetime(tnchildcare_df['open_time'], format='%I:%M %p').dt.strftime('%H:%M')
    tnchildcare_df['close_time'] = pd.to_datetime(tnchildcare_df['close_time'], format='%I:%M %p').dt.strftime('%H:%M')

    return tnchildcare_df
