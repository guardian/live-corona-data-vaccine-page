#%%
import pandas as pd 
import requests
import os 
import datetime

# test = ""
test = "-test"

# READ IN COVIDLIVE CASE DATA

# cl = 'https://interactive.guim.co.uk/2021/02/coronavirus-widget-data/oz-covid-cases.json'
cl = 'https://covidlive.com.au/covid-live.json'
cl = pd.read_json(cl)

#%%

oz = cl.loc[cl['CODE'] == 'AUS']
oz = oz.loc[oz['REPORT_DATE'] > "2021-06-04"]

def getweekly(frame, coller, out_name):
	inter = frame.copy()

	## Grab just Friday
	inter['REPORT_DATE'] = pd.to_datetime(inter['REPORT_DATE'])
	inter['WeekDay'] = inter['REPORT_DATE'].dt.weekday
	inter = inter.loc[inter['WeekDay'] == 4]

	## Sort and difference

	inter.sort_values(by=['REPORT_DATE'], ascending=True, inplace=True)

	inter[out_name] = inter[coller].diff()

	inter = inter[['REPORT_DATE', out_name]]

	inter['REPORT_DATE'] = inter['REPORT_DATE'].dt.strftime("%Y-%m-%d")
	inter.set_index('REPORT_DATE', inplace=True)

	p = inter 

	# print(p)
	# print(p.columns.tolist())

	return inter 

deaths = getweekly(oz, 'DEATH_CNT', 'Weekly deaths')

#%%

# ### Need to make a trend line

# deaths_avg = deaths.copy()
# deaths_avg = deaths_avg.reset_index()
# deaths_avg['Trend'] = deaths_avg['Weekly deaths'].rolling(window=4).mean()

# deaths_avg = deaths_avg[['Trend']]

# deaths_avg.fillna('', inplace=True)
# deaths_avg.reset_index(inplace=True)
# deaths_avg = deaths_avg.to_dict(orient='records')

# p = deaths_avg
# print(p)
# # print(p.columns.tolist())



#%%

latest_date = oz['REPORT_DATE'].max()
init_date = datetime.datetime.strptime(latest_date, "%Y-%m-%d")
display_date = datetime.datetime.strftime(init_date, "%-d %B %Y")

def makeTotalDeathBars(df):


	template = [
			{
				"title": "Weekly deaths from Covid-19 in Australia",
				"subtitle": f"Showing the count on the friday of each week since June 2021, as reported by states and territories. Dates used are the date of death where known, or the date reported. Last updated {display_date}.",
				"footnote": "",
				"source": " | Source: Covidlive.com.au, Guardian Australia",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "Deaths",
				# "timeInterval":"week",
				"tooltip":"TRUE",
				# "periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "20",
				"margin-bottom": "20",
				"margin-right": "25",
				"xAxisDateFormat": "%b %y",
				# "tooltip":"<strong>{{#nicerdate}}{{Date}}{{/nicerdate}}</strong><br><strong>{{group}}</strong>: {{groupValue}}"
				"tooltip":"<strong>{{#nicerdate}}REPORT_DATE{{/nicerdate}}</strong><br><strong>Weekly deaths</strong>: {{Total}}"
			}
		]

	periods = []
	key = [{"key":"Deaths","colour":"#cfa1d4"}]
	chartId = [{"type":"stackedbar"}]
	options = [{"trendColors":"#751480"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	# yachtCharter(template=template, data=chartData, options=options, chartId=chartId, trendline=deaths_avg, key=key, chartName="aus-weekly-covid-deaths-stacked-bar".format(test=test))
	yachtCharter(template=template, data=chartData, options=options, chartId=chartId, key=key, chartName="aus-weekly-covid-deaths-stacked-bar".format(test=test))


from modules.yachtCharter import yachtCharter
makeTotalDeathBars(deaths)

