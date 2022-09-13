#%%
import simplejson as json
import boto3
import os
import requests
import pandas as pd
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


zdf = df[['REPORT_DATE',  'CODE','VACC_FIRST_DOSE_CNT', 'VACC_PEOPLE_CNT', 'VACC_BOOSTER_CNT',  'VACC_WINTER_CNT']].copy()

zdf['Population'] = zdf['CODE'].map(pops)

latest_date = zdf['REPORT_DATE'].max()
init_date = datetime.datetime.strptime(latest_date, "%Y-%m-%d")
display_date = datetime.datetime.strftime(init_date, "%-d %B %Y")

zdf.sort_values(by=['REPORT_DATE'], ascending=True, inplace=True)

# zdf = zdf.loc[zdf['REPORT_DATE'] == '2022-07-14']

cols = zdf.columns.tolist()


listo = []

for juri in zdf['CODE'].unique().tolist():

  inter = zdf.loc[zdf['CODE'] == juri].copy()
  inter[cols[2:]] = inter[cols[2:]].interpolate(method='linear', limit_direction='forward')
  # inter = inter.loc[inter[cols[2]] == inter[cols[2]].max()]
  inter = inter.loc[inter[cols[0]] == inter[cols[0]].max()].copy()

  for col in inter.columns.tolist():
    if col not in ['REPORT_DATE',  'CODE', 'Population']:
      inter[col] = round((inter[col] / inter['Population'])*100,2)

  listo.append(inter)

cat = pd.concat(listo)

cat.sort_values(by=['Population'], ascending=False, inplace=True)

cat = cat[['CODE', 'VACC_FIRST_DOSE_CNT', 'VACC_PEOPLE_CNT', 'VACC_BOOSTER_CNT',  'VACC_WINTER_CNT']]

cat.columns = ['Jurisdiction', 'One dose', 'Two doses', 'Three doses', 'Four doses']



# p = cat 

# print(p)
# print(p.columns.tolist())
# %%

final = cat.to_dict(orient='records')

template = [
	{
	"title": "Vaccination levels by dose and jurisdiction",
	"subtitle": f"Showing the percentage of the total estimated resident population (aged 0+) for each jurisidiction. Last updated {display_date}.",
	"footnote": "",
	"source": "CovidLive.com.au, Australian Bureau of Statistics, Guardian Australia",
	"margin-left": "20",
	"margin-top": "30",
	"margin-bottom": "20",
	"margin-right": "10"
	}
]

from yachtcharter import yachtCharter
# testo = "-testo"
testo = ''
chart_key = f"oz-datablogs-new-covid-cases-vax-page-jurisidction-table{testo}"
yachtCharter(template=template, 
            options=[{"colorScheme":"guardian","format": "truncate",
            "enableSearch": "FALSE","enableSort": "TRUE"}],
			data=final,
			chartId=[{"type":"table"}],
            key = [{'key': f'{x}','values':f'{cat[x].min()},{cat[x].max()}', 'colours': '#ffffff, #94b1ca', 'scale': 'linear'} if x != "Issues" else "" for x in cat.columns.tolist()[1:]],
			chartName=f"{chart_key}")
