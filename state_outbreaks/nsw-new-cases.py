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

state = "NSW"
start = '2021-11-01'
end = '2022-01-12'

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

final.to_csv("nsw-final.csv")

#%%

def makeTestingLine(df):

    template = [
            {
                "title": "NSW Covid cases announced daily",
                "subtitle": f"""Showing the number of cases announced daily by testing type and the trend of total cases as a 7-day rolling average. The annotation (1) shows an approximate date for when significant testing capacity issues began. Cases after this point should be considered an underestimate and may contain duplicates from RAT reporting. Testing criteria (2) changed significantly on 5 January 2022. Last updated {display_date}.""",
                "footnote": "",
                "source": "| * 12 to 15 January case numbers include a backlog of RAT tests, and are not all from the past 24 hours. Sources: NSW Health, covid19data, Guardian Australia, CovidLive.com.au",
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
    periods = [{"label":"1", "start":"2021-12-20", "end":"","labelAlign":"middle"},
			   {"label":"2", "start":"2022-01-05", "end":"","labelAlign":"middle"}]
    labels = [{"x1":"2022-01-12", "y1":"92264", "y2":"92264", "text":"*", "align":"middle"},
			  {"x1":"2022-01-13", "y1":"63018", "y2":"63018", "text":"*", "align":"middle"},
			  {"x1":"2022-01-14", "y1":"48768", "y2":"48768", "text":"*", "align":"middle"},
			  {"x1":"2022-01-15", "y1":"34660", "y2":"34660", "text":"*", "align":"middle"}]
    df.fillna("", inplace=True)
    chartData = df.to_dict('records')


    yachtCharter(template=template, labels=labels, key=key, periods=periods, trendline=roll, data=chartData, 		chartId=[{"type":"stackedbar"}],
    options=[{"colorScheme":"guardian"}], chartName=f"{state}-new-cases-chart-2022")

makeTestingLine(final)
