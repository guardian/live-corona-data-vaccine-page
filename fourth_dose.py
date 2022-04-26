#%%
import simplejson as json
import boto3
import os
import requests
import pandas as pd
# from modules.syncData import syncData
import datetime

day = datetime.datetime.today().weekday()

print("Checking covidlive")

#%%

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

#%%

## Grab Covid Live Data

data = r.json()
df = pd.read_json(r.text)
# 'REPORT_DATE', 'LAST_UPDATED_DATE', 'CODE', 'NAME',
# 'CASE_CNT', 'TEST_CNT', 'DEATH_CNT', 'RECOV_CNT',
# 'MED_ICU_CNT', 'MED_VENT_CNT', 'MED_HOSP_CNT', 
# 'SRC_OVERSEAS_CNT', 'SRC_INTERSTATE_CNT', 'SRC_CONTACT_CNT',
# 'SRC_UNKNOWN_CNT', 'SRC_INVES_CNT', 'PREV_CASE_CNT', 
# 'PREV_TEST_CNT', 'PREV_DEATH_CNT', 'PREV_RECOV_CNT', 
# 'PREV_MED_ICU_CNT', 'PREV_MED_VENT_CNT', 'PREV_MED_HOSP_CNT', 
# 'PREV_SRC_OVERSEAS_CNT', 'PREV_SRC_INTERSTATE_CNT', 
# 'PREV_SRC_CONTACT_CNT', 'PREV_SRC_UNKNOWN_CNT', 
# 'PREV_SRC_INVES_CNT', 'PROB_CASE_CNT', 'PREV_PROB_CASE_CNT', 
# 'ACTIVE_CNT', 'PREV_ACTIVE_CNT', 'NEW_CASE_CNT', 
# 'PREV_NEW_CASE_CNT', 'VACC_DIST_CNT', 'PREV_VACC_DIST_CNT', 
# 'VACC_DOSE_CNT', 'PREV_VACC_DOSE_CNT', 'VACC_PEOPLE_CNT', 
# 'PREV_VACC_PEOPLE_CNT', 'VACC_AGED_CARE_CNT', 
# 'PREV_VACC_AGED_CARE_CNT', 'VACC_GP_CNT', 'PREV_VACC_GP_CNT', 
# 'VACC_FIRST_DOSE_CNT', 'PREV_VACC_FIRST_DOSE_CNT', 
# 'VACC_FIRST_DOSE_CNT_12_15', 'PREV_VACC_FIRST_DOSE_CNT_12_15', 
# 'VACC_PEOPLE_CNT_12_15', 'PREV_VACC_PEOPLE_CNT_12_15', 
# 'VACC_BOOSTER_CNT', 'PREV_VACC_BOOSTER_CNT', 
# 'VACC_FIRST_DOSE_CNT_5_11', 'PREV_VACC_FIRST_DOSE_CNT_5_11', 
# 'VACC_PEOPLE_CNT_5_11', 'PREV_VACC_PEOPLE_CNT_5_11',
# 'NEW_PROB_CASE_CNT', 'PREV_NEW_PROB_CASE_CNT'

#%%
### Can I work out fourth doses by subtracting all the other ones?

zdf = df.loc[df['CODE'] == 'AUS'].copy()
# zdf = zdf.loc[zdf['REPORT_DATE'] == zdf['REPORT_DATE'].max()]
zdf = zdf.loc[zdf['REPORT_DATE'] == '2022-04-25']

oz = zdf[['VACC_DOSE_CNT',  'VACC_PEOPLE_CNT', 
'VACC_FIRST_DOSE_CNT', 
'VACC_BOOSTER_CNT']].copy()

oz['Res'] = oz['VACC_DOSE_CNT'] - oz['VACC_PEOPLE_CNT'] - oz['VACC_FIRST_DOSE_CNT'] - oz['VACC_BOOSTER_CNT']

## Above maths gives me 368842 fourth doses on the 25th of April
## Covidlive gives me 345,829 as of 25th April

p = oz

print(p)
print(p.columns.tolist())
# %%
