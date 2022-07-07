#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import requests
# Jxeeno's data by state of residence

url = "https://vaccinedata.covid19nearme.com.au/data/air_residence.json"
r = requests.get(url)

df = pd.DataFrame(r.json())

#%%

cols = list(df.columns)
df = df.fillna(0)
df['first'] = df['AIR_RESIDENCE_FIRST_DOSE_COUNT'] + df['AIR_RESIDENCE_FIRST_DOSE_APPROX_COUNT']
df['second'] = df['AIR_RESIDENCE_SECOND_DOSE_COUNT'] + df['AIR_RESIDENCE_SECOND_DOSE_APPROX_COUNT']

df['total'] = df['first'] + df['second']


#%%

population_all = {
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

population_16 = {
	"NSW":6565651,
	"ACT":344037
	}



#%%



df2 = df[(df['AGE_LOWER'] == 16) & (df['AGE_UPPER'] == 999)]

totals = df2[['DATE_AS_AT', 'STATE', 'total']] 

totals = totals[(totals['STATE'] == 'NSW') | (totals['STATE'] == 'ACT')]

pivoted = totals.pivot(index='DATE_AS_AT', columns='STATE', values='total')

#%%
states = ['NSW', 'ACT']
daily = pivoted.copy()

for state in states:
	daily[state] = daily[state].sub(daily[state].shift())

#%%


for state in states:
	daily[state + "_rate"] = daily[state] / population_16[state] * 100
	daily[state + "_rate_7day_mean"] = daily[state + "_rate"].rolling(7).mean()

#%%



# gp = df[['DATE_AS_AT', 'STATE', 'first', 'second']].groupby(['DATE_AS_AT', 'STATE']).sum()
