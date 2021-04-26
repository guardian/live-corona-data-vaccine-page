import pandas as pd 
from modules.syncData import syncData

row_csv = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv'

print("updating vaccine chloropleth")


owid = pd.read_csv(row_csv)

latest = owid.drop_duplicates(subset="location",keep="last")

latest = latest[['location', 'iso_code', 'date', 'total_vaccinations_per_hundred', 'daily_vaccinations_per_million']]

latest = latest.dropna()

latest = latest.loc[~latest['iso_code'].str.contains('OWID')]

jsony = latest.to_json(orient="records")

syncData(jsony, "covidfeeds", "world-vaccine-chloropleth")

# print(latest)