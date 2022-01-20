#%%

import os
import requests
import pandas as pd
from yachtcharter import yachtCharter
import datetime

og = pd.read_json('https://covidlive.com.au/covid-live.json')

states = ["NSW","VIC","QLD","SA","WA","TAS","ACT","NT","AUS"]

beds = {
  "AUS": 62575,
  "NSW": 20722,
  "VIC": 14949,
  "QLD": 12889,
  "WA": 5883,
  "SA": 4532,
  "TAS": 1472,
  "ACT": 1151,
  "NT": 977
}
# "2021-08-01"
start = "2021-08-01"
# start = "2021-12-01"

#%%

# optionally manually add today's hosp numbers

useLatest = True
merge = og.copy()

if useLatest:
	new_data = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vSNljV81sJgmhQJnKHT4jvsZbqkdYHxaE0k7g5xaurBn0hHMujHEA47dDqELgwHRd4UGfpmRxV4kBkT/pub?gid=203642518&single=true&output=csv")
	new_data = new_data.dropna()
	merge = merge.append(new_data)


test = merge.loc[merge['CODE'] == "NSW"]

#%%

state = "NSW"

print(state)	

df = merge.copy()	
df = df.loc[df['CODE'] == state]
#%%
df = df.loc[df['REPORT_DATE'] >= start].copy()

df = df[['REPORT_DATE','MED_HOSP_CNT']]
df['MED_HOSP_CNT'] = pd.to_numeric(df['MED_HOSP_CNT'])

df.columns = ['Date', 'Hospitalised cases']
# print(df)

import datetime
today = datetime.datetime.today()
today = datetime.datetime.strftime(today, "%Y-%m-%d")
# 	startDate = '2021-08-01'


# %%

maxY = max(beds[state] * 0.2, df['Hospitalised cases'].max())
print(df['Hospitalised cases'].max())
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values(by='Date', ascending=True)
#%%
updated_date = df['Date'].max()
df['Date'] = df['Date'].dt.strftime("%Y-%m-%d")
# print(df)
updated_date = datetime.datetime.strftime(updated_date, "%-d %B %Y")

# combo = pd.merge(df, other, left_on='Date', right_on='Date', how="left")
if state == "AUS":
	state_text = "Australia"
else:
	state_text = state	
# print(combo)

if state == "AUS" or state == "NT" or state == "QLD":
	hosp_text = ". Queensland and the NT previously had a policy of hospitalising all Covid cases. These policies were lifted in December 2021"
else:
	hosp_text = ""

def makeLineChart(df):

	template = [
			{
				"title": f"Covid cases hospitalised in {state_text} v hospital capacity impact thresholds",
				"subtitle": f"Showing the number of people hospitalised with Covid over time, along with the federal government's clinical capacity thresholds that indicate when action is required. The 'amber' or 15% hospital capacity threshold indicates 'targeted adjustments' are required or in progress, while the 'red' threshold of 30% – currently not shown – indicates a 'harder or wider' response is required. Last updated {updated_date}.",
				"footnote": "",
				"source": f"CovidLive.com.au, Department of Health, AIHW, <a href='hhttps://www.health.gov.au/sites/default/files/documents/2022/01/coronavirus-covid-19-common-operating-picture-3-january-2022.pdf'>clinical capacity thresholds</a>, Guardian analysis{hosp_text}",
				"dateFormat": "%Y-%m-%d",
				"yScaleType":"",
				"xAxisLabel": "Date",
				"yAxisLabel": "",
				"minY": "",
				"maxY": f"{maxY}",
				# "periodDateFormat":"",
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
	lines = thresholds
	chartId = [{"type":"linechart"}]
	df.fillna('', inplace=True)
	# df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], options=[{"colorScheme":"guardian", "lineLabelling":"FALSE"}], chartName=f"{state}-hospitalisation-thresholds", lines=lines)

makeLineChart(df)
