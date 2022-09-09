#%%
import pandas as pd 
import requests
import os 
import datetime

# test = ""
test = "-test"

# READ IN COVIDLIVE CASE DATA

cl = 'https://interactive.guim.co.uk/2021/02/coronavirus-widget-data/oz-covid-cases.json'
cl = pd.read_json(cl)

#%%

#%%

deaths = cl.loc[cl['CODE'] == "AUS"].copy()
deaths['DEATH_CNT'] = pd.to_numeric(deaths['DEATH_CNT'])

deaths['Incremental'] = deaths['DEATH_CNT'].diff(periods=-1)

deaths = deaths[['REPORT_DATE', 'Incremental']]

deaths.columns = ['Date', "Total"]

#%%

inter = deaths.copy()
inter['Date'] = pd.to_datetime(inter['Date'])
inter.set_index('Date', inplace=True)

deaths_resampled = inter.resample('w')

p = deaths_resampled

# p = inter 

print(p)
print(p.columns.tolist())

#%%


#%%

def makeTotalDeathBars(df):


	template = [
			{
				"title": "Deaths per day from Covid-19 in Australia",
				"subtitle": "Showing the daily count of deaths* as reported by states and territories. Dates used are the date of death where known, or the date reported. Spike on the 1st of April 2022 due to a backlog of cases being reported. Last updated {date}".format(date=lastUpdated),
				"footnote": "",
				"source": " | Source: Covidlive.com.au. *NSW Health added 331 backdated deaths to its total on the 1st of April 2022. Guardian Australia added the backdated data to the preceding 104 days.",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "Deaths",
				"timeInterval":"day",
				"tooltip":"TRUE",
				# "periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "20",
				"margin-bottom": "20",
				"margin-right": "25",
				"xAxisDateFormat": "%d %b, '%y",
				# "tooltip":"<strong>{{#nicerdate}}{{Date}}{{/nicerdate}}</strong><br><strong>{{group}}</strong>: {{groupValue}}"
				"tooltip":"<strong>{{#nicerdate}}Date{{/nicerdate}}</strong><br><strong>Deaths</strong>: {{Total}}"
			}
		]

	periods = []
	key = [{"key":"Deaths","colour":"#cfa1d4"}]
	chartId = [{"type":"stackedbar"}]
	options = [{"trendColors":"#751480"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, data=chartData, options=options, chartId=chartId, trendline=deaths_avg, key=key, chartName="aus-total-corona-deaths".format(test=test))

# from modules.yachtCharter import yachtCharter
# from modules.numberFormat import numberFormat
# makeTotalDeathBars(merged)