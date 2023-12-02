import pandas as pd

kCovidDf = pd.read_csv('../data/owid-covid-data.csv', parse_dates=['date'])
kResponseTrackerDf = pd.read_csv('../data/OxCGRT_compact_national_v1.csv', parse_dates=['Date'])
kResponseOrdinalMeaning = pd.read_csv('../data/OxCGRT_ordinal_data_meaning.csv', delimiter=';')
k_iso_code_country_name_df = kResponseTrackerDf[['CountryName', 'CountryCode']].drop_duplicates()
k_iso_to_name = k_iso_code_country_name_df.set_index('CountryCode').to_dict()['CountryName']
k_name_to_iso = k_iso_code_country_name_df.set_index('CountryName').to_dict()['CountryCode']

iso_code_country_name_df = kCovidDf[['location', 'iso_code']].drop_duplicates()
k_iso_to_name_owid = iso_code_country_name_df.set_index('iso_code').to_dict()['location']
k_name_to_iso_owid = iso_code_country_name_df.set_index('location').to_dict()['iso_code']