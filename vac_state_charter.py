import pandas as pd 
import requests
import os
import ssl
from modules.yachtCharter import yachtCharter
import numpy as np 


state_json = "https://interactive.guim.co.uk/2021/02/coronavirus-widget-data/state-vaccine-rollout.json"

print("updating re-indexed state rollout chart")

# fixes ssl error on OSX???

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

# Population counts:
oz_pop = 25693.1 * 1000
nsw_pop = 8166.4* 1000
vic_pop = 6680.6* 1000
qld_pop = 5184.8* 1000
sa_pop = 1770.6* 1000
wa_pop = 2667.1* 1000
tas_pop = 541.1* 1000
nt_pop = 246.5* 1000
act_pop = 431.2* 1000
# source: https://www.abs.gov.au/statistics/people/population/national-state-and-territory-population/sep-2020

df = pd.read_json(state_json)
df = df.loc[df['CODE'] != "AUS"]
df = df[['REPORT_DATE', 'CODE', 'PREV_VACC_DOSE_CNT']]
df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
df = df.sort_values(by="REPORT_DATE", ascending=True)


## Get last date for updated date in subhead
last_date = df.iloc[-1:]["REPORT_DATE"].dt.strftime("%Y-%m-%d").values[0]

# areas = [('NT', nt_pop), ('AUS', oz_pop), ('NSW', nsw_pop), ('VIC', vic_pop), ('ACT', act_pop), ('WA', wa_pop), ('SA', sa_pop), ('TAS', tas_pop), ('QLD', qld_pop)]
areas = [('NT', nt_pop), ('NSW', nsw_pop), ('VIC', vic_pop), ('ACT', act_pop), ('WA', wa_pop), ('SA', sa_pop), ('TAS', tas_pop), ('QLD', qld_pop)]


pivoted = df.pivot(index='REPORT_DATE', columns='CODE')['PREV_VACC_DOSE_CNT'].reset_index()

## Calculate doses per hundred people
# pivoted['Day'] = pivoted.index
for area in areas:
    pivoted[area[0]] = pd.to_numeric(pivoted[area[0]])
    pivoted[area[0]] = round((pivoted[area[0]]/area[1])*100, 2)


pivoted = pivoted.replace({'0':np.nan, 0:np.nan})
pivoted.columns.name = None

pivoted.drop(columns={'REPORT_DATE'}, inplace=True)

pivoted.to_csv('state-comparison.csv', index=False)




def makeSince100Chart(df):
   
    template = [
            {
                "title": "Australia's state vaccine rollout",
                "subtitle": f"Showing the Covid-19 vaccine doses administered per hundred people. Last updated {last_date }.",
                "footnote": "",
                "source": "Covidlive.com.au, Australian Bureau of Statistics",
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
                "margin-right": "20",
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
    # print(chartData)
    yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], options=[{"colorScheme":"guardian", "lineLabelling":"TRUE"}], chartName="state_rollout_per_hundred")

makeSince100Chart(pivoted)
