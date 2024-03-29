import pandas as pd
from modules.yachtCharter import yachtCharter
import datetime
import numpy as np
import os, ssl
import math

here = os.path.dirname(__file__)


#%%

print("updating re-indexed vaccine chart")

# fixes ssl error on OSX???

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

oz_json = 'https://interactive.guim.co.uk/2021/02/coronavirus-widget-data/aus-vaccines.json'
row_csv = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv'

#%%
# oz_pop = 25203000
# # https://ourworldindata.org/grapher/population

# # Sort out Australia's vaccination per hundred

# oz = pd.read_json(oz_json)

# #%%
# oz['REPORT_DATE'] = pd.to_datetime(oz['REPORT_DATE'])
# # oz = oz.sort_values(by ="REPORT_DATE", ascending=True)

# oz['total_vaccinations_per_hundred'] = (oz["VACC_DOSE_CNT"] / oz_pop) * 100
# oz['location'] = "Australia"
# oz = oz.sort_values(by="REPORT_DATE", ascending=True)
# last_date = oz.iloc[-1:]["REPORT_DATE"].dt.strftime("%d %B %Y").values[0]

# # last_date = datetime.datetime.strftime(last_date, "%d %B %Y")

# print(oz)

#%%
# # last_date = datetime.datetime.strptime(last_date, "%Y-%m-%d %H:%M:%S")
# # last_date = last_date.strftime("%Y-%m-%d")
# # print(last_date)

# oz.rename(columns={"REPORT_DATE":"date"}, inplace=True)

# oz = oz[['location', 'date', 'total_vaccinations_per_hundred']]

# oz = oz.loc[oz['total_vaccinations_per_hundred'] > 0]


## Load Our World

our_world = pd.read_csv(row_csv, parse_dates=['date'])
our_world = our_world.sort_values(by="date", ascending=True)

## Work out UK

graun_uk = pd.read_json(f'{here}/vaxx-data-2020.json')
owid_uk = our_world.loc[our_world['location'] == "United Kingdom"]

graun_uk['allDosesByPublishDate'] = graun_uk['allDosesByPublishDate'].cumsum()
graun_uk.columns = ['date', 'total_vaccinations']

owid_uk = owid_uk.loc[owid_uk['date'] > "2021-01-10"]

owid_uk = owid_uk[['date', 'total_vaccinations']]

uk = graun_uk.append(owid_uk)

## Work out UK dose per hundred
uk_pop = 66650000
## https://ourworldindata.org/grapher/population

uk['location'] = "United Kingdom"
uk['total_vaccinations_per_hundred'] = (uk['total_vaccinations'] / uk_pop) * 100
uk = uk[['date','total_vaccinations_per_hundred', 'location']]


# Sort out everyone else from Our World in Data


countries = ["Australia", 'United States', "European Union", "South Korea", "Japan"]
our_world = our_world.loc[our_world["location"].isin(countries)]

our_world = our_world[['date','total_vaccinations_per_hundred', 'location']]


our_world = our_world.append(uk)

# print(our_world['location'].unique())


# # Append Australia to rest of the world

# combined = our_world.append(oz)
# combined = combined.sort_values(by="date", ascending=True)
# combined['date'] = combined['date'].dt.strftime('%Y-%m-%d')

#%%
# Pivot the dataframe

pivoted = our_world.pivot(index="date", columns='location')['total_vaccinations_per_hundred'].reset_index()
pivoted = pivoted.replace({'0':np.nan, 0:np.nan})
pivoted = pivoted.ffill(axis=0)

#%%
# print(pivoted)

includes = ["Australia",'United States', "European Union","South Korea", "Japan", 'United Kingdom']

#%%

sinceDayZero = pd.DataFrame()

for col in includes:

	start = pivoted[col].notna().idxmax()

	tempSeries = pivoted[col][start:]

	tempSeries = tempSeries.replace({0:np.nan})

	tempSeries = tempSeries.reset_index()

	tempSeries = tempSeries.drop(['index'], axis=1)

	sinceDayZero = pd.concat([sinceDayZero, tempSeries], axis=1)


## Automatically work out cutoff (current number of days in rollout rounded up to nearest 10):

rollout_begin = datetime.date(2021, 2, 22)
today = datetime.datetime.today().date()

days_running = today - rollout_begin
days_running = days_running.days

cut_off = math.ceil(days_running/10) * 10

# Cut dataset

upto = sinceDayZero[:cut_off].copy()

# upto.to_csv('country-comparison.csv')

last_date = our_world.iloc[-1:]["date"].dt.strftime("%d %B %Y").values[0]

#%%

def makeSince100Chart(df):

    template = [
            {
                "title": "Covid-19 vaccine doses per hundred people for selected countries",
                "subtitle": f"Showing up to the first {cut_off} days starting from the first day of recorded vaccinations in each country or region. Last updated {last_date }",
                "footnote": "",
                "source": "Covidlive.com.au, Our World in Data ",
                "dateFormat": "",
                "yScaleType":"",
                "xAxisLabel": "Days since first vaccination",
                "yAxisLabel": "Doses per hundred people",
                "minY": "",
                "maxY": "",
                "periodDateFormat":"",
                "margin-left": "50",
                "margin-top": "15",
                "margin-bottom": "20",
                "margin-right": "10",
                "breaks":"no"
            }
        ]
    key = []
    periods = []
    labels = []
    chartId = [{"type":"linechart"}]
    df.fillna('', inplace=True)
    df = df.reset_index()
    chartData = df.to_dict('records')
    # print(since100.head())

    yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], options=[{"colorScheme":"guardian", "lineLabelling":"FALSE"}], chartName="vaccines_per_hundred_reindexed_to_50")

makeSince100Chart(upto)
