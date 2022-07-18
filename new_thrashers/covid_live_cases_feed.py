#%%
import requests
import pandas as pd
import datetime
import pytz
import json 

today = datetime.datetime.now().astimezone(pytz.timezone("Australia/Brisbane"))
week_ago = today - datetime.timedelta(days=7)
thirty_ago = today - datetime.timedelta(days=30)

today = today.strftime('%Y-%m-%d')
week_ago = week_ago.strftime('%Y-%m-%d')
thirty_ago = thirty_ago.strftime('%Y-%m-%d')

pops = {"AUS": 25766605, 
'NSW': 8095.4*1000, 
'VIC': 6559.9*1000, 
'QLD': 5265.0*1000,
'SA': 1806.6 * 1000,
'WA': 2762.2 * 1000,
'TAS': 569.8 * 1000,
'NT': 249.3 * 1000,
'ACT': 453.3 * 1000
}

#%%

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

#%%

## Grab Covid Live Data

data = r.json()
df = pd.read_json(r.text)
# print(df.columns)

# 'REPORT_DATE', 'LAST_UPDATED_DATE', 'CODE', 'NAME', 
# 'CASE_CNT', 'TEST_CNT', 'DEATH_CNT', 'RECOV_CNT', 
# 'MED_ICU_CNT', 'MED_VENT_CNT', 'MED_HOSP_CNT', 
# 'SRC_OVERSEAS_CNT', 'SRC_INTERSTATE_CNT', 'SRC_CONTACT_CNT', 
# 'SRC_UNKNOWN_CNT', 'SRC_INVES_CNT', 'PREV_CASE_CNT', 
# 'PREV_TEST_CNT', 'PREV_DEATH_CNT', 'PREV_RECOV_CNT', 
# 'PREV_MED_ICU_CNT', 'PREV_MED_VENT_CNT', 'PREV_MED_HOSP_CNT', 
# 'PREV_SRC_OVERSEAS_CNT', 'PREV_SRC_INTERSTATE_CNT', 
# 'PREV_SRC_CONTACT_CNT', 'PREV_SRC_UNKNOWN_CNT', 'PREV_SRC_INVES_CNT', 
# 'PROB_CASE_CNT', 'PREV_PROB_CASE_CNT', 'ACTIVE_CNT', 
# 'PREV_ACTIVE_CNT', 'NEW_CASE_CNT', 'PREV_NEW_CASE_CNT', 
# 'VACC_DIST_CNT', 'PREV_VACC_DIST_CNT', 'VACC_DOSE_CNT', 
# 'PREV_VACC_DOSE_CNT', 'VACC_PEOPLE_CNT', 'PREV_VACC_PEOPLE_CNT', 
# 'VACC_AGED_CARE_CNT', 'PREV_VACC_AGED_CARE_CNT', 'VACC_GP_CNT', 
# 'PREV_VACC_GP_CNT', 'VACC_FIRST_DOSE_CNT', 'PREV_VACC_FIRST_DOSE_CNT', 
# 'VACC_FIRST_DOSE_CNT_12_15', 'PREV_VACC_FIRST_DOSE_CNT_12_15', 
# 'VACC_PEOPLE_CNT_12_15', 'PREV_VACC_PEOPLE_CNT_12_15', 'VACC_BOOSTER_CNT', 
# 'PREV_VACC_BOOSTER_CNT', 'VACC_FIRST_DOSE_CNT_5_11', 
# 'PREV_VACC_FIRST_DOSE_CNT_5_11', 'VACC_PEOPLE_CNT_5_11', 
# 'PREV_VACC_PEOPLE_CNT_5_11', 'NEW_PROB_CASE_CNT', 
# 'PREV_NEW_PROB_CASE_CNT', 'VACC_WINTER_CNT', 'PREV_VACC_WINTER_CNT'

#%%

listo = []

zdf = df[['REPORT_DATE', 'CODE', 'NAME',
'ACTIVE_CNT', 'CASE_CNT',
'DEATH_CNT','TEST_CNT', 
'MED_HOSP_CNT', 
'MED_ICU_CNT', 'MED_VENT_CNT',
'NEW_CASE_CNT']].copy()
zdf.sort_values(by=['REPORT_DATE'], ascending=True, inplace=True)

# zdf = zdf[:10]

zdf['REPORT_DATE'] = pd.to_datetime(zdf['REPORT_DATE'])
zdf['REPORT_DATE'] = zdf['REPORT_DATE'].dt.strftime("%Y-%m-%d")

for col in zdf.columns.tolist():
  if col not in ['REPORT_DATE', 'CODE', 'NAME']:
    zdf[col] = zdf[col].astype(float)

# for juri in zdf['CODE'].unique().tolist():
#   inter = zdf.loc[zdf['CODE'] == juri].copy()

#   listo.extend(inter.to_dict(orient='records'))



zdf.fillna('', inplace=True)

jsony = json.dumps(zdf.to_dict(orient='records'))

from modules.syncData import syncData
syncData(jsony,'2022/07/oz-covid-health-data', f"cases.json")

# print(listo)
# p = zdf

# print(p)
# print(p.columns.tolist())
# %%
