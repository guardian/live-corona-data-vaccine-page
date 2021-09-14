#%%
import pandas as pd
import requests
import os
import ssl
from modules.yachtCharter import yachtCharter
import numpy as np
import datetime
import pytz


#%%
# fixes ssl error on OSX???

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

pops = {'NT':246.5* 1000, 'NSW':8166.4* 1000,
'VIC':6680.6* 1000, 'QLD':5184.8* 1000,
'ACT':431.2* 1000, 'SA':1770.6* 1000,
 'WA':2667.1* 1000, 'TAS':541.1* 1000}

# source: https://www.abs.gov.au/statistics/people/population/national-state-and-territory-population/sep-2020

# 16+ population counts:

sixteen_pop = {
    'NT':190571, 'NSW':6565651, 'VIC':5407574,
    'QLD':4112707, 'ACT':344037,
    'SA':1440400, 'WA':2114978, 'TAS':440172, "AUS":20619959}

# source: https://www.health.gov.au/sites/default/files/documents/2021/07/covid-19-vaccine-rollout-update-5-july-2021.pdf

data = pd.read_json('https://covidlive.com.au/covid-live.json')
cols = list(data.columns)
# short_cols =	 ['DATE_AS_AT','STATE','AIR_RESIDENCE_FIRST_DOSE_PCT','AIR_RESIDENCE_SECOND_DOSE_PCT','AIR_RESIDENCE_FIRST_DOSE_COUNT','AIR_RESIDENCE_SECOND_DOSE_COUNT']

short_cols = ['REPORT_DATE','CODE','VACC_DOSE_CNT','VACC_FIRST_DOSE_CNT']

#%%

# 'AIR_RESIDENCE_FIRST_DOSE_APPROX_COUNT',
#        'AIR_RESIDENCE_SECOND_DOSE_APPROX_COUNT', 'ABS_ERP_JUN_2020_POP',
#        'VALIDATED', 'URL', 'AIR_RESIDENCE_FIRST_DOSE_APPROX_COUNT',
#        'AIR_RESIDENCE_SECOND_DOSE_COUNT'

# Time between doses AZ 4 to 8 weeks, Pfizer 3 to 6 weeks
# https://www.health.gov.au/initiatives-and-programs/covid-19-vaccines/getting-vaccinated-for-covid-19/covid-19-vaccine-information-for-people-in-greater-sydney

vax_assumptions = requests.get("https://interactive.guim.co.uk/docsdata/14PY-eDz_KYTgeyVVBFUDu9muZ2s2JnJ6zMoLa3U1B7I.json").json()['sheets']['data']

vax_assump_df = pd.DataFrame(vax_assumptions)
# cols = vax_assump_df.columns
vax_assump_df = vax_assump_df.apply(pd.to_numeric, errors="ignore")
vax_assump_df['pfizer_proportion'] = vax_assump_df['pfizer_total'] / (vax_assump_df['pfizer_total'] + vax_assump_df['az_total'])
vax_assump_df['az_proportion'] = vax_assump_df['az_total'] / (vax_assump_df['pfizer_total'] + vax_assump_df['az_total'])

#%%

# variables set up for state projections

date_index = pd.date_range(start='2021-07-27', end='2021-12-31')	


state = "VIC"
assumptions_cutoff = datetime.datetime.strptime("2021-09-01", "%Y-%m-%d")
end_year = datetime.datetime.strptime("2022-01-01", "%Y-%m-%d")
temp_state = data.loc[data['CODE'] == state].copy()
temp_state = temp_state.loc[(temp_state["AGE_LOWER"] == 16) & (temp_state['AGE_UPPER'] == 999)]
temp_state = temp_state[short_cols]
temp_state['daily_first_dose'] = temp_state['AIR_RESIDENCE_FIRST_DOSE_COUNT'].diff(1)
temp_state['daily_first_dose_avg'] = temp_state['daily_first_dose'].rolling(window=7).mean()
last_doses = temp_state['daily_first_dose_avg'].iloc[-1]
temp_state.index = temp_state['DATE_AS_AT']
temp_state = temp_state.reindex(date_index)
# temp_state['second_dose_estimate'] = temp_state.apply(makeSecondDoses, axis=1)

temp_projections = temp_state.copy()
temp_projections['second_dose_pfizer_projection'] = 0
temp_projections['second_dose_az_projection'] = 0

#%%

for index, row in temp_state["2021-07-28":].iterrows():
	
	month = index.strftime('%B')
	print(index)
	# check if we have actual doses to project forward, otherwise use most recent 7-day avg
	
	if pd.isnull(row['daily_first_dose']):
		# null
		doses = last_doses
		assumptions = vax_assump_df[(vax_assump_df['month_ending'] == "August") & (vax_assump_df['state'] == state)]
	else:
		doses = row['daily_first_dose']
		if index < assumptions_cutoff:
			assumptions = vax_assump_df[(vax_assump_df['month_ending'] == month) & (vax_assump_df['state'] == state)]
		else:
			assumptions = vax_assump_df[(vax_assump_df['month_ending'] == "August") & (vax_assump_df['state'] == state)]
	
	# Forward date for pfizer
	print("doses: ", doses)
	days = assumptions['pfizer_interval_upper'].iloc[0]

	pf_projection_fwd_date = index + datetime.timedelta(days=int(days))
# 	print(pf_projection_fwd_date)
	if pf_projection_fwd_date < end_year:
		print("pf doses:", doses * assumptions['pfizer_proportion'].iloc[0])
		temp_projections.at[pf_projection_fwd_date,'second_dose_pfizer_projection'] = doses * assumptions['pfizer_proportion'].iloc[0]

	# Forward date for az
	
	days = assumptions['az_interval_upper'].iloc[0]
# 	print(days)
	pf_projection_fwd_date = index + datetime.timedelta(days=int(days))
# 	print(pf_projection_fwd_date)
	if pf_projection_fwd_date < end_year:
		
		temp_projections.at[pf_projection_fwd_date,'second_dose_az_projection'] = doses * assumptions['az_proportion'].iloc[0]