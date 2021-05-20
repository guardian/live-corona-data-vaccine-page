import requests
import simplejson as json
import pandas as pd
from modules.syncData import syncData

print("Checking covidlive")

#%%

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

#%%

data = r.json()

df = pd.read_json(r.text)

print(list(df.columns.values))

cols = ['REPORT_DATE', 'LAST_UPDATED_DATE', 'ACTIVE_CNT', 'PREV_ACTIVE_CNT','CODE', 'NAME', 'RECOV_CNT','VACC_DIST_CNT', 'PREV_VACC_DIST_CNT', 'VACC_DOSE_CNT', 'PREV_VACC_DOSE_CNT', 'VACC_PEOPLE_CNT', 'PREV_VACC_PEOPLE_CNT']

df_aus = df[df['NAME'] == "Australia"]
df_aus = df_aus[df_aus['REPORT_DATE'] >= '2021-02-14']

final = df_aus[cols]
finalJson = final.to_json(orient='records')

## Make separate json for state-based chart

states = df[['REPORT_DATE', 'LAST_UPDATED_DATE', 'CODE', 'VACC_DOSE_CNT', 'PREV_VACC_DOSE_CNT', 
'PREV_VACC_AGED_CARE_CNT', 'PREV_VACC_GP_CNT']]

states = states[states['REPORT_DATE'] >= '2021-02-24']
states_final = states.to_json(orient='records')

#%%

syncData(finalJson, "2021/02/coronavirus-widget-data", "aus-vaccines.json")
syncData(states_final, "2021/02/coronavirus-widget-data", "state-vaccine-rollout.json")

# import vaccinesPerHundred
import vaccinesReindex
# import vaccinegap
import vac_state_charter
import vac_gap_goals_trend
import vac_gap_goals_three
