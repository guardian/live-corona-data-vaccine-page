#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
import ssl
from datetime import timedelta
from modules.yachtCharter import yachtCharter


testo = ''
testo = '-testo'

# state_json = "https://vaccinedata.covid19nearme.com.au/data/all.json"
state_json = 'https://vaccinedata.covid19nearme.com.au/data/air.json'
# state_json = 'https://vaccinedata.covid19nearme.com.au/data/air_residence.json'

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

#%%
	
df = pd.read_json(state_json)
cols = df.columns.tolist()

# print(cols)
print([x for x in cols if("NSW" in x) & ("COUNT" in x)])

population = {
	"NSW":8166.4* 1000,
	"VIC":6680.6* 1000,
	"QLD":5184.8* 1000,
	"SA":1770.6* 1000,
	"WA":2667.1* 1000,
	"TAS":541.1* 1000,
	"NT":246.5* 1000,
	"ACT":431.2* 1000,
	"AUS":25693.1 * 1000
	}

states = ["NSW","VIC","QLD","SA","WA","TAS","ACT","NT", 'AUS']

# STATE_CLINICS_WA_TOTAL CWTH_AGED_CARE_WA_TOTAL CWTH_PRIMARY_CARE_WA_TOTAL

state_cum = df.copy()

for state in states:
	# state_cum[f'{state}_TOTAL'] = state_cum[f'STATE_CLINICS_{state}_TOTAL'] + state_cum[f'CWTH_AGED_CARE_{state}_TOTAL'] + state_cum[f'CWTH_PRIMARY_CARE_{state}_TOTAL']
	state_cum[f'{state}_TOTAL'] = state_cum[f'AIR_{state}_16_PLUS_FIRST_DOSE_COUNT'] + 	state_cum[f'AIR_{state}_16_PLUS_SECOND_DOSE_COUNT'] + state_cum[f'AIR_{state}_12_15_FIRST_DOSE_COUNT']+ state_cum[f'AIR_{state}_12_15_SECOND_DOSE_COUNT'] + state_cum[f'AIR_{state}_18_PLUS_THIRD_DOSE_COUNT'] + state_cum[f'AIR_{state}_5_11_FIRST_DOSE_COUNT'] + state_cum[f'AIR_{state}_5_11_SECOND_DOSE_COUNT']

state_cum = state_cum[['DATE_AS_AT', 'AUS_TOTAL', 'NSW_TOTAL', "VIC_TOTAL", "QLD_TOTAL", "SA_TOTAL", "WA_TOTAL", "TAS_TOTAL", "ACT_TOTAL", "NT_TOTAL"]]

states_daily = state_cum.copy()

states_daily = states_daily.set_index('DATE_AS_AT')

states_daily = states_daily[['AUS_TOTAL', 'NSW_TOTAL', "VIC_TOTAL", "QLD_TOTAL", "SA_TOTAL", "WA_TOTAL", "TAS_TOTAL", "ACT_TOTAL", "NT_TOTAL"]].sub(states_daily.shift())

states_daily.reset_index(inplace=True)

states_daily = states_daily.rename(columns = {"AUS_TOTAL": "AUS_TOTAL"})

# print(states_daily)



states_daily['DATE_AS_AT'] = pd.to_datetime(states_daily['DATE_AS_AT'])

states =['NSW','VIC','QLD','WA','SA','TAS','NT','ACT','AUS']

short_cols = ['DATE_AS_AT']

states_daily.fillna(0, inplace=True)

for state in states:

	states_daily[f'{state}_7_day_avg'] = states_daily[f'{state}_TOTAL'].rolling(window=7).mean()
	
	states_daily[f'{state}_7_day_avg_per_100'] = round((states_daily[f'{state}_7_day_avg']/population[state])*100,2)

	short_cols.append(f'{state}_7_day_avg_per_100')
	

rolled = states_daily[short_cols]


#%%

zdf = rolled.copy()


oz = zdf[['DATE_AS_AT', 'AUS_7_day_avg_per_100']]
oz.columns = ['Date', 'National']


zdf = zdf[['DATE_AS_AT', 'NSW_7_day_avg_per_100', 'VIC_7_day_avg_per_100', 'QLD_7_day_avg_per_100', 'WA_7_day_avg_per_100', 'SA_7_day_avg_per_100', 'TAS_7_day_avg_per_100', 'NT_7_day_avg_per_100', 'ACT_7_day_avg_per_100']]
zdf.columns = ['Date', 'NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'NT', 'ACT']



melted = pd.melt(zdf, id_vars=['Date'], value_vars=['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'NT', 'ACT'])

melted = melted.sort_values(by=['Date'], ascending=True)

tog = pd.merge(melted, oz, on=['Date'], how='left')

tog.columns = ['Date', 'Code', 'State or territory', 'National']

lastUpdated = tog['Date'].max()

updatedText = lastUpdated.strftime('%-d %B, %Y')

thirty_days = lastUpdated - timedelta(days=30)

tog = tog.loc[tog['Date'] > thirty_days]


tog['Date'] = tog['Date'].dt.strftime("%Y-%m-%d")

tog.set_index('Date', inplace=True)




#%%

# df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'], format="%Y-%m-%d")
# df = df.rename(columns={"REPORT_DATE": "Date"})

# #%%
# pivoted = df.pivot(index='Date', columns='CODE')['VACC_DOSE_CNT']
# states = ["NSW","VIC","QLD","SA","WA","TAS","ACT","NT"]
# daily = pivoted[states]

# for state in states:
# 	daily[state] = daily[state].sub(daily[state].shift())

# daily = daily["2021-04-10":]
# daily[daily < 0] = 0

# #%%
	
# lastUpdated = daily.index[-1]
# newUpdated = lastUpdated + timedelta(days=1)
# updatedText = newUpdated.strftime('%-d %B, %Y')

# # sixty_days = lastUpdated - timedelta(days=60)
# daily.index = daily.index.strftime('%Y-%m-%d')

# daily_stack = daily.stack().reset_index().rename(columns={"level_1":"category", 0:"count"})
# daily_stack = daily_stack.set_index('Date')	


# #%%

def makeStateVaccinations(df):

	template = [
			{
				"title": "Trend in recent daily vaccinations by state and territory",
				"subtitle": "Showing the seven-day rolling average in Covid vaccination doses administered daily per 100 people in each state and territory, versus the national rate. Showing the last 30 days only. Last updated {date}".format(date=updatedText),
				"footnote": "",
				"source": " | Source: Guardian Australia analysis of <a href='https://covidlive.com.au/' target='_blank'>covidlive.com.au</a> data | Data shows vaccinations by state of administration, not by state of residence",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "",
				"timeInterval":"day",
				"tooltip":"<strong>Date: </strong>{{#nicedate}}Date{{/nicedate}}<br/><strong>Rolling average per 100: </strong>{{State or territory}}",
				"periodDateFormat":"",
				"margin-left": "27",
				"margin-top": "25",
				"margin-bottom": "22",
				"margin-right": "22",
				"xAxisDateFormat": "%b %d"
			}
		]
	key = []
	periods = [{"label":"Data change", "start":"2021-08-16","end":"","textAnchor":"start"}]
	labels = []
	options = [{"numCols":4, "chartType":"line", "height":150, "scaleBy":"group"}]
	chartId = [{"type":"smallmultiples"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template,options=options, data=chartData, periods=periods, chartId=chartId, chartName=f"state-vaccinations-boosters-sm-2021{testo}")

makeStateVaccinations(tog)