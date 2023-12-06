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

kCovidDf_without_owid = kCovidDf[~(kCovidDf.iso_code.str.startswith('OWID', na=False))]
merge_1_df = pd.DataFrame()
merge_1_df[['iso_code', 'location', 'date', 'stringency_index']] = (
    kResponseTrackerDf)[['CountryCode', 'CountryName', 'Date', 'StringencyIndex_Average']]
merge_1_df.set_index(['iso_code', 'location', 'date'], inplace=True)
merge_2_df = pd.DataFrame()
merge_2_df[['iso_code', 'location', 'date', 'new_cases_smoothed', 'new_deaths_smoothed']] = \
    kCovidDf[['iso_code', 'location', 'date', 'new_cases_smoothed', 'new_deaths_smoothed']]
merge_2_df[['new_cases_smoothed_per_million', 'new_deaths_smoothed_per_million']] = (
    kCovidDf)[['new_cases_smoothed_per_million', 'new_deaths_smoothed_per_million']]
merge_2_df.set_index(['iso_code', 'location', 'date'], inplace=True)
kCovid_Response = pd.concat([merge_1_df, merge_2_df], axis=1, join='inner')
kCovid_Response.reset_index(inplace=True)

date_format = '%m/%d/%Y'


def get_label(column):
    if column == 'location':
        return 'Countries'
    label = column.capitalize()
    label = label.replace("_", " ")
    return label


def label_map(cols):
    result = []
    for col in cols:
        response_desc = kResponseOrdinalMeaning[kResponseOrdinalMeaning['Name'] == col]
        if response_desc.empty:
            result.append({'label': get_label(col), 'value': col})
        else:
            result.append({'label': response_desc['Description'], 'value': col})
    return result
