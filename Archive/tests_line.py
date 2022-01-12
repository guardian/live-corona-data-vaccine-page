#%%
import requests
import pandas as pd
from modules.yachtCharter import yachtCharter
import datetime
chart_key = f"oz-covid-small-tests-line"

testo = ''

day = datetime.datetime.today().weekday()

#%%

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

#%%

## Grab Covid Live Data

data = r.json()
df = pd.read_json(r.text)
df = df.sort_values(by='REPORT_DATE', ascending=True)

oz = df.loc[df['CODE'] == 'AUS'].copy()

oz['New_tests'] = oz['TEST_CNT'].diff(1)

oz['Tests, 7 day avg'] = round(oz['New_tests'].rolling(window=7).mean(),2)

oz = oz[['REPORT_DATE','Tests, 7 day avg']]



p = oz

print(p)
print(p.columns.tolist())
# %%

oz.fillna('', inplace=True)

final = oz.to_dict(orient='records')

template = [
    {
    "title": f"Testing for Covid-19 in Australia",
    "subtitle": f"Showing the seven day rolling average of daily tests",
    "footnote": "",
    "dateFormat": "%Y-%m-%d",
    "source": "CovidLive.com.au",
    "margin-left": "35",
    "margin-top": "30",
    "margin-bottom": "20",
    "margin-right": "10",
    "tooltip":"<strong>{{#formatDate}}{{REPORT_DATE}}{{/formatDate}}</strong><br/> 7 day avg: {{Tests, 7 day avg}}<br/>"
    }
]

yachtCharter(template=template, 
            data=final,
            chartId=[{"type":"linechart"}],
            options=[{"colorScheme":"guardian", "lineLabelling":"TRUE"}],
            chartName=f"{chart_key}{testo}")