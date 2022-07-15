#%%
import simplejson as json
import boto3
import os
import requests
import pandas as pd
# from modules.syncData import syncData
# from modules.numberFormat import numberFormat
# from yachtcharter import yachtCharter
import datetime

day = datetime.datetime.today().weekday()

print("Checking covidlive")


#%%

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

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

data = r.json()
df = pd.read_json(r.text)



#%%


zdf = df[['REPORT_DATE',  'CODE','MED_HOSP_CNT', ]]

piv = zdf.pivot(index='REPORT_DATE', columns='CODE', values='MED_HOSP_CNT').reset_index()

piv.fillna('', inplace=True)

with open('Archive/state_hospitalisations.csv', 'w') as f:
  piv.to_csv(f, index=False, header=True)






p = piv 

print(p)
print(p.columns.tolist())
# %%
