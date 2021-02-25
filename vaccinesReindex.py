import pandas as pd 
from modules.yachtCharter import yachtCharter
import datetime 
import numpy as np 

import os, ssl

# fixes ssl error on OSX???

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

oz_json = 'https://interactive.guim.co.uk/2021/02/coronavirus-widget-data/aus-vaccines.json'
row_csv = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv'

oz_pop = 25203000
# https://ourworldindata.org/grapher/population

# Sort out Australia's vaccination per hundred

oz = pd.read_json(oz_json)

oz['REPORT_DATE'] = pd.to_datetime(oz['REPORT_DATE'])
# oz = oz.sort_values(by ="REPORT_DATE", ascending=True)

oz['total_vaccinations_per_hundred'] = (oz["VACC_DOSE_CNT"] / oz_pop) * 100
oz['location'] = "Australia"
oz = oz.sort_values(by="REPORT_DATE", ascending=True)
last_date = str(oz[-1:]["LAST_UPDATED_DATE"].values[0])
last_date = datetime.datetime.strptime(last_date, "%Y-%m-%d %H:%M:%S")
last_date = last_date.strftime("%Y-%m-%d")
# print(last_date)

oz.rename(columns={"REPORT_DATE":"date"}, inplace=True)

oz = oz[['location', 'date', 'total_vaccinations_per_hundred']]

oz = oz.loc[oz['total_vaccinations_per_hundred'] > 0]

# Sort out everyone else from Our World in Data

our_world = pd.read_csv(row_csv, parse_dates=['date'])
our_world = our_world.sort_values(by="date", ascending=True)

countries = ['Israel', 'United Kingdom', 'United States', "European Union"]
our_world = our_world.loc[our_world["location"].isin(countries)]

our_world = our_world[['date','total_vaccinations_per_hundred', 'location']]

# Append Australia to rest of the world

combined = our_world.append(oz)
combined = combined.sort_values(by="date", ascending=True)
combined['date'] = combined['date'].dt.strftime('%Y-%m-%d')

# Pivot the dataframe

pivoted = combined.pivot(index="date", columns='location')['total_vaccinations_per_hundred'].reset_index()

# print(pivoted)

def makeSince100Chart(df, includes):
    includes.append("Australia")

    since100 = pd.DataFrame()

    lastUpdatedInt = df.index[-1]
    # print(lastUpdatedInt)

    # for col in includes:
    #     inter = df[col].copy()
    #     print(inter)

    for col in includes:
        # print(col)
        start = df[col].notna().idxmax()

        tempSeries = df[col][start:]

        tempSeries = tempSeries.replace({0:np.nan})

        tempSeries = tempSeries.reset_index()

        tempSeries = tempSeries.drop(['index'], axis=1)

        since100 = pd.concat([since100, tempSeries], axis=1)



    template = [
            {
                "title": "Covid-19 vaccinations per hundred people",
                "subtitle": f"Last updated {last_date }",
                "footnote": "",
                "source": "Covidlive.com.au, Our World in Data ",
                "dateFormat": "",
                "yScaleType":"",
                "xAxisLabel": "Days since first vaccination",
                "yAxisLabel": "Vaccinations per hundred people",
                "minY": "",
                "maxY": "",
                "periodDateFormat":"",
                "margin-left": "50",
                "margin-top": "30",
                "margin-bottom": "20",
                "margin-right": "20"
            }
        ]
    key = []
    periods = []
    labels = []
    chartId = [{"type":"linechart"}]
    since100.fillna('', inplace=True)
    since100 = since100.reset_index()
    chartData = since100.to_dict('records')
    # print(since100.head())

    yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], 
    options=[{"colorScheme":"guardian", "lineLabelling":"TRUE"}], chartName="vaccines_per_hundred_reindexed")

makeSince100Chart(pivoted, countries)