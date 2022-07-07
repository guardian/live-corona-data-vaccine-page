#%%

import os
import requests
import pandas as pd
from yachtcharter import yachtCharter
import datetime
import numpy as np

og = pd.read_json('https://covidlive.com.au/covid-live.json')

states = ["NSW","VIC","QLD","SA","WA","TAS","ACT","NT","AUS"]

testo = ''
testo = '-testo'

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

# # optionally manually add today's hosp numbers

# useLatest = True
# merge = og.copy()

# if useLatest:
# 	new_data = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vSNljV81sJgmhQJnKHT4jvsZbqkdYHxaE0k7g5xaurBn0hHMujHEA47dDqELgwHRd4UGfpmRxV4kBkT/pub?gid=203642518&single=true&output=csv")
# 	new_data = new_data.dropna()
# 	merge = merge.append(new_data)


# test = merge.loc[merge['CODE'] == "NSW"]

#%%

# state = "NSW"

# print(state)	

# df = merge.copy()	
# df = df.loc[df['CODE'] == state]
#%%

zdf = og.copy()
zdf = zdf.loc[zdf['CODE'] == "NSW"]

zdf = zdf.loc[zdf['REPORT_DATE'] >= start].copy()

zdf = zdf[['REPORT_DATE','MED_HOSP_CNT', "MED_ICU_CNT"]]
zdf['MED_HOSP_CNT'] = pd.to_numeric(zdf['MED_HOSP_CNT'])
zdf["MED_ICU_CNT"] = pd.to_numeric(zdf["MED_ICU_CNT"])


zdf = zdf.sort_values(by=['REPORT_DATE'], ascending=True)
zdf.drop_duplicates(subset='REPORT_DATE', keep='last', inplace=True)

# zdf['HOSP_%_CHANGE'] = ((zdf["MED_HOSP_CNT"] - np.roll(zdf["MED_HOSP_CNT"], shift=-7))/np.roll(zdf["MED_HOSP_CNT"], shift=-7))*100

# zdf["MED_HOSP_CNT"] = zdf["MED_HOSP_CNT"].rolling(window=7).mean()
# zdf["MED_ICU_CNT"] = zdf["MED_ICU_CNT"].rolling(window=7).mean()

zdf['HOSP_7_BEFORE'] = zdf["MED_HOSP_CNT"].shift(7)
zdf['HOSP_7_BEFORE_CHANGE'] = zdf["MED_HOSP_CNT"] - zdf['HOSP_7_BEFORE']
zdf['HOSP_%_CHANGE_7_BEFORE'] = round((zdf['HOSP_7_BEFORE_CHANGE']/zdf['HOSP_7_BEFORE'])*100, 2)


zdf['ICU_7_BEFORE'] = zdf["MED_ICU_CNT"].shift(7)
zdf['ICU_7_BEFORE_CHANGE'] = zdf["MED_ICU_CNT"] - zdf['ICU_7_BEFORE']
zdf['ICU_%_CHANGE_7_BEFORE'] = round((zdf['ICU_7_BEFORE_CHANGE']/zdf['ICU_7_BEFORE'])*100, 2)

# zdf = zdf[['REPORT_DATE', 'MED_HOSP_CNT', 'MED_ICU_CNT', 'HOSP_%_CHANGE_7_BEFORE', 'ICU_%_CHANGE_7_BEFORE']]
zdf = zdf[['REPORT_DATE', 'HOSP_%_CHANGE_7_BEFORE', 'ICU_%_CHANGE_7_BEFORE']]

zdf = zdf.loc[zdf['REPORT_DATE'] > "2021-12-01"]

zdf.columns = ["Date", "In hospital", 'In ICU']


# df['target'] = df.value / np.roll(df.value, shift=-1)

p = zdf

print(p.tail(20))
print(p.columns)

# import datetime
# today = datetime.datetime.today()
# today = datetime.datetime.strftime(today, "%Y-%m-%d")
# # 	startDate = '2021-08-01'

# thresholds = [
# 	{"y1":beds[state] * 0.15,"y2":beds[state] * 0.15,"x1":start, "x2":today, "text":"Amber (> 15% of hospital beds)"},
# # 		{"y1":beds[state] * 0.30,"y2":beds[state] * 0.30,"x1":startDate, "x2":today, "text":"Red (> 30% of hospital beds) "},
# 	]

# # %%

# maxY = max(beds[state] * 0.2, df['Hospitalised cases'].max())
# print(df['Hospitalised cases'].max())
# df['Date'] = pd.to_datetime(df['Date'])
# df = df.sort_values(by='Date', ascending=True)
# #%%
# updated_date = df['Date'].max()
# df['Date'] = df['Date'].dt.strftime("%Y-%m-%d")
# # print(df)
# updated_date = datetime.datetime.strftime(updated_date, "%-d %B %Y")

# # combo = pd.merge(df, other, left_on='Date', right_on='Date', how="left")
# if state == "AUS":
# 	state_text = "Australia"
# else:
# 	state_text = state	
# # print(combo)

# if state == "AUS" or state == "NT" or state == "QLD":
# 	hosp_text = ". Queensland and the NT previously had a policy of hospitalising all Covid cases. These policies were lifted in December 2021"
# else:
# 	hosp_text = ""

def makeLineChart(df):

	template = [
			{
				"title": f"Change in hospital and ICU cases in NSW",
				"subtitle": f"Showing the percentage change from 7 days prior",
				"footnote": "",
				"source": f"CovidLive.com.au, based on a chart by Dr Edward Jegasothy",
				"dateFormat": "%Y-%m-%d",
				"yScaleType":"",
				"xAxisLabel": "Date",
				"yAxisLabel": "",
				"minY": "-30",
				"maxY": "",
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
	# lines = thresholds
	lines = []
	chartId = [{"type":"linechart"}]
	df.fillna('', inplace=True)
	# df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], options=[{"colorScheme":"guardian", "lineLabelling":"TRUE"}], chartName=f"nsw-hospo-change{testo}", lines=lines)

makeLineChart(zdf)

# %%
