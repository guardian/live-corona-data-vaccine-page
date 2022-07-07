#%%
import simplejson as json
import boto3
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from yachtcharter import yachtCharter
# from modules.syncData import syncData

here = os.path.dirname(__file__)
data_path = os.path.dirname(__file__) + "/data/"
output_path = os.path.dirname(__file__) + "/output/"

print("Checking covidlive")
pd.options.mode.chained_assignment = None
#%%


df = pd.read_json('covid-live.json')


nsw = df.loc[df['NAME'] == "NSW"]
cols = nsw.columns

#%%

# medical = ['REPORT_DATE','ACTIVE_CNT','MED_HOSP_CNT','MED_ICU_CNT','MED_VENT_CNT', 'DEATH_CNT']
# medical = ['REPORT_DATE','MED_HOSP_CNT','MED_ICU_CNT','MED_VENT_CNT', 'DEATH_CNT']
medical = ['REPORT_DATE','CASE_CNT','MED_HOSP_CNT']


#%%
nsw_med = nsw[medical]
nsw_med['New cases'] = nsw_med['CASE_CNT'].diff(periods=-1)

nsw_med = nsw_med[['REPORT_DATE', 'New cases', 'MED_HOSP_CNT']]
nsw_med['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'], format="%Y-%m-%d")
nsw_med = nsw_med.sort_values(['REPORT_DATE'], ascending=True)


#%%
nsw_med['New cases, 7 day avg'] = nsw_med['New cases'].rolling(7).mean()
# nsw_med = nsw_med.rename(columns={"REPORT_DATE": "Date",'ACTIVE_CNT':"Active cases","MED_ICU_CNT":"In ICU",  'MED_VENT_CNT':"On ventilators", 'MED_HOSP_CNT':"In hospital", "DEATH_CNT":"Deaths"})
nsw_med = nsw_med.rename(columns={"REPORT_DATE": "Date",'MED_HOSP_CNT':"In hospital", 'NEW_CASE_CNT':"New cases"})


nsw_med = nsw_med.sort_values(['Date'])
nsw_med = nsw_med.set_index('Date')

#%%

# nsw_med.loc[:"2021-07-09", "Deaths"] = 0
# nsw_med.loc["2021-07-09":, "Deaths"] = nsw_med.loc["2021-07-09":, "Deaths"].sub(nsw_med.loc["2021-07-09":, "Deaths"].shift())
# nsw_med.loc["2021-07-09":"2021-07-10", "Deaths"] = 0
# nsw_med['Deaths'] = nsw_med['Deaths'].cumsum()

#%%
lastUpdated = nsw_med.index[-1]
updatedText = lastUpdated.strftime('%-d %B, %Y')
sixty_days = lastUpdated - timedelta(days=60)
nsw_med_60 = nsw_med["2021-06-15":]
# nsw_med_60 = nsw_med
nsw_med_60.index = nsw_med_60.index.strftime('%Y-%m-%d')
nsw_med_60 = nsw_med_60.dropna()

# nsw_med_60_stack = nsw_med_60.stack().reset_index().rename(columns={"level_1":"category", 0:"count"})
# nsw_med_60_stack = nsw_med_60_stack.set_index('Date')

#%%

def makeLine(df):
	
	template = [
			{
				"title": "NSW daily new Covid-19 cases and hospitalisations",
				"subtitle": "Showing the rolling seven-day average of daily new cases, and the total count of Covid-19 patients in hospital on each day. Last updated {date}".format(date=updatedText),
				"footnote": "",
				"source": "NSW Health, covidlive.com.au",
				"dateFormat": "%Y-%m-%d",
				"yScaleType":"",
				"xAxisLabel": "",
				"yAxisLabel": "",
				"minY": "",
				"maxY": "",
				"x_axis_cross_y":"0",
				"periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "30",
				"margin-bottom": "30",
				"margin-right": "10",
				"tooltip":"<strong>{{#formatDate}}{{Date}}{{/formatDate}}</strong><br/> New cases: {{New cases, 7 day avg}}<br/>In hospital: {{In hospital}}<br/>"
			}
		]
	key = []
	periods = []
	labels = []
	options = [{"colorScheme":"guardian", "lineLabelling":"TRUE", "aria":"FALSE"}] 
	chartId = [{"type":"linechart"}]
	df.fillna(0, inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, options=options, data=chartData, chartId=[{"type":"linechart"}], chartName="nsw-cases-and-hospitalisations")


makeLine(nsw_med_60[['New cases, 7 day avg', "In hospital"]])