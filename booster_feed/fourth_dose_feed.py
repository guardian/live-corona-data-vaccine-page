#%%
import simplejson as json
import boto3
import os
import requests
import pandas as pd
# from modules.syncData import syncData
from modules.numberFormat import numberFormat
from yachtcharter import yachtCharter
import datetime

day = datetime.datetime.today().weekday()

print("Checking covidlive")

#%%

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

#%%

pop = 25766605


## Grab Covid Live Data

data = r.json()
df = pd.read_json(r.text)
# 'REPORT_DATE', 'LAST_UPDATED_DATE', 'CODE', 'NAME', 
# 'CASE_CNT', 'TEST_CNT', 'DEATH_CNT', 'RECOV_CNT', 
# 'MED_ICU_CNT', 'MED_VENT_CNT', 'MED_HOSP_CNT', 
# 'SRC_OVERSEAS_CNT', 'SRC_INTERSTATE_CNT', 
# 'SRC_CONTACT_CNT', 'SRC_UNKNOWN_CNT', 'SRC_INVES_CNT', 
# 'PREV_CASE_CNT', 'PREV_TEST_CNT', 'PREV_DEATH_CNT', 
# 'PREV_RECOV_CNT', 'PREV_MED_ICU_CNT', 'PREV_MED_VENT_CNT', 
# 'PREV_MED_HOSP_CNT', 'PREV_SRC_OVERSEAS_CNT', 
# 'PREV_SRC_INTERSTATE_CNT', 'PREV_SRC_CONTACT_CNT', 
# 'PREV_SRC_UNKNOWN_CNT', 'PREV_SRC_INVES_CNT', 
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
# 'PREV_VACC_PEOPLE_CNT_5_11', 'NEW_PROB_CASE_CNT', 'PREV_NEW_PROB_CASE_CNT', 
# 'VACC_WINTER_CNT', 'PREV_VACC_WINTER_CNT'



oz = df.loc[df['CODE'] == 'AUS'].copy()
oz = oz.loc[oz['REPORT_DATE'] > "2021-03-01"]

oz = oz[['REPORT_DATE', 'VACC_PEOPLE_CNT','VACC_BOOSTER_CNT','VACC_WINTER_CNT']]

oz.sort_values(by=['REPORT_DATE'], ascending=True, inplace=True)

latest_date = oz['REPORT_DATE'].max()
init_date = datetime.datetime.strptime(latest_date, "%Y-%m-%d")
display_date = datetime.datetime.strftime(init_date, "%-d %B %Y")

for col in oz.columns.tolist()[1:]:
	oz[col] = round((oz[col] / pop)*100,2)


max_second = oz['VACC_PEOPLE_CNT'].max()
max_boost = oz['VACC_BOOSTER_CNT'].max()
max_fourth = oz['VACC_WINTER_CNT'].max()

oz['VACC_WINTER_CNT'] = oz['VACC_WINTER_CNT'].interpolate(method='linear', limit_direction='forward')

oz.loc[oz['VACC_PEOPLE_CNT'] == 0, 'VACC_PEOPLE_CNT'] = ''
oz.loc[oz['VACC_BOOSTER_CNT'] == 0, 'VACC_BOOSTER_CNT'] = ''

oz.rename(columns={'REPORT_DATE': 'Date',
'VACC_PEOPLE_CNT':f"{numberFormat(max_second)}% Second doses",
'VACC_BOOSTER_CNT':f"{numberFormat(max_boost)}% Boosters",
'VACC_WINTER_CNT':f"{numberFormat(max_fourth)}% Fourth doses"}, inplace=True)

oz.fillna('', inplace=True)

final = oz.to_dict(orient='records')

template = [
	{
	"title": "Tracking the rollout of Covid vaccines in Australia",
	# "subtitle": f"""Showing the cumulative count of second and booster doses. The <b style="color:rgb(245, 189, 44)">trend</b> in booster doses is based on the current interval between when the equivalent number of second and booster doses were administered. Last updated {display_date}.""",
	"subtitle": f"""Showing the percentage of the total Australian population that have received second, booster and fourth doses of a Covid vaccine. Last updated {display_date}.""",

	"footnote": "Footnote",
	"source": "CovidLive.com.au, Ken Tsang, Guardian Australia analysis",
	"margin-left": "35",
	"margin-top": "30",
	"margin-bottom": "20",
	"margin-right": "10"
	}
]

chart_key = f"oz-live-corona-page-second-boosters-fourth-doses-tracker"
yachtCharter(template=template,
			data=final,
			chartId=[{"type":"linechart"}],
            options=[{"colorScheme":"guardian", "lineLabelling":"TRUE"}],
			chartName=f"{chart_key}")



p = oz 

print(p)
print(p.columns.tolist())
# %%
