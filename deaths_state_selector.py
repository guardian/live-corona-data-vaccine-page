#%%
import simplejson as json
import boto3
import os
import requests
import pandas as pd
pd.set_option("display.max_rows", 100)

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


zdf = df[['REPORT_DATE',  'CODE','DEATH_CNT']]

latest_date = zdf['REPORT_DATE'].max()
init_date = datetime.datetime.strptime(latest_date, "%Y-%m-%d")
display_date = datetime.datetime.strftime(init_date, "%-d %B %Y")

# zdf.sort_values(by=['CODE'], key=lambda x: x.map(pops), inplace=True)

piv = zdf.pivot(index='REPORT_DATE', columns='CODE', values='DEATH_CNT').reset_index()



piv = piv[['REPORT_DATE', 'AUS', 'ACT', 'NSW', 'NT', 'QLD', 'SA', 'TAS', 'VIC', 'WA']]

for col in piv.columns.tolist()[1:]:
  piv[col] = pd.to_numeric( piv[col])
  piv[col] = piv[col].diff()
  piv.loc[piv[col] <0, col] = 0

  print(col)

  ### Need to adjust the deaths for NSW and Oz for the backdated deaths on April 1st 2022:
  if col in ['AUS', 'NSW']:
    actual_val = piv.loc[piv['REPORT_DATE'] == '2022-04-01'][col].values[0]

    difference = actual_val - 300

    piv.loc[piv['REPORT_DATE'] == '2022-04-01', col] = difference

    piv.loc[((piv['REPORT_DATE'] >= '2021-12-22') & (piv['REPORT_DATE'] <= '2022-04-01')), col] += 3


#%%

piv.fillna('', inplace=True)

piv = piv[1:]

p = piv 

print(p.head(100))
print(p.columns.tolist())


keyo = []

for juri in list(pops.keys()):
  keyo.append({'data': juri, 'display': juri})


# print(keyo)


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
chart_key = f"oz-datablogs-covid-page-juri-deaths-selector{testo}"
# yachtCharter(template=template, 
#             data=final,
#             key = [{"key":"Net internal migration", "colour":'#7d0068'}],
#             dropdown= keyo,
#             chartId=[{"type":"linechart"}],
#             options=[{"colorScheme":"guardian", "lineLabelling":"TRUE"}],
#             chartName=f"{chart_key}{testo}")



from yachtcharter import yachtCharter
def makeTestingLine(df):
	
    template = [
            {
                "title": "Covid deaths by jurisidction",
                "subtitle": f"""Showing the total number of deaths by day* and jurisdiction. Last updated {display_date}.""",
                "footnote": "",
                "source": "Covidlive.com.au",
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
