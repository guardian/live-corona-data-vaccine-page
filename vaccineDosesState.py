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
daily_cum = pivoted[states]
daily_cum.to_csv('pivot_cumulative.csv')

# daily_cum["2021-02-24":"2021-08-16"] = daily_cum["2021-02-24":"2021-08-16"].apply(adjust)

#%%

daily = daily_cum.copy()

for state in states:
	daily[state] = daily[state].sub(daily[state].shift())

count = len(daily_cum["2021-02-24":"2021-08-15"].index) - 1

daily.to_csv('daily-vax.csv')

# Adjusts for the switchover from 2021-08-16 to the AIR derived data, by taking the new difference and adjusting previous values using an average of the difference

diff_adjustment = {"NSW":119652, "VIC":-30981, "QLD":11598, "SA": -5354, "WA":15146, "TAS": 860, "ACT":47614, "NT":5192,"AUS":163727}
state_adjustments = {}
daily_adj = daily.copy()

for state in states:
	gap = diff_adjustment[state]
	avg_7day = daily[state]["2021-08-09":"2021-08-15"].mean()
	adj_gap = gap - avg_7day
	adj_avg = adj_gap / count
	print("gap", gap, "avg_7day", avg_7day, "adj_gap", adj_gap, "adj_avg", adj_avg)
	state_adjustments[state] = {"adj_avg":adj_avg, "avg_7day":avg_7day}
	daily_adj[state]["2021-08-16"] = avg_7day

#%%
def adjust(col):
	return col + state_adjustments[col.name]["adj_avg"]

daily_adj["2021-02-24":"2021-08-15"] = daily_adj["2021-02-24":"2021-08-15"].apply(adjust)

#%%

daily_short = daily_adj["2021-04-10":]
# daily_short = daily["2021-04-10":]
# daily[daily < 0] = 0

#%%

lastUpdated = daily_short.index[-1]
# newUpdated = lastUpdated + timedelta(days=1)
updatedText = lastUpdated.strftime('%-d %B, %Y')

#%%

def getRate(col):
	print(col.name)
	return col / population[col.name] * 100

daily_short.apply(getRate)
daily_rate = daily_short.apply(getRate)

#%%

daily_mean = daily_rate.rolling(7).mean()
thirty_days = lastUpdated - timedelta(days=30)
daily_mean = daily_mean[thirty_days:]
daily_mean = daily_mean.dropna()
# daily_mean = daily_mean[:-2]
daily_mean.index = daily_mean.index.strftime('%Y-%m-%d')
aus_only = daily_mean['AUS']

#%%
daily_mean = daily_mean.drop(['AUS'], axis=1)

#%%
daily_stack = daily_mean.stack().reset_index().rename(columns={"level_1":"category", 0:"State or territory"})
daily_stack = daily_stack.set_index('Date')
merge = pd.merge(daily_stack, aus_only, left_index=True, right_index=True)
merge = merge.rename(columns={"AUS": "National"})
merge = merge.round(3)

print(merge)

#%%

def makeStateVaccinations(df):

	template = [
			{
				"title": "Trend in recent daily vaccinations by state and territory",
				"subtitle": "Showing the seven-day rolling average in Covid vaccination doses administered daily per 100 people in each state and territory, versus the national rate. Showing the last 30 days only. Figures have been adjusted to average out the difference of the data changing sources on 16 August, see notes. Last updated {date}".format(date=updatedText),
				"footnote": "",
				"source": " | Source: Guardian Australia analysis of <a href='https://covidlive.com.au/' target='_blank'>covidlive.com.au</a> data | Data shows vaccinations by state of administration, not by state of residence | On 16 August the Department of Health switched to using figures from the Australian Immunisation Register for state and territory vaccination totals. The day-on-day difference between the old and new data has been averaged out on data up to 16 August, and the 16 August total replaced with a 7-day average. After 16 August figures are as normal.",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "",
				"timeInterval":"day",
				"tooltip":"<strong>Date: </strong>{{#nicedate}}Date{{/nicedate}}<br/><strong>Count: </strong>{{State or territory}}",
				"periodDateFormat":"",
				"margin-left": "25",
				"margin-top": "25",
				"margin-bottom": "22",
				"margin-right": "22",
				"xAxisDateFormat": "%b %d"
			}
		]
	key = []
	periods = [{"label":"Data change", "start":"2021-08-16","end":"","textAnchor":"start"}]
	labels = []
	options = [{"numCols":4, "chartType":"line", "height":150, "scaleBy":"group"}]
	chartId = [{"type":"smallmultiples"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template,options=options, data=chartData, periods=periods, chartId=chartId, chartName="state-vaccinations-sm-2021")

makeStateVaccinations(merge)
