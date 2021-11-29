#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import requests
from yachtcharter import yachtCharter
import datetime

states =['AUS','NSW','VIC','QLD','WA','SA','TAS','NT','ACT']

cols = ["DATE_AS_AT",
"FIRST_NATIONS_VIC_FIRST_DOSE_TOTAL",
"FIRST_NATIONS_VIC_SECOND_DOSE_TOTAL",
"FIRST_NATIONS_QLD_FIRST_DOSE_TOTAL",
"FIRST_NATIONS_QLD_SECOND_DOSE_TOTAL",
"FIRST_NATIONS_WA_FIRST_DOSE_TOTAL",
"FIRST_NATIONS_WA_SECOND_DOSE_TOTAL",
"FIRST_NATIONS_TAS_FIRST_DOSE_TOTAL",
"FIRST_NATIONS_TAS_SECOND_DOSE_TOTAL",
"FIRST_NATIONS_SA_FIRST_DOSE_TOTAL",
"FIRST_NATIONS_SA_SECOND_DOSE_TOTAL",
"FIRST_NATIONS_ACT_FIRST_DOSE_TOTAL",
"FIRST_NATIONS_ACT_SECOND_DOSE_TOTAL",
"FIRST_NATIONS_NT_FIRST_DOSE_TOTAL",
"FIRST_NATIONS_NT_SECOND_DOSE_TOTAL",
"FIRST_NATIONS_NSW_FIRST_DOSE_TOTAL",
"FIRST_NATIONS_NSW_SECOND_DOSE_TOTAL",
"FIRST_NATIONS_AUS_FIRST_DOSE_TOTAL",
"FIRST_NATIONS_AUS_SECOND_DOSE_TOTAL"]

indig_df = pd.read_csv("https://vaccinedata.covid19nearme.com.au/data/all.csv")

indig_df = indig_df[cols]

newIndigData = pd.DataFrame(columns=['DATE_AS_AT','INDIG_FIRST_DOSE', 'INDIG_SECOND_DOSE'])

for state in states:
	temp = indig_df[['DATE_AS_AT',
				  f'FIRST_NATIONS_{state}_FIRST_DOSE_TOTAL', 
				  f'FIRST_NATIONS_{state}_SECOND_DOSE_TOTAL',
				  ]]
	temp['STATE'] = state
	temp = temp.rename(columns={f'FIRST_NATIONS_{state}_FIRST_DOSE_TOTAL':'INDIG_FIRST_DOSE',f'FIRST_NATIONS_{state}_SECOND_DOSE_TOTAL':'INDIG_SECOND_DOSE'}) 
	newIndigData = newIndigData.append(temp)


newIndigData['DATE_AS_AT'] = pd.to_datetime(newIndigData['DATE_AS_AT'])

newIndigData['weekday'] = newIndigData['DATE_AS_AT'].dt.dayofweek

#%%

population = requests.get("https://interactive.guim.co.uk/docsdata/1EHQCjj3VGo3TlXT6lniSJmsD19C8q2MLSUclmNZV2Yk.json").json()['sheets']['data']

pop_dict = {}

for row in population:
	pop_dict[row['State or territory']] = row

#%%
	
url = 'https://vaccinedata.covid19nearme.com.au/data/air.json'

air_data = pd.read_json(url)
air_data = air_data.rename(columns={"AIR_12_15_FIRST_DOSE_COUNT":"AIR_AUS_12_15_FIRST_DOSE_COUNT", "AIR_12_15_SECOND_DOSE_COUNT":"AIR_AUS_12_15_SECOND_DOSE_COUNT"})
air_cols = list(air_data.columns)
#%%

# short_cols = ['DATE_AS_AT']

# for state in states:
# 	short_cols.append(f'AIR_{state}_16_PLUS_FIRST_DOSE_COUNT')
# 	short_cols.append(f'AIR_{state}_16_PLUS_SECOND_DOSE_COUNT')

newData = pd.DataFrame(columns=['DATE_AS_AT','FIRST_DOSE_COUNT_16', 'SECOND_DOSE_COUNT_16','FIRST_DOSE_COUNT_12', 'SECOND_DOSE_COUNT_12' ])

for state in states:
	temp = air_data[['DATE_AS_AT',
				  f'AIR_{state}_16_PLUS_FIRST_DOSE_COUNT', 
				  f'AIR_{state}_16_PLUS_SECOND_DOSE_COUNT',
				  f'AIR_{state}_12_15_FIRST_DOSE_COUNT',
				  f'AIR_{state}_12_15_SECOND_DOSE_COUNT',
				  ]]
	temp['STATE'] = state
	temp = temp.rename(columns={f'AIR_{state}_16_PLUS_FIRST_DOSE_COUNT':'FIRST_DOSE_COUNT_16',f'AIR_{state}_16_PLUS_SECOND_DOSE_COUNT':'SECOND_DOSE_COUNT_16', f'AIR_{state}_12_15_FIRST_DOSE_COUNT':'FIRST_DOSE_COUNT_12', f'AIR_{state}_12_15_SECOND_DOSE_COUNT':'SECOND_DOSE_COUNT_12'}) 
	newData = newData.append(temp)

# newData = pd.read_csv("dummy.csv")
newData['DATE_AS_AT'] = pd.to_datetime(newData['DATE_AS_AT'])
newData['weekday'] = newData['DATE_AS_AT'].dt.dayofweek


# print(newData['DATE_AS_AT'].dtypes)	
#%%
newData_sundays = newData[newData['weekday'] == 6]
newIndigData_sundays = newIndigData[newIndigData['weekday'] == 6]

most_recent = newData_sundays['DATE_AS_AT'].iloc[-1]

latest_states = newData[newData['DATE_AS_AT'] == most_recent]

latest_indig = newIndigData[newIndigData['DATE_AS_AT'] == most_recent]

latest_states['FIRST_DOSE'] = latest_states['FIRST_DOSE_COUNT_16'] + latest_states['FIRST_DOSE_COUNT_12']

latest_states['SECOND_DOSE'] = latest_states['SECOND_DOSE_COUNT_16'] + latest_states['SECOND_DOSE_COUNT_12']

#%%
merged = latest_states.merge(latest_indig[['INDIG_FIRST_DOSE', 'INDIG_SECOND_DOSE', 'STATE']], on="STATE")

merged = merged[merged['STATE'] != 'AUS']
merged['NI_FIRST_DOSE'] = merged['FIRST_DOSE'] - merged['INDIG_FIRST_DOSE']
merged['NI_SECOND_DOSE'] = merged['SECOND_DOSE'] - merged['INDIG_SECOND_DOSE']

merged['Indigenous 12+ population (AIR 2021)'] = merged.apply(lambda x: pop_dict[x['STATE']]['Indigenous 12+ population (AIR 2021)'], axis=1)

merged['Indigenous 12+ population (AIR 2021)'] = merged['Indigenous 12+ population (AIR 2021)'].astype('int64')

merged['non-Indigenous 12+ (ERP/AIR)'] = merged.apply(lambda x: pop_dict[x['STATE']]['non-Indigenous 12+ (ERP - AIR)'], axis=1)

merged['non-Indigenous 12+ (ERP/AIR)'] = merged['non-Indigenous 12+ (ERP/AIR)'].astype('int64')

merged['% Indigenous at least one dose'] = merged['INDIG_FIRST_DOSE'] / merged['Indigenous 12+ population (AIR 2021)'] * 100
merged['% Indigenous fully vaccinated'] = merged['INDIG_SECOND_DOSE'] / merged['Indigenous 12+ population (AIR 2021)'] * 100

merged['non-Indigenous % at least one dose'] = merged['NI_FIRST_DOSE'] / merged['non-Indigenous 12+ (ERP/AIR)'] * 100
merged['non-Indigenous % fully vaccinated'] = merged['NI_SECOND_DOSE'] / merged['non-Indigenous 12+ (ERP/AIR)'] * 100

final_table = merged[['STATE','% Indigenous fully vaccinated', '% Indigenous at least one dose', 'non-Indigenous % fully vaccinated','non-Indigenous % at least one dose']]

final_table = final_table.round(2)

final_table.rename(columns={"STATE": "State or territory"}, inplace=True)

date_str = lastUpdated = datetime.datetime.strftime(most_recent, '%d %B %Y')

#%%

def makeChart1(df):

	template = [
			{
				"title": "Comparing vaccination rates for Indigenous people v non-Indigenous people",
				"subtitle": "Comparing the vaccination rates for Indigenous people (12+) by state and territory, with the non-Indigenous rate (12+) for each state and territory. Last updated {date}".format(date=date_str),
				"footnote": "",
				"source": " | Source: Department of Health data scraped by Ken Tsang, AIR and ABS population figures",
				"dateFormat": "",
				"xAxisLabel": "",
				"yAxisLabel": "",
				"margin-left": "50",
				"margin-top": "20",
				"margin-bottom": "20",
				"margin-right": "20",
				"xAxisDateFormat": "%b %d",
				"tooltip":""
				
			}
		]

	periods = []
	key = [{"key":"% Indigenous fully vaccinated (12+)","colour":"#4575b4"},
			{"key":"% Indigenous at least one dose (12+)","colour":"#74add1"},
			{"key":"non-Indigenous % fully vaccinated (12+)","colour":"#d73027"},
			{"key":"non-Indigenous % at least one dose (12+)","colour":"#f46d43"}]
	chartId = [{"type":"groupedbar"}]
	df.fillna('', inplace=True)
# 	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, data=chartData, chartId=chartId, chartName="aus-indigenous-state-bar-chart", key=key)

makeChart1(final_table)

