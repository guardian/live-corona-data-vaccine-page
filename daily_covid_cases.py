#%%
import pandas as pd 
from modules.yachtCharter import yachtCharter
from modules.numberFormat import numberFormat
import requests
import os 
import datetime

test = ""
# test = "-test"

#%%
## Read in existing Guardian Oz data
old = requests.get('https://interactive.guim.co.uk/docsdata/1q5gdePANXci8enuiS4oHUJxcxC13d6bjMRSicakychE.json').json()['sheets']
old_df = pd.DataFrame(old['updates'])
old_df.Date = pd.to_datetime(old_df.Date, format="%d/%m/%Y")

old_df = old_df[['State', 'Date', 'Cumulative case count']]

old_grouped = old_df.groupby(by=['Date'])['Cumulative case count'].sum()

#%%

# READ IN COVIDLIVE CASE DATA

cl = 'https://interactive.guim.co.uk/2021/02/coronavirus-widget-data/oz-covid-cases.json'
cl = pd.read_json(cl)

oz_new_cases = cl.loc[cl['CODE'] == "AUS"].copy()
oz_new_cases['CASE_CNT'] = pd.to_numeric(oz_new_cases['CASE_CNT'])

oz_new_cases['Incremental'] = oz_new_cases['CASE_CNT'].diff(periods=-1)

oz_new_cases['REPORT_DATE'] = pd.to_datetime(oz_new_cases['REPORT_DATE'], format="%Y-%m-%d")
lastUpdated = oz_new_cases['REPORT_DATE'].max()
oz_new_cases['REPORT_DATE'] = oz_new_cases['REPORT_DATE'].dt.strftime('%Y-%m-%d')

oz_new_cases = oz_new_cases[['REPORT_DATE','Incremental']]

oz_new_cases.columns = ['Date', "Total"]

oz_new_cases = oz_new_cases.sort_values(by='Date', ascending=True)

oz_new_cases.set_index('Date', inplace=True)

oz_trend_cases = oz_new_cases.copy()

oz_trend_cases = oz_trend_cases[:-1].rolling(7).mean()

oz_trend_cases = oz_trend_cases.round(1)

# oz_new_cases['2021-08-21':'2021-08-21']['Total'] = oz_new_cases['2021-08-21':'2021-08-21']['Total'] + 832

lastUpdated = datetime.datetime.strftime(lastUpdated, "%d/%m/%Y")

oz_new_cases.index.name = None

#%%

def makeNationalBars(df):

	df.rename(columns={"Total": "New cases"}, inplace=True)

	template = [
			{
				"title": "Daily new coronavirus cases in Australia",
				"subtitle": "Showing the daily count of new cases as reported by states and territories. Most recent day may show incomplete data. Last updated {date}".format(date=lastUpdated),
				"footnote": "",
				"source": " | Source: Covidlive.com.au",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "Date",
				"yAxisLabel": "Cases",
				"margin-left": "50",
				"margin-top": "20",
				"margin-bottom": "20",
				"margin-right": "20",
				"xAxisDateFormat": "%b %d",
				"tooltip":"<strong>{{#formatDate}}{{data.index}}{{/formatDate}}</strong><br><strong>{{group}}</strong>: {{groupValue}}"
				
			}
		]

	periods = []
	key = []
	chartId = [{"type":"stackedbar"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, data=chartData, chartId=chartId, chartName="aus-national-total-corona-cases{test}".format(test=test), key=key)

makeNationalBars(oz_new_cases)

#%%

def makeNationalLine(df):

	df.rename(columns={"Total": "Trend in cases"}, inplace=True)

	template = [
			{
				"title": "Trend in daily new coronavirus cases in Australia",
				"subtitle": "Showing the seven-day rolling average of new cases as reported by states and territories. Most recent day may show incomplete data. Last updated {date}".format(date=lastUpdated),
				"footnote": "",
				"source": " | Source: Covidlive.com.au",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "Date",
				"yAxisLabel": "",
				"margin-left": "50",
				"margin-top": "20",
				"margin-bottom": "20",
				"margin-right": "20",
				"xAxisDateFormat": "%b %d",
				"tooltip":"<strong>{{#formatDate}}{{Date}}{{/formatDate}}</strong><br><strong>Trend in cases</strong>: {{Trend in cases}}"
				
			}
		]

	periods = []
	key = []
	chartId = [{"type":"linechart"}]
	options = [{"colorScheme":"guardian", "lineLabelling":"TRUE", "aria":"TRUE"}] 
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, options=options, data=chartData, chartId=chartId, chartName="aus-national-trend-new-cases", key=key)

makeNationalLine(oz_trend_cases)


#%%

deaths = cl.loc[cl['CODE'] == "AUS"].copy()
deaths['DEATH_CNT'] = pd.to_numeric(deaths['DEATH_CNT'])

deaths['Incremental'] = deaths['DEATH_CNT'].diff(periods=-1)

deaths = deaths[['REPORT_DATE', 'Incremental']]

deaths.columns = ['Date', "Total"]
deaths = deaths.sort_values(by='Date', ascending=True)
deaths.set_index('Date', inplace=True)
deaths.index.name = None


def makeTotalDeathBars(df):


	template = [
			{
				"title": "Deaths per day from Covid-19 in Australia",
				"subtitle": "Showing the daily count of deaths as reported by states and territories. Dates used are the date of death where known, or the date reported. Last updated {date}".format(date=lastUpdated),
				"footnote": "",
				"source": " | Source: Covidlive.com.au",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "Deaths",
				"timeInterval":"day",
				"tooltip":"TRUE",
				# "periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "20",
				"margin-bottom": "20",
				"margin-right": "20",
				"xAxisDateFormat": "%b %d",
				"tooltip":"<strong>{{#formatDate}}{{data.index}}{{/formatDate}}</strong><br><strong>{{group}}</strong>: {{groupValue}}"
				
			}
		]

	periods = []
	key = [{"key":"Deaths","colour":"#000"}]
	chartId = [{"type":"stackedbar"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, data=chartData, chartId=chartId, chartName="aus-total-corona-deaths{test}".format(test=test), key=key)

makeTotalDeathBars(deaths)

states = cl.loc[cl['CODE'] != "AUS"].copy()
states['CASE_CNT'] = pd.to_numeric(states['CASE_CNT'])

# states['Incremental'] = states['DEATH_CNT'].diff(periods=-1)
# states['REPORT_DATE'] = pd.to_datetime(states['REPORT_DATE'], format="%Y-%m-%d")

states = states[['REPORT_DATE', 'CODE', 'CASE_CNT']]


states.columns = ['Date', 'State', "Total"]
states = states.sort_values(by='Date', ascending=True)
# states.set_index('Date', inplace=True)
# states.index.name = None

states = states.pivot(index="Date", columns='State')['Total'].reset_index()
states.columns.name=None
states.index.name = None

states.set_index('Date', inplace=True)

def makeCumulativeChart(df):
	
	lastUpdatedInt = df.index[-1]

	template = [
			{
				"title": "Cumulative count of confirmed Covid-19 cases by state and territory",
				"subtitle": "The most recent day is usually based on incomplete data. Last updated {date}".format(date=lastUpdated),
				"footnote": "",
				"source": " | Source: Covidlive.com.au",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "Cumulative cases",
				"timeInterval":"day",
				"tooltip":"TRUE",
				# "periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "20",
				"margin-bottom": "20",
				"margin-right": "20",
				"xAxisDateFormat": "%b %d"
			}
		]
	key = [
		{"key":"NSW","colour":"#000000"},
		{"key":"VIC","colour":"#0000ff"},
		{"key":"QLD","colour":"#9d02d7"},
		{"key":"SA","colour":"#cd34b5"},
		{"key":"WA","colour":"#ea5f94"},
		{"key":"TAS","colour":"#fa8775"},
		{"key":"ACT","colour":"#ffb14e"},
		{"key":"NT","colour":"#ffd700"}
		]
	periods = []
	labels = []
	chartId = [{"type":"stackedbarchart"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, data=chartData, chartId=chartId, chartName="australian-covid-cases-2020{test}".format(test=test), key=key)

makeCumulativeChart(states)



