from getData import getData
from modules.yachtCharter import yachtCharter
from modules.syncDoc import syncDoc
import pandas as pd
import numpy as np
import requests
from datetime import datetime

test = ""
# test = "-test"

state_order = ['NSW','VIC',	'QLD','SA', 'WA','TAS',	'ACT','NT']
state_order2 = ['NSW','VIC','QLD','SA', 'WA','TAS',	'ACT']

#%%

# getData()

#%%

states = requests.get('https://interactive.guim.co.uk/docsdata/1q5gdePANXci8enuiS4oHUJxcxC13d6bjMRSicakychE.json').json()['sheets']

#%%

pd.options.mode.chained_assignment = None  # default='warn'
states_df = pd.DataFrame(states['updates'])
states_df.Date = pd.to_datetime(states_df.Date, format="%d/%m/%Y")

deaths_df = states_df

states_df['Cumulative case count'] = pd.to_numeric(states_df['Cumulative case count'])
deaths_df['Cumulative deaths'] = pd.to_numeric(states_df['Cumulative deaths'])

states_df = states_df.dropna(axis=0,subset=['Cumulative case count'])
deaths_df = deaths_df.dropna(axis=0,subset=['Cumulative deaths'])

states_df = states_df.sort_values(['Date','State', 'Cumulative case count']).drop_duplicates(['State', 'Date'], keep='last')
deaths_df = deaths_df.sort_values(['Date','State', 'Cumulative deaths']).drop_duplicates(['State', 'Date'], keep='last')

states_df_og = states_df

states_df = states_df.pivot(index='Date', columns='State', values='Cumulative case count')
deaths_df = deaths_df.pivot(index='Date', columns='State', values='Cumulative deaths')

#%%

totals_df = pd.DataFrame(states['latest totals'])

#%%

states_df_daily = pd.DataFrame()

for col in state_order:
	print(col)
	tempSeries = states_df[col].dropna()
	tempSeries = tempSeries.sub(tempSeries.shift())
	tempSeries.iloc[0] = states_df[col].dropna().iloc[0]
	states_df_daily = pd.concat([states_df_daily, tempSeries], axis=1)

states_df_daily.iloc[0] = states_df.iloc[0]


deaths_df_daily = pd.DataFrame()

for col in state_order2:
	print(col)
	tempSeries = deaths_df[col].dropna()
	tempSeries = tempSeries.sub(tempSeries.shift())
	tempSeries.iloc[0] = deaths_df[col].dropna().iloc[0]
	deaths_df_daily = pd.concat([deaths_df_daily, tempSeries], axis=1)

deaths_df_daily.iloc[0] = states_df.iloc[0]

#%%

date_index = pd.date_range(start='2020-01-23', end=states_df.index[-1])

states_df = states_df.reindex(date_index)
deaths_df = deaths_df.reindex(date_index)

states_df_daily = states_df_daily.reindex(date_index)

states_df.index = states_df.index.strftime('%Y-%m-%d')
deaths_df.index = deaths_df.index.strftime('%Y-%m-%d')

states_df_daily = states_df_daily.fillna(0)
states_df_daily.index = states_df_daily.index.strftime('%Y-%m-%d')

states_df = states_df.fillna(method='ffill')
states_df = states_df.fillna(0)
states_df = states_df[state_order]

deaths_df = deaths_df.fillna(method='ffill')
deaths_df = deaths_df.fillna(0)
states_df = states_df[state_order2]


total_cum = pd.DataFrame()
total_cum['Total'] = states_df.sum(axis=1)
total_cum['pct_change'] = total_cum['Total'].pct_change()
total_cum = total_cum["2020-02-20":]
total_cum = total_cum[:-1]

states_df_daily = states_df_daily[state_order]

daily_total = pd.DataFrame()
daily_total['Total'] = states_df_daily.sum(axis=1)

lastUpdated = daily_total.index[-1]

deaths_total = pd.DataFrame()
deaths_total['Deaths'] = deaths_df_daily.sum(axis=1)
deaths_total.index = deaths_total.index.strftime('%Y-%m-%d')

restack_states_daily = states_df_daily.stack().reset_index()

restack_states_daily = restack_states_daily.rename(columns={"level_0":"Date","level_1":"State",0:"Cases"})


#%%

# % positive rate for testing

states_df_og['Tests conducted (total)'] = pd.to_numeric(states_df_og['Tests conducted (total)'])
states_df_og['pct_positive'] = states_df_og['Cumulative case count']/states_df_og['Tests conducted (total)'] * 100
states_df_og = states_df_og.replace([np.inf, -np.inf], np.nan)
testing_pct = states_df_og.pivot(index='Date', columns='State', values='pct_positive')
testing_pct = testing_pct["2020-03-15":]


#%%


total_cum.index = pd.to_datetime(total_cum.index, format="%Y-%m-%d")
total_cum['pct_change'] = total_cum['pct_change']*100
total_cum['5 day average'] = total_cum['pct_change'].rolling(5).mean()
total_cum.index = total_cum.index.strftime('%Y-%m-%d')
# total_cum.to_csv('data-output/total-cumulative.csv')


#%%

def makeCumulativeChart(df):
	
	lastUpdatedInt = df.index[-1]

	template = [
			{
				"title": "Cumulative count of confirmed Covid-19 cases by state and territory",
				"subtitle": "The most recent day is usually based on incomplete data. Last updated {date}".format(date=lastUpdatedInt),
				"footnote": "",
				"source": " | Source: <a href='' target='_blank'>Guardian Australia analysis of state and territory data</a>",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "Cumulative cases",
				"timeInterval":"day",
				"tooltip":"TRUE",
				"periodDateFormat":"",
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

	yachtCharter(template=template, data=chartData, chartId=chartId, chartName="australian-covid-cases-2020", key=key)

makeCumulativeChart(states_df)
	
#%%

def makeDailyStatesChart(df):
	
	lastUpdatedInt = df['Date'].iloc[-1]

	template = [
			{
				"title": "Daily count of confirmed Covid-19 cases by state and territory",
				"subtitle": "The most recent day is usually based on incomplete data. States can exclude previously reported cases which may result in a negative number, but we are backdating excluded cases where possible. Last updated {date}".format(date=lastUpdatedInt),
				"footnote": "",
				"source": " | Source: <a href='' target='_blank'>Guardian Australia analysis of state and territory data</a>",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "Cumulative cases",
				"timeInterval":"day",
				"tooltip":"<strong>Date: </strong>{{#nicedate}}Date{{/nicedate}}<br/><strong>Cases: </strong>{{Cases}}",
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
	chartId = [{"type":"smallmultiples"}]
	df.fillna('', inplace=True)
	chartData = df.to_dict('records')

	yachtCharter(template=template, data=chartData, chartId=chartId, chartName="australian-states-daily-covid-cases-2020")

makeDailyStatesChart(restack_states_daily)

#%%

def makeTotalDeathBars(df):

# 	lastUpdatedInt =  df.index[-1]
	
	template = [
			{
				"title": "Deaths per day from Covid-19 in Australia",
				"subtitle": "Showing the daily count of deaths as reported by states and territories. Dates used are the date of death where known, or the date reported. Last updated {date}".format(date=lastUpdated),
				"footnote": "",
				"source": "",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "Deaths",
				"timeInterval":"day",
				"tooltip":"TRUE",
				"periodDateFormat":"",
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

makeTotalDeathBars(deaths_total)

#%%
def makeNationalBars(df):

	df.rename(columns={"Total": "New cases"}, inplace=True)
# 	lastUpdatedInt =  df.index[-1]
	
	template = [
			{
				"title": "Daily new coronavirus cases in Australia",
				"subtitle": "Showing the daily count of new cases as reported by states and territories. Most recent day may show incomplete data. Last updated {date}".format(date=lastUpdated),
				"footnote": "",
				"source": "",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "Cases",
				"timeInterval":"day",
				"tooltip":"TRUE",
				"periodDateFormat":"",
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

makeNationalBars(daily_total)