#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
import ssl
from datetime import timedelta
from modules.yachtCharter import yachtCharter

state_json = "https://vaccinedata.covid19nearme.com.au/data/all.json"

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

#%%
	
df = pd.read_json(state_json)

#%%
cols = list(df.columns)

#%%

df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'], format="%Y-%m-%d")
df = df.rename(columns={"REPORT_DATE": "Date"})

#%%
pivoted = df.pivot(index='Date', columns='CODE')['VACC_DOSE_CNT']
states = ["NSW","VIC","QLD","SA","WA","TAS","ACT","NT"]
daily = pivoted[states]

for state in states:
	daily[state] = daily[state].sub(daily[state].shift())

daily = daily["2021-04-10":]
daily[daily < 0] = 0

#%%
	
lastUpdated = daily.index[-1]
newUpdated = lastUpdated + timedelta(days=1)
updatedText = newUpdated.strftime('%-d %B, %Y')

# sixty_days = lastUpdated - timedelta(days=60)
daily.index = daily.index.strftime('%Y-%m-%d')

daily_stack = daily.stack().reset_index().rename(columns={"level_1":"category", 0:"count"})
daily_stack = daily_stack.set_index('Date')	


#%%

def makeStateVaccinations(df):
	
	template = [
			{
				"title": "Daily vaccinations by state and territory",
				"subtitle": "Showing total daily vaccinations for each state and territory, including those in Commonwealth-run clinics. Last updated {date}".format(date=updatedText),
				"footnote": "",
				"source": " | Source: <a href='https://covidlive.com.au/' target='_blank'>Covidlive.com.au</a>",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "",
				"timeInterval":"day",
				"tooltip":"<strong>Date: </strong>{{#nicedate}}Date{{/nicedate}}<br/><strong>Count: </strong>{{count}}",
				"periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "5",
				"margin-bottom": "20",
				"margin-right": "25",
				"xAxisDateFormat": "%b %d"
			}
		]
	key = []
	periods = []
	labels = []
	options = [{"numCols":"", "chartType":"bar", "height":150}]
	chartId = [{"type":"smallmultiples"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template,options=options, data=chartData, chartId=chartId, chartName="state-vaccinations-sm-2021")

makeStateVaccinations(daily_stack)