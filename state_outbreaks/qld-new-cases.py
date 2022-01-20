#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pandas as pd 
import datetime
import os 
from modules.yachtCharter import yachtCharter
import numpy as np 


#%% 

# setup variables

state = "QLD"
start = '2021-11-01'
end = '2022-01-08'

# Get CovidLive data

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

clive = r.json()
#%%

clive = pd.read_json(r.text)
clive = clive.loc[clive['CODE'] == state].copy()
cols = list(clive.columns)

#%%
clive['REPORT_DATE'] = pd.to_datetime(clive['REPORT_DATE'])
clive = clive.sort_values(by=['REPORT_DATE'], ascending=True)
clive['REPORT_DATE'] = clive['REPORT_DATE'] - datetime.timedelta(days=1)
clive['REPORT_DATE'] = clive['REPORT_DATE'].dt.strftime("%Y-%m-%d")

## Calculate new cases by differencing totals
# clive['PCR'] = clive['CASE_CNT']
# clive['PCR'] = clive['PCR'].diff(1)

# Calculate new tests 

clive['PCR_tests'] = clive['TEST_CNT']
clive['PCR_tests'] = clive['PCR_tests'].diff(1)

clive['PCR'] = clive['NEW_CASE_CNT']
clive['PCR'].fillna(0, inplace=True)
clive = clive[['REPORT_DATE','PCR', 'PCR_tests']]
clive.columns = ['Date', 'PCR', 'PCR_tests']

clive["Test positivity"] = clive['PCR'] / clive['PCR_tests'] * 100
clive = clive.loc[clive['Date'] < end]


#%%

# Add new manual PCR and RAT data

new_data = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vSNljV81sJgmhQJnKHT4jvsZbqkdYHxaE0k7g5xaurBn0hHMujHEA47dDqELgwHRd4UGfpmRxV4kBkT/pub?gid=0&single=true&output=csv")

#%%
new_data = new_data.loc[new_data['State'] == state].copy()
new_data = new_data[['Date', 'PCR', 'RAT']]

# Merge the data

#%%

merged = clive.append(new_data)
merged.fillna(0, inplace=True)
merged['Total'] = merged['PCR'] + merged['RAT']

#%%
# Make trend line

roll = merged.copy()
roll['Trend'] = roll['Total'].rolling(window=7).mean()
roll = roll[['Date', 'Trend']]
roll = roll.loc[roll['Date'] >= start]
roll.fillna('', inplace=True)
roll = roll.to_dict(orient='records')

merged = merged.loc[merged['Date'] >= start]

#%%

last_updated = merged['Date'].max()
last_updated = datetime.datetime.strptime(last_updated, "%Y-%m-%d")
last_updated = last_updated + datetime.timedelta(days=1)
display_date = datetime.datetime.strftime(last_updated, "%-d %B %Y")

final = merged[['Date', 'PCR', 'RAT']]

# final.to_csv("nsw-final.csv")

#%%

def makeTestingLine(df):

    template = [
            {
                "title": "Covid cases announced daily in Queensland",
                "subtitle": f"""Showing the number of cases announced daily by testing type and the trend of total cases as a 7-day rolling average. Testing criteria (1) changed significantly on 5 January 2022. Cases after this point should be considered an underestimate and may contain duplicates from RAT reporting Last updated {display_date}.""",
                "footnote": "",
                "source": "| Sources: NSW Health, covid19data, Guardian Australia, CovidLive.com.au",
                "dateFormat": "%Y-%m-%d",
                "xAxisDateFormat":"%b %d",
                "minY": "0",
                "maxY": "",
				"includeCols":"PCR,RAT",
                "x_axis_cross_y":"",
                "periodDateFormat":"",
                "margin-left": "50",
                "margin-top": "30",
                "margin-bottom": "20",
                "margin-right": "15",
				"tooltip":"<strong>{{#nicerdate}}Date{{/nicerdate}}</strong><br><strong>{{group}}</strong>: {{groupValue}}"
            }
        ]
    key = [{"key":"PCR","values":"","colour":"#fc9272", "colours":"", "scale":"linear", "source":"Test positivity"},
		{"key":"RAT","colour":"#74add1"}]
    periods = [{"label":"1", "start":"2022-01-05", "end":"","labelAlign":"middle"}]
    
    df.fillna("", inplace=True)
    chartData = df.to_dict('records')


    yachtCharter(template=template, key=key, periods=periods, trendline=roll, data=chartData, 		chartId=[{"type":"stackedbar"}],
    options=[{"colorScheme":"guardian"}], chartName=f"{state}-new-cases-chart-2022")

makeTestingLine(final)
