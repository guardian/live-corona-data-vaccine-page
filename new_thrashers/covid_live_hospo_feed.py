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

#%%


zdf = df[['REPORT_DATE','CODE','MED_HOSP_CNT','VACC_PEOPLE_CNT', 'VACC_BOOSTER_CNT','VACC_WINTER_CNT','DEATH_CNT']].copy()
zdf.sort_values(by=['REPORT_DATE'], ascending=True, inplace=True)


dicto = {}

for juri in pops.keys():
  inter = zdf.loc[zdf['CODE'] == juri].copy()

  for col in zdf.columns.tolist():
    if col not in ['REPORT_DATE']:
      inter[col] = inter[col].interpolate(method='linear', limit_direction='forward')

  popper = pops[juri]

  today_med = inter.loc[inter['REPORT_DATE'] == today]['MED_HOSP_CNT'].values[0]
  week_ago_med = inter.loc[inter['REPORT_DATE'] == week_ago]['MED_HOSP_CNT'].values[0]

  # inter['DEATH_CNT'] = inter['DEATH_CNT'].diff(30)
  today_deaths = inter.loc[inter['REPORT_DATE'] == today]['DEATH_CNT'].values[0]
  deaths_30_ago = inter.loc[inter['REPORT_DATE'] == thirty_ago]['DEATH_CNT'].values[0]

  two_doses = inter.loc[inter['REPORT_DATE'] == today]['VACC_PEOPLE_CNT'].values[0]
  three_doses = inter.loc[inter['REPORT_DATE'] == today]['VACC_BOOSTER_CNT'].values[0]
  four_doses = inter.loc[inter['REPORT_DATE'] == today]['VACC_WINTER_CNT'].values[0]

  deaths_last_thirty = today_deaths - deaths_30_ago

  if today_med > week_ago_med:
    status = 'Increasing'
  else:
    status = 'Decreasing'

  dicto[f"{juri}_hospitalised"] = today_med
  dicto[f"{juri}_PREV_WEEK_hospitalised"] = week_ago_med
  dicto[f"{juri}_status"] = status

  if juri == 'AUS':
    dicto[f"{juri}_deaths_last_thirty"] = float(deaths_last_thirty)
    dicto[f"{juri}_two_doses_percent"] = round((two_doses/popper)*100,2)
    dicto[f"{juri}_three_doses_percent"] = round((three_doses/popper)*100,2)
    dicto[f"{juri}_four_doses_percent"] = round((four_doses/popper)*100,2)

  # print(juri)
  # print(inter.tail(10))

  # print(today_med)
  # print(week_ago_med)

print(dicto)

# p = zdf 

# print(p)
# print(p.columns.tolist())
# %%

jsony = json.dumps(dicto)

from modules.syncData import syncData
syncData(jsony, "2022/07/coronavirus-thrasher-data", "thrasher-health-scrape-data-new-NEW.json")
