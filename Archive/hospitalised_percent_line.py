#%%

import os
import requests
import pandas as pd
from modules.yachtCharter import yachtCharter
import datetime
import numpy as np

here = os.path.dirname(__file__)
data_path = os.path.dirname(__file__) + "/data/"
output_path = os.path.dirname(__file__) + "/output/"

print("Checking covidlive")

testo = ''
# testo = "_testo"

#%%

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

#%%

## Grab Covid Live Data

data = r.json()

df = pd.read_json(r.text)
# 'REPORT_DATE', 'LAST_UPDATED_DATE', 'CODE', 'NAME', 'CASE_CNT',
#        'TEST_CNT', 'DEATH_CNT', 'RECOV_CNT', 'MED_ICU_CNT', 'MED_VENT_CNT',
#        'MED_HOSP_CNT', 'SRC_OVERSEAS_CNT', 'SRC_dfSTATE_CNT',
#        'SRC_CONTACT_CNT', 'SRC_UNKNOWN_CNT', 'SRC_INVES_CNT', 'PREV_CASE_CNT',
#        'PREV_TEST_CNT', 'PREV_DEATH_CNT', 'PREV_RECOV_CNT', 'PREV_MED_ICU_CNT',
#        'PREV_MED_VENT_CNT', 'PREV_MED_HOSP_CNT', 'PREV_SRC_OVERSEAS_CNT',
#        'PREV_SRC_dfSTATE_CNT', 'PREV_SRC_CONTACT_CNT',
#        'PREV_SRC_UNKNOWN_CNT', 'PREV_SRC_INVES_CNT', 'PROB_CASE_CNT',
#        'PREV_PROB_CASE_CNT', 'ACTIVE_CNT', 'PREV_ACTIVE_CNT', 'NEW_CASE_CNT',
#        'PREV_NEW_CASE_CNT', 'VACC_DIST_CNT', 'PREV_VACC_DIST_CNT',
#        'VACC_DOSE_CNT', 'PREV_VACC_DOSE_CNT', 'VACC_PEOPLE_CNT',
#        'PREV_VACC_PEOPLE_CNT', 'VACC_AGED_CARE_CNT', 'PREV_VACC_AGED_CARE_CNT',
#        'VACC_GP_CNT', 'PREV_VACC_GP_CNT'

df = df.loc[df['NAME'] == "Australia"]
df = df.sort_values(by='REPORT_DATE', ascending=True)


if np.isnan(df['NEW_CASE_CNT'].values[-1]):
    df['New_cases'] = df['PREV_NEW_CASE_CNT']
else:
    df['New_cases'] = df['NEW_CASE_CNT']
# df['New_cases'].diff(0)
df['New_cases'].fillna(0, inplace=True)

df['Cases_last_14'] = df['New_cases'].rolling(window=14).sum()

# print(df[['REPORT_DATE','New_cases','Cases_last_14']])

#%%

medical = ['REPORT_DATE','Cases_last_14','ACTIVE_CNT','MED_HOSP_CNT']
df_med = df[medical]
# df_med['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'], format="%Y-%m-%d")

df_med = df_med.rename(columns={"REPORT_DATE": "Date", "ACTIVE_CNT":"Active cases",
 'MED_HOSP_CNT':"In hospital"})
# df_med = df_med.sort_values(['Date'])
# df_med = df_med.set_index('Date'


# df_med['Percentage hospitalised'] = (df_med['In hospital'] / df_med['Active cases']) * 100
df_med['Percentage hospitalised'] = (df_med['In hospital'] / df_med['Cases_last_14']) * 100



df = df_med[['Date', 'Percentage hospitalised']]

df = df.loc[df['Date'] > "2020-04-01"]

df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values(by='Date', ascending=True)

updated_date = df['Date'].max()
df['Date'] = df['Date'].dt.strftime("%Y-%m-%d")
# print(df)
updated_date = datetime.datetime.strftime(updated_date, "%d %B %Y")

print(df)
#%%


def makeLineChart(df):

    template = [
            {
                "title": "Covid hospitalisation rate in Australia",
                "subtitle": f"Showing the number of number of hospitalised Covid cases divided by the number of new cases over the previous two weeks, including overseas acquired cases. Last updated {updated_date}.",
                "footnote": "",
                "source": "CovidLive.com.au, Guardian analysis | Based on a chart by Covid19data.com.au",
                "dateFormat": "%Y-%m-%d",
                "yScaleType":"",
                "xAxisLabel": "Date",
                "yAxisLabel": "",
                "minY": "0",
                "maxY": "",
                # "periodDateFormat":"",
                "margin-left": "30",
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

    yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], options=[{"colorScheme":"guardian", "lineLabelling":"FALSE"}], chartName=f"oz-corona-live-page-hospitalised-percentage{testo}")

makeLineChart(df)

