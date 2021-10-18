#%%
import requests
import pandas as pd 
import datetime
chart_key = f"oz-covid-nsw-june2021-outbreak"
import os 
from modules.yachtCharter import yachtCharter

#%%

# sht1 = gc.open_by_key('0BmgG6nO_6dprdS1MN3d3MkdPa142WFRrdnRRUWl1UFE')
fillo = 'https://docs.google.com/spreadsheets/d/1t3l50GPkIib2lzPRfXlVW4P4Z-xYak3VwjhZH3T6Rw4/pub?gid=1454102594&single=True&output=csv'

statto = "NSW"

#%%

## GRAB Current data

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

new = r.json()
new = pd.read_json(r.text)


#%%


def together(state, new_data, past):

    ### Grab old data 

    old_data = pd.read_csv(past, parse_dates=['Date'])
    old_data = old_data.loc[old_data['Date'] <= "2021-10-15"]

    ## Subset data
    inter = new_data.loc[new_data['CODE'] == state].copy()

    inter['REPORT_DATE'] = pd.to_datetime(inter['REPORT_DATE'])
    inter = inter.sort_values(by=['REPORT_DATE'], ascending=True)
    inter['REPORT_DATE'] = inter['REPORT_DATE'].dt.strftime("%Y-%m-%d")


    ## Calculate new local cases
    inter['New_local'] = inter['CASE_CNT'] - inter['SRC_OVERSEAS_CNT']
    inter['New_local'] = inter['New_local'].diff(1)

    inter = inter[['REPORT_DATE','New_local']]

    inter.columns = ['Date', 'Locally-acquired cases']

    old_data['Date'] = old_data['Date'].dt.strftime("%Y-%m-%d")
    latest_date = old_data['Date'].max()


    ## Cutoff new data for existing values in the dataset
    inter = inter.loc[inter['Date'] > latest_date]

    ## Combine

    combo = pd.concat([old_data, inter])

    # print(combo)

    return combo


old = together(statto, new, fillo)  

#%%

## Get the trendline

roll = old.copy()
roll['Trend'] = roll['Locally-acquired cases'].rolling(window=7).mean()

roll = roll[['Date', 'Trend']]

roll.fillna('', inplace=True)
roll = roll.to_dict(orient='records')
# p = roll

# print(p)
# print(p.columns.tolist())

last_updated = old['Date'].max()
last_updated = datetime.datetime.strptime(last_updated, "%Y-%m-%d")
display_date = datetime.datetime.strftime(last_updated, "%-d %B %Y")


# %%


def makeTestingLine(df):

    template = [
            {
                "title": "NSW Covid cases announced daily",
                "subtitle": f"""Showing the number of locally-acquired cases announced daily and the trend as a 7-day rolling average. Last updated {display_date}.""",
                "footnote": "",
                "source": "Sources: NSW Health, Guardian Australia, CovidLive.com.au",
                "dateFormat": "%Y-%m-%d",
                "xAxisDateFormat":"%b %d",
                "minY": "0",
                "maxY": "",
                "x_axis_cross_y":"",
                "periodDateFormat":"",
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