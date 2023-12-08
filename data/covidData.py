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
    response_desc = kResponseOrdinalMeaning[kResponseOrdinalMeaning['Name'] == column]
    if response_desc.empty:
        label = column.capitalize()
        label = label.replace("_", " ")
    else:
        label = response_desc['Description'].iloc[0]

    return label


def label_map(cols):
    result = []
    for col in cols:
        result.append({'label': get_label(col), 'value': col})
    return result


def new_legend(fig, names):
    for item in names:
        for i, elem in enumerate(fig.data[0].labels):
            if elem == item:
                fig.data[0].labels[i] = get_label(item)
    return fig


SIDEBAR_STYLE = {
    "margin-bottom": "2rem",
}

STYLE = {
    "margin-top": "1rem",
    "margin-left": "1rem",
    "margin-right": "1rem",
    "margin-bottom": "1rem",
}
