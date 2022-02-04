#%%

import os
import requests
import pandas as pd
from modules.yachtCharter import yachtCharter
import datetime


og = pd.read_json('https://covidlive.com.au/covid-live.json')
# og = pd.read_json('https://interactive.guim.co.uk/2022/01/oz-covid-health-data/cases.json')

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

# "2021-08-01"
start = "2021-08-01"
# start = "2021-12-01"

test = "-test"
# test= ""

df = pd.DataFrame

test_df = og.loc[og['CODE'] == "SA"]

#%%

def makeChart(state):
	
	# state = "VIC"
	print(state)	
	global df
	df = og.copy()	
	df = df.loc[df['CODE'] == state]
	
	#%%
# 	df = df.loc[df['REPORT_DATE'] >= start].copy()
	
	df = df[['REPORT_DATE','NEW_CASE_CNT']]
	df['NEW_CASE_CNT'] = pd.to_numeric(df['NEW_CASE_CNT'])
	
	df.columns = ['Date', 'Confirmed cases']
	df = df.dropna()
	# print(df)
	
	import datetime
	today = datetime.datetime.today()
	today = datetime.datetime.strftime(today, "%Y-%m-%d")
# 	startDate = '2021-08-01'

	df['Date'] = pd.to_datetime(df['Date'])
	df = df.sort_values(by='Date', ascending=True)
	#%%
	updated_date = df['Date'].max()
	df['Date'] = df['Date'].dt.strftime("%Y-%m-%d")
	# print(df)
	updated_date = datetime.datetime.strftime(updated_date, "%-d %B %Y")
	
	
	roll = df.copy()
	roll['Trend'] = roll['Confirmed cases'].rolling(window=7).mean()
	roll = roll[['Date', 'Trend']]
	roll = roll.loc[roll['Date'] >= start]
	roll.fillna('', inplace=True)
	roll = roll.to_dict(orient='records')
	
	df = df.loc[df['Date'] >= start].copy()
	
	
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
	                "title": f"{state_text} Covid cases announced daily",
	                "subtitle": f"""Showing the number of cases announced daily  and the trend of total cases as a 7-day rolling average. Testing criteria (2) changed significantly on 5 January 2022, and cases after this point should be considered an underestimate. Last updated {updated_date}.""",
	                "footnote": "",
	                "source": "| Sources: NSW Health, covidlive.com.au, Guardian Australia, CovidLive.com.au",
	                "dateFormat": "%Y-%m-%d",
	                "xAxisDateFormat":"%b %d",
	                "minY": "0",
	                "maxY": "",
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
	    labels = []
	    df.fillna("", inplace=True)
	    chartData = df.to_dict('records')


	    yachtCharter(template=template, labels=labels, key=key, periods=periods, trendline=roll, data=chartData, 		chartId=[{"type":"stackedbar"}],
	    options=[{"colorScheme":"guardian"}], chartName=f"{state}-basic-cases-chart-2022{test}")
	
	makeLineChart(df)
#%%

for state in states:
 	makeChart(state)	
# makeChart("SA")