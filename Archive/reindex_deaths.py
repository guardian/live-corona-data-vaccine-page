
#%%
import pandas as pd 
from modules.yachtCharter import yachtCharter
from modules.numberFormat import numberFormat
import requests
import os 
import datetime

# test = ""
test = "-test"
test = "-test298347293842"

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


#%%

deaths = cl.loc[cl['CODE'] == "AUS"].copy()
deaths['DEATH_CNT'] = pd.to_numeric(deaths['DEATH_CNT'])

deaths['Incremental'] = deaths['DEATH_CNT'].diff(periods=-1)

deaths = deaths[['REPORT_DATE', 'Incremental']]

deaths.columns = ['Date', "Total"]

#%%

useLatest = True
current = pd.DataFrame([{"Date":"2022-01-21", "Total":80}])
merged = pd.DataFrame()

if useLatest:
	print("Using latest values")
	merged = pd.concat([current, deaths])
else:
	print("Not latest")
	merged = deaths

merged['Total'] = pd.to_numeric(merged['Total'])

merged.loc[merged['Date'] == '2022-04-01', 'Total'] = 29
merged.loc[((merged['Date'] > '2021-12-17') & (merged['Date'] <= '2022-04-01')), 'Total'] = merged.loc[((merged['Date'] > '2021-12-17') & (merged['Date'] <= '2022-04-01'))]['Total'] + 3

merged.set_index('Date', inplace=True)

merged = merged[~merged.index.duplicated()]

merged = merged.sort_values(by='Date', ascending=True)



#%%
deaths_avg = merged.copy()
deaths_avg['Trend'] = deaths_avg['Total'].rolling(window=7).mean()

deaths_avg = deaths_avg[['Trend']]

deaths_avg.fillna('', inplace=True)
deaths_avg.reset_index(inplace=True)
deaths_avg = deaths_avg.to_dict(orient='records')


#%%


# merged.index.name = None





p = merged

p = p.reset_index()
p = p.loc[(p['Date'] >= '2022-03-27') & (p['Date'] < '2022-04-04')]




print(p)
print(p.columns.tolist())

# print(merged)


def makeTotalDeathBars(df):


	template = [
			{
				"title": "Deaths per day from Covid-19 in Australia",
				"subtitle": "Showing the daily count of deaths as reported by states and territories. Dates used are the date of death where known, or the date reported. Spike on the 1st of April 2022 due to a backlog of cases being reported. Last updated {date}".format(date=lastUpdated),
				"footnote": "",
				"source": " | Source: Covidlive.com.au. NSW Health added 331 deaths to its total on the 1st of April 2022.",
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

makeTotalDeathBars(merged)