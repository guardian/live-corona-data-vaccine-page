#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import requests

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
states =['AUS','NSW','VIC','QLD','WA','SA','TAS','NT','ACT']
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
print(newData)	