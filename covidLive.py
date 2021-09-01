#%%
import simplejson as json
import boto3
import os
import requests
import pandas as pd
from modules.syncData import syncData
import datetime

print("Checking covidlive")

#%%

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

#%%

## Grab Covid Live Data

data = r.json()
df = pd.read_json(r.text)
# print(df.columns)

#%%

## Extract Australia vaccination

aus_vacc = df[df['NAME'] == "Australia"].copy()
aus_vacc = aus_vacc[aus_vacc['REPORT_DATE'] >= '2021-02-14']

aus_vacc_final = aus_vacc[['REPORT_DATE', 'LAST_UPDATED_DATE', 'ACTIVE_CNT',
'PREV_ACTIVE_CNT','CODE', 'NAME', 'RECOV_CNT','VACC_DIST_CNT', 'PREV_VACC_DIST_CNT', 'VACC_DOSE_CNT', 'PREV_VACC_DOSE_CNT', 'VACC_PEOPLE_CNT', 'PREV_VACC_PEOPLE_CNT']]

aus_vacc_finalJson = aus_vacc_final.to_json(orient='records')

#%%

## Make separate vaccination json for state-based chart

states_vacc = df[['REPORT_DATE', 'LAST_UPDATED_DATE', 'CODE', 'VACC_DOSE_CNT', 'PREV_VACC_DOSE_CNT',
'PREV_VACC_AGED_CARE_CNT', 'PREV_VACC_GP_CNT']].copy()

states_vacc = states_vacc[states_vacc['REPORT_DATE'] >= '2021-02-24']
states_vacc_finalJson = states_vacc.to_json(orient='records')

#%%

## Make final json for Australia case counts

aus_cases = df[['REPORT_DATE', 'LAST_UPDATED_DATE', 'CODE', 'NAME', 'CASE_CNT',
       'TEST_CNT', 'DEATH_CNT', 'RECOV_CNT', 'MED_ICU_CNT', 'MED_VENT_CNT',
       'MED_HOSP_CNT', 'SRC_OVERSEAS_CNT', 'SRC_INTERSTATE_CNT',
       'SRC_CONTACT_CNT', 'SRC_UNKNOWN_CNT', 'SRC_INVES_CNT', 'PREV_CASE_CNT',
       'PREV_TEST_CNT', 'PREV_DEATH_CNT', 'PREV_RECOV_CNT', 'PREV_MED_ICU_CNT',
       'PREV_MED_VENT_CNT', 'PREV_MED_HOSP_CNT', 'PREV_SRC_OVERSEAS_CNT',
       'PREV_SRC_INTERSTATE_CNT', 'PREV_SRC_CONTACT_CNT',
       'PREV_SRC_UNKNOWN_CNT', 'PREV_SRC_INVES_CNT', 'PROB_CASE_CNT',
       'PREV_PROB_CASE_CNT', 'ACTIVE_CNT', 'PREV_ACTIVE_CNT', 'NEW_CASE_CNT',
       'PREV_NEW_CASE_CNT']]

aus_cases_finalJson = aus_cases.to_json(orient='records')

#%%

## Sync

syncData(aus_vacc_finalJson, "2021/02/coronavirus-widget-data", "aus-vaccines.json")
syncData(states_vacc_finalJson, "2021/02/coronavirus-widget-data", "state-vaccine-rollout.json")
syncData(aus_cases_finalJson, "2021/02/coronavirus-widget-data", "oz-covid-cases.json")

#%%

import thrasher_endpoint
import vac_gap_goals_five
import state_by_state.vac_state_projection_table
import vac_state_charter
import vaccinesReindex
import daily_covid_cases
import vac_global_per_hund
import vac_global_bar
import vaccineDosesState
import hospitalised_percent_line


day = datetime.datetime.today().weekday()
#%%
if day > 4:
       import vaccine_availability.weekly_state_utilisation
       import vaccine_availability.weekly_distribution

# import vaccineDosesState

#%%