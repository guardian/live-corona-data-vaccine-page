#%%
import requests
import pandas as pd 
import datetime
chart_key = f"oz-covid-aus-outbreak-chart-bar"
import os 
from modules.yachtCharter import yachtCharter
import numpy as np 

#%%

# fillo = 'https://docs.google.com/spreadsheets/d/1BaHphN6yIfVk10EHlOFPlYSq8qLI8IHSiEJLZ2WVuAg/pub?gid=1454102594&single=True&output=csv'
statto = "AUS"
init = '2021-07-12'

#%%

## GRAB Current data

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

new = r.json()
new = pd.read_json(r.text)

# new.loc[new['REPORT_DATE'] == "2021-10-21", 'CASE_CNT'] = np.nan 
# new.loc[new['REPORT_DATE'] == "2021-10-21", 'SRC_OVERSEAS_CNT'] = np.nan 

#%%


def together(state, new_data,  start):

    ## Subset data
    inter = new_data.loc[new_data['CODE'] == state].copy()

    inter['REPORT_DATE'] = pd.to_datetime(inter['REPORT_DATE'])
    inter = inter.sort_values(by=['REPORT_DATE'], ascending=True)

    # Reduce days by one day to get the actual date
    inter['REPORT_DATE'] = inter['REPORT_DATE'] - datetime.timedelta(days=1)


    inter['REPORT_DATE'] = inter['REPORT_DATE'].dt.strftime("%Y-%m-%d")

    # ## Calculate new local cases
    # inter['New_local'] = inter['CASE_CNT'] - inter['SRC_OVERSEAS_CNT']
    # inter['New_local'] = inter['New_local'].diff(1)
    inter['New_cases'] = inter['CASE_CNT'].diff(1)

    inter = inter[['REPORT_DATE','New_cases']]

    inter.columns = ['Date', 'New cases']

    return inter


old = together(statto, new,  init)  

old = old.dropna()

print(old.tail())

#%%

## Get the trendline

roll = old.copy()
roll['Trend'] = roll['New cases'].rolling(window=7).mean()

roll = roll[['Date', 'Trend']]

roll.fillna('', inplace=True)
roll = roll.to_dict(orient='records')
# p = roll

# print(p)
# print(p.columns.tolist())

last_updated = old['Date'].max()
last_updated = datetime.datetime.strptime(last_updated, "%Y-%m-%d")
last_updated = last_updated + datetime.timedelta(days=1)
display_date = datetime.datetime.strftime(last_updated, "%-d %B %Y")


# %%


def makeTestingLine(df):

    template = [
            {
                "title": "Australian Covid cases announced daily",
                "subtitle": f"""Showing the number of cases announced daily and the trend as a 7-day rolling average. Last updated {display_date}.""",
                "footnote": "",
                "source": "Sources: Covid19data, Guardian Australia, CovidLive.com.au",
                "dateFormat": "%Y-%m-%d",
                "xAxisDateFormat":"%b/%y",
                "minY": "0",
                "maxY": "",
                "x_axis_cross_y":"",
                "periodDateFormat":"",
                # "tooltip":"New cases: {{New cases}}",
                "margin-left": "50",
                "margin-top": "30",
                "margin-bottom": "20",
                "margin-right": "10"
            }
        ]
    key = [{"key":"Locally-acquired cases", "colour":"#fc9272"}]
    periods = []
    labels = []
    df.fillna("", inplace=True)
    chartData = df.to_dict('records')


    yachtCharter(template=template, labels=labels, key=key, trendline=roll, data=chartData, chartId=[{"type":"stackedbar"}],
    options=[{"colorScheme":"guardian"}], chartName=f"{chart_key}")

makeTestingLine(old)