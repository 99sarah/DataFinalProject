import pandas as pd

kCovidDf = pd.read_csv('../data/owid-covid-data.csv')
kResponseTrackerDf = pd.read_csv('../data/OxCGRT_compact_national_v1.csv', parse_dates=['Date'])
