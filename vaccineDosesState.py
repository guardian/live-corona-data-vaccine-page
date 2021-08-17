#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
import ssl
from datetime import timedelta
from modules.yachtCharter import yachtCharter

state_json = "https://interactive.guim.co.uk/2021/02/coronavirus-widget-data/state-vaccine-rollout.json"

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

#%%
	
df = pd.read_json(state_json)

#%%

population = {
	"NSW":8166.4* 1000,
	"VIC":6680.6* 1000,
	"QLD":5184.8* 1000,
	"SA":1770.6* 1000,
	"WA":2667.1* 1000,
	"TAS":541.1* 1000,
	"NT":246.5* 1000,
	"ACT":431.2* 1000,
	"AUS":25693.1 * 1000
	}


#%%

df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'], format="%Y-%m-%d")
df = df.rename(columns={"REPORT_DATE": "Date"})

#%%
pivoted = df.pivot(index='Date', columns='CODE')['VACC_DOSE_CNT']
states = ["NSW","VIC","QLD","SA","WA","TAS","ACT","NT","AUS"]
daily = pivoted[states]

for state in states:
	daily[state] = daily[state].sub(daily[state].shift())

daily = daily["2021-04-10":]
daily[daily < 0] = 0

#%%
	
lastUpdated = daily.index[-1]
# newUpdated = lastUpdated + timedelta(days=1)
updatedText = lastUpdated.strftime('%-d %B, %Y')

#%%

def getRate(col):
	print(col.name)
	return col / population[col.name] * 1000
daily.apply(getRate)
daily_rate = daily.apply(getRate)

#%%

daily_mean = daily_rate.rolling(7).mean()
thirty_days = lastUpdated - timedelta(days=30)
daily_mean = daily_mean[thirty_days:]
daily_mean = daily_mean.dropna()
daily_mean = daily_mean[:-2]
daily_mean.index = daily_mean.index.strftime('%Y-%m-%d')
aus_only = daily_mean['AUS']

#%%
daily_mean = daily_mean.drop(['AUS'], axis=1)

#%%
daily_stack = daily_mean.stack().reset_index().rename(columns={"level_1":"category", 0:"State or territory"})
daily_stack = daily_stack.set_index('Date')	
merge = pd.merge(daily_stack, aus_only, left_index=True, right_index=True)
merge = merge.rename(columns={"AUS": "National"})

#%%

def makeStateVaccinations(df):
	
	template = [
			{
				"title": "Trend in recent daily vaccinations by state and territory",
				"subtitle": "Showing the seven-day rolling average in Covid vaccination doses administered daily per 1,000 people for each state and territory, versus the national rate. Showing the last 30 days only. Last updated {date}".format(date=updatedText),
				"footnote": "",
				"source": " | Source: Guardian Australia analysis of <a href='https://covidlive.com.au/' target='_blank'>covidlive.com.au</a> data",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "",
				"timeInterval":"day",
				"tooltip":"<strong>Date: </strong>{{#nicedate}}Date{{/nicedate}}<br/><strong>Count: </strong>{{count}}",
				"periodDateFormat":"",
				"margin-left": "22",
				"margin-top": "5",
				"margin-bottom": "22",
				"margin-right": "22",
				"xAxisDateFormat": "%b %d"
			}
		]
	key = []
	periods = []
	labels = []
	options = [{"numCols":4, "chartType":"line", "height":150, "scaleBy":"group"}]
	chartId = [{"type":"smallmultiples"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template,options=options, data=chartData, chartId=chartId, chartName="state-vaccinations-sm-2021")

makeStateVaccinations(merge)

