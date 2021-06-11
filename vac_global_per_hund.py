#%%
from modules.yachtCharter import yachtCharter
import pandas as pd 
import os 
import datetime

here = os.path.dirname(__file__)
data_path = os.path.dirname(__file__) + "/data/"
output_path = os.path.dirname(__file__) + "/output/"

# fillo = f"{data_path}"
#%%

print("updating select countries vaccine chart")

row_csv = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv'

# 'location', 'iso_code', 'date', 'total_vaccinations',
#        'people_vaccinated', 'people_fully_vaccinated',
#        'daily_vaccinations_raw', 'daily_vaccinations',
#        'total_vaccinations_per_hundred', 'people_vaccinated_per_hundred',
#        'people_fully_vaccinated_per_hundred',
#        'daily_vaccinations_per_million'


df = pd.read_csv(row_csv)

#%%
includes = ["Australia",'United States', "European Union","South Korea", "Japan"]

ow = df.loc[df['location'].isin(includes)].copy()

## ADD BACK THE MISSING UK DATES TO OWID

graun_uk = pd.read_json(f'{here}/vaxx-data-2020.json')
owid_uk = df.loc[df['location'] == "United Kingdom"].copy()

# print(owid_uk)

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

# print(uk)

ow = ow.append(uk)

ow = ow[['date', 'location', 'total_vaccinations_per_hundred']]

ow['date'] = pd.to_datetime(ow['date'])
latest_date = ow['date'].max()

# latest_date = datetime.datetime.strptime(latest_date, "%Y-%m-%d")
latest_date = datetime.datetime.strftime(latest_date, "%d/%m/%Y")
# print(ow)
# print(latest_date)

ow['date'] = ow['date'].dt.strftime('%Y-%m-%d')
pivoted = ow.pivot(index="date", columns='location')['total_vaccinations_per_hundred'].reset_index()

# pivoted.set_index('date', inplace=True)
# pivoted.index.name = None
# # print(latest_date)
# print(pivoted)
# print(pivoted.columns)

#%%


def makeLineChart(df):

    template = [
            {
                "title": "Covid-19 vaccine rollout to date for selected countries",
                "subtitle": f"Showing vaccine doses administered per hundred people to date in each country or region. Latest data as of {latest_date}.",
                "footnote": "",
                "source": "Our World in Data",
                "dateFormat": "%Y-%m-%d",
                "yScaleType":"",
                "xAxisLabel": "Date",
                "yAxisLabel": "Doses per hundred people",
                "minY": "",
                "maxY": "",
                # "periodDateFormat":"",
                "margin-left": "50",
                "margin-top": "15",
                "margin-bottom": "20",
                "margin-right": "20",
                "breaks":"no"
            }
        ]
    key = []
    periods = []
    labels = []
    chartId = [{"type":"linechart"}]
    df.fillna('', inplace=True)
    # df = df.reset_index()
    chartData = df.to_dict('records')
    # print(since100.head())
    # print(chartData)
    # yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], options=[{"colorScheme":colours, "lineLabelling":"FALSE"}], chartName="state_rollout_per_hundred_test")
    yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], options=[{"colorScheme":"guardian", "lineLabelling":"FALSE"}], chartName="vac_global_per_hundred")


makeLineChart(pivoted)
# %%
