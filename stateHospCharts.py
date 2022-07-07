#%%

import os
import requests
import pandas as pd
from yachtcharter import yachtCharter
import datetime

# og = pd.read_json('https://covidlive.com.au/covid-live.json')
og = pd.read_json('https://interactive.guim.co.uk/2022/01/oz-covid-health-data/cases.json')

# 'REPORT_DATE', 'LAST_UPDATED_DATE', 'CODE', 'NAME', 'CASE_CNT',
#        'TEST_CNT', 'DEATH_CNT', 'RECOV_CNT', 'MED_ICU_CNT', 'MED_VENT_CNT',
#        'MED_HOSP_CNT', 'SRC_OVERSEAS_CNT', 'SRC_INTERSTATE_CNT',
#        'SRC_CONTACT_CNT', 'SRC_UNKNOWN_CNT', 'SRC_INVES_CNT', 'PREV_CASE_CNT',
#        'PREV_TEST_CNT', 'PREV_DEATH_CNT', 'PREV_RECOV_CNT', 'PREV_MED_ICU_CNT',
#        'PREV_MED_VENT_CNT', 'PREV_MED_HOSP_CNT', 'PREV_SRC_OVERSEAS_CNT',
#        'PREV_SRC_INTERSTATE_CNT', 'PREV_SRC_CONTACT_CNT',
#        'PREV_SRC_UNKNOWN_CNT', 'PREV_SRC_INVES_CNT', 'PROB_CASE_CNT',
#        'PREV_PROB_CASE_CNT', 'ACTIVE_CNT', 'PREV_ACTIVE_CNT', 'NEW_CASE_CNT',
#        'PREV_NEW_CASE_CNT', 'VACC_DIST_CNT', 'PREV_VACC_DIST_CNT',
#        'VACC_DOSE_CNT', 'PREV_VACC_DOSE_CNT', 'VACC_PEOPLE_CNT',
#        'PREV_VACC_PEOPLE_CNT', 'VACC_AGED_CARE_CNT', 'PREV_VACC_AGED_CARE_CNT',
#        'VACC_GP_CNT', 'PREV_VACC_GP_CNT'

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

# test = "-test"
test= ""

#%%

# optionally manually add today's hosp numbers

useLatest = True
merge = og.copy()

if useLatest:
	print("yeah")
	new_data = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vSNljV81sJgmhQJnKHT4jvsZbqkdYHxaE0k7g5xaurBn0hHMujHEA47dDqELgwHRd4UGfpmRxV4kBkT/pub?gid=203642518&single=true&output=csv")
	new_data = new_data.dropna(subset=['MED_HOSP_CNT'])
	merge = merge.append(new_data)


test_df = merge.loc[merge['CODE'] == "NSW"]

test_df = test_df[['REPORT_DATE', 'MED_HOSP_CNT']]

#%%




def makeChart(state):
	
	# state = "VIC"
	print(state)	
	
	df = merge.copy()	
	df = df.loc[df['CODE'] == state]
	#%%
	df = df.loc[df['REPORT_DATE'] >= start].copy()
	
	df = df[['REPORT_DATE','MED_HOSP_CNT']]
	df['MED_HOSP_CNT'] = pd.to_numeric(df['MED_HOSP_CNT'])
	
	df.columns = ['Date', 'Hospitalised cases']
	# print(df)
	if state == "ACT":
		df.loc[df['Date'] =="2022-04-17", 'Hospitalised cases'] = 60
		df.loc[df['Date'] =="2022-04-15", 'Hospitalised cases'] = 56
		# print(df)
	
	import datetime
	today = datetime.datetime.today()
	today = datetime.datetime.strftime(today, "%Y-%m-%d")
# 	startDate = '2021-08-01'
	
# 	thresholds = [
# 		{"y1":beds[state] * 0.15,"y2":beds[state] * 0.15,"x1":start, "x2":today, "text":"Amber (> 15% of hospital beds)"},
# # 		{"y1":beds[state] * 0.30,"y2":beds[state] * 0.30,"x1":startDate, "x2":today, "text":"Red (> 30% of hospital beds) "},
# 		]
	
	# %%
	
	# maxY = max(beds[state] * 0.2, df['Hospitalised cases'].max())

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
					# "title": f"Covid cases hospitalised in {state_text} v hospital capacity impact thresholds",	
					"title": f"Covid cases hospitalised in {state_text}",
					"subtitle": f"Showing the number of people hospitalised with Covid over time. Last updated {updated_date}.",
					"footnote": "",
					"source": f"CovidLive.com.au, Department of Health, AIHW, <a href='hhttps://www.health.gov.au/sites/default/files/documents/2022/01/coronavirus-covid-19-common-operating-picture-3-january-2022.pdf'>clinical capacity thresholds</a>, Guardian analysis{hosp_text}",
					"dateFormat": "%Y-%m-%d",
					"yScaleType":"",
					"xAxisLabel": "Date",
					"yAxisLabel": "",
					"minY": "",
					# "maxY": f"{maxY}",
					"maxY": "",
					"tooltip":"<strong>{{#formatDate}}{{Date}}{{/formatDate}}</strong><br/> Hospitalised: {{Hospitalised cases}}",
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
		lines = []
		chartId = [{"type":"linechart"}]
		df.fillna('', inplace=True)
		# df = df.reset_index()
		chartData = df.to_dict('records')
	
		yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], options=[{"colorScheme":"guardian", "lineLabelling":"FALSE"}], chartName=f"{state}-hospitalisation-thresholds{test}", lines=lines)
	
	makeLineChart(df)
#%%
for state in states:
 	makeChart(state)	
# makeChart("NT")