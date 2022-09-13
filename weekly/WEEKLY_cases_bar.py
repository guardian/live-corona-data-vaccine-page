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
	# inter = inter.loc[inter['WeekDay'] == 6]
	inter = inter.loc[inter['WeekDay'] == 4]

	## Sort and difference

	inter.sort_values(by=['REPORT_DATE'], ascending=True, inplace=True)

	inter[out_name] = inter[coller].diff()

	inter = inter[['REPORT_DATE', out_name]]

	inter['REPORT_DATE'] = inter['REPORT_DATE'].dt.strftime("%Y-%m-%d")
	inter.set_index('REPORT_DATE', inplace=True)

	# p = inter 

	# print(p)
	# print(p.columns.tolist())

	return inter 

cases = getweekly(oz, 'CASE_CNT', 'Weekly cases')


#%%

latest_date = oz['REPORT_DATE'].max()
init_date = datetime.datetime.strptime(latest_date, "%Y-%m-%d")
display_date = datetime.datetime.strftime(init_date, "%-d %B %Y")

def makeTotalDeathBars(df):


	template = [
			{
				"title": "Weekly Covid-19 cases in Australia",
				"subtitle": f"Showing the count on the friday of each week since June 2021, as reported by states and territories. Dates used are the date reported. Testing criteria changed significantly on 5 January 2022, and cases after this point should be considered an underestimate. Last updated {display_date}.",
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
				"tooltip":"<strong>{{#nicerdate}}REPORT_DATE{{/nicerdate}}</strong><br><strong>Weekly cases</strong>: {{Total}}"
			}
		]

	periods = []
	key = [{"key":"Weekly cases","colour":"#fc9272"}]
	chartId = [{"type":"stackedbar"}]
	options = [{"trendColors":"#751480"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	# yachtCharter(template=template, data=chartData, options=options, chartId=chartId, trendline=deaths_avg, key=key, chartName="aus-weekly-covid-cases-stacked-bar".format(test=test))
	yachtCharter(template=template, data=chartData, options=options, chartId=chartId, key=key, chartName="aus-weekly-covid-cases-stacked-bar".format(test=test))


from modules.yachtCharter import yachtCharter
makeTotalDeathBars(cases)

