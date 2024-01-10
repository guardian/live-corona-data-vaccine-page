#%%
import simplejson as json
import boto3
import os
import requests
import pandas as pd
import datetime

day = datetime.datetime.today().weekday()

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



colours = ["#4e79a7","#f28e2c","#e15759","#76b7b2","#59a14f","#edc949","#af7aa1","#ff9da7","#9c755f","#bab0ab"]

new_colours = []
for i in range(0, len(pops.keys())):
  new_colours.append({"key": list(pops.keys())[i], 'colour': colours[i]})
  # new_colours[list(pops.keys())[i]] = colours[i]


# print(new_colours)

#%%

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)




#%%

data = r.json()
df = pd.read_json(r.text)

#%%


df.sort_values(by=['REPORT_DATE'], ascending=True, inplace=True)

df = df.loc[df['REPORT_DATE'] >= '2021-06-01']

latest_date = df['REPORT_DATE'].max()
init_date = datetime.datetime.strptime(latest_date, "%Y-%m-%d")
display_date = datetime.datetime.strftime(init_date, "%-d %B %Y")

#%%

### Switch to weekly data
we = df.copy()

we['REPORT_DATE'] = pd.to_datetime(we['REPORT_DATE'])

we['WeekDay'] = we['REPORT_DATE'].dt.weekday

we = we.loc[we['WeekDay'] == 4]

# we.drop(columns={'WeekDay'}, inplace=True)


#%%

init = we.copy()

zdf = init[['REPORT_DATE',  'CODE','MED_HOSP_CNT',]].copy()


zdf['Population'] = zdf['CODE'].map(pops)

zdf = zdf[['REPORT_DATE',  'CODE','MED_HOSP_CNT', ]]

zdf['Population'] = zdf['CODE'].map(pops)

zdf['MED_HOSP_CNT'] = round((zdf['MED_HOSP_CNT']/zdf['Population'])*100000,2)

piv = zdf.pivot(index='REPORT_DATE', columns='CODE', values='MED_HOSP_CNT').reset_index()

# for col in piv.columns.tolist()[1:]:
#   piv[col] = piv[col].interpolate(method='linear', limit_direction='forward')
#   piv[col] = piv[col].rolling(window=7).mean()

# piv.fillna('', inplace=True)

piv['REPORT_DATE'] = piv['REPORT_DATE'].dt.strftime("%Y-%m-%d")


# p = piv 

# print(p.tail(50))
# print(p.columns.tolist())
# %%

# %%

# %%

piv.fillna('', inplace=True)
final = piv.to_dict(orient='records')
# print(final) 

template = [
	{
	"title": "Weekly covid hospitalisations per 100k population, by jurisdiction",
	# "subtitle": f"Showing the 7-day rolling average of Covid hospitalisations per 100k estimated resident population. Using the total population (aged 0+). Last updated {display_date}.",
  "subtitle": f"""Showing the total number of Covid patients admitted to hospital per 100k estimated resident population, on each Friday, by jurisdiction. Some states have at times mandated that all Covid positive patients be admitted to hospital. Last updated {display_date}.""",
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
# testo = '-since-july-2022'
testo = ''
chart_key = f"oz-datablogs-weekly-covid-hospitalisations-per-100k{testo}"
yachtCharter(template=template, 
            data=final,
            key = new_colours,
            chartId=[{"type":"linechart"}],
            options=[{"colorScheme":"guardian", "lineLabelling":"FALSE"}],
            chartName=f"{chart_key}{testo}")