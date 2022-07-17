#%%
import simplejson as json
import boto3
import os
import requests
import pandas as pd
import numpy as np 

pd.set_option("display.max_rows", 100)
# from modules.syncData import syncData
# from modules.numberFormat import numberFormat
from yachtcharter import yachtCharter
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

latest_date = zdf['REPORT_DATE'].max()
init_date = datetime.datetime.strptime(latest_date, "%Y-%m-%d")
display_date = datetime.datetime.strftime(init_date, "%-d %B %Y")

# zdf.sort_values(by=['CODE'], key=lambda x: x.map(pops), inplace=True)

piv = zdf.pivot(index='REPORT_DATE', columns='CODE', values='MED_HOSP_CNT').reset_index()

### Fill in the nan value for ACT
piv.loc[piv['REPORT_DATE'].isin(['2022-04-15', '2022-04-17']), 'ACT'] = np.nan

for col in ['AUS', 'ACT', 'NSW', 'NT', 'QLD', 'SA', 'TAS', 'VIC', 'WA']:
  piv[col] = piv[col].interpolate(method='linear', limit_direction='forward')

piv.fillna('', inplace=True)

with open('Archive/state_hospitalisations.csv', 'w') as f:
  piv.to_csv(f, index=False, header=True)


# print(piv.columns.tolist())

piv = piv[['REPORT_DATE', 'AUS', 'ACT', 'NSW', 'NT', 'QLD', 'SA', 'TAS', 'VIC', 'WA']]

keyo = []

for juri in list(pops.keys()):
  keyo.append({'data': juri, 'display': juri})





print(keyo)

p = piv 

print(p.tail(100))
print(p.columns.tolist())


# bye = piv 

# final = bye.to_dict(orient='records') 
# template = [
#     {
#     "title": f"Covid hospitalisations by jurisidction",
#     "subtitle": f"Showing the total number of Covid patients to hospital by jurisdiction. Some states previously mandated all Covid positive patients be admitted to hospital. ",
#     "footnote": "",
#     "dateFormat": "%Y-%m-%d",
#     "source": "CovidLive.com.au",
#     "margin-left": "35",
#     "margin-top": "30",
#     "margin-bottom": "20",
#     "margin-right": "10",
#     "xColumn" : "REPORT_DATE",

# #     "tooltip":"<strong>{{#formatDate}}{{Date}}{{/formatDate}}</strong><br/> In ICU: {{ICU}}<br/>"
#     }
# ]

# from yachtcharter import yachtCharter
# testo = "-testo"
testo = ''
chart_key = f"oz-datablogs-covid-page-juri-hospitalisation-selector{testo}"
# yachtCharter(template=template, 
#             data=final,
#             key = [{"key":"Net internal migration", "colour":'#7d0068'}],
#             dropdown= keyo,
#             chartId=[{"type":"linechart"}],
#             options=[{"colorScheme":"guardian", "lineLabelling":"TRUE"}],
#             chartName=f"{chart_key}{testo}")




def makeTestingLine(df):
	
    template = [
            {
                "title": "Covid hospitalisations by jurisidction",
                "subtitle": f"""Showing the total number of Covid patients to hospital by jurisdiction. Gaps in the data have been interpolated. Some states have at times mandated that all Covid positive patients be admitted to hospital. Last updated {display_date}.""",
                "footnote": "",
                "source": "Federal and state health departments, CovidLive.com.au, Guardian Australia",
                "dateFormat": "%Y-%m-%d",
                "yScaleType":"",
                "minY": "0",
                "maxY": "",
                "xColumn" : "REPORT_DATE",
                "margin-left": "50",
                "margin-top": "30",
                "margin-bottom": "20",
                "margin-right": "10"
            }
        ]
    key = []
    periods = []
    # labels = []
    df.fillna("", inplace=True)
    chartData = df.to_dict('records')
    labels = []

    yachtCharter(template=template, labels=labels,  dropdown= keyo, data=chartData, chartId=[{"type":"linechart"}], 
    options=[{"colorScheme":"guardian", "lineLabelling":"FALSE"}], chartName=chart_key)

makeTestingLine(piv)

# p = piv 

# print(p)
# print(p.columns.tolist())
# # %%
