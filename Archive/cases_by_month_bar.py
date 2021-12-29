#%%
import requests
import pandas as pd
from modules.yachtCharter import yachtCharter
import datetime
chart_key = f"oz-covid-cases-by-month"

day = datetime.datetime.today().weekday()

print("Checking covidlive")

#%%

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

#%%

## Grab Covid Live Data

data = r.json()
df = pd.read_json(r.text)
df = df.sort_values(by='REPORT_DATE', ascending=True)

oz = df.loc[df['CODE'] == 'AUS']
oz = oz[['REPORT_DATE', 'CASE_CNT']]

#%%

zdf = oz.copy()
zdf['REPORT_DATE'] = pd.to_datetime(zdf['REPORT_DATE'])
zdf['Month'] = zdf['REPORT_DATE'].dt.strftime("%b/%y")
# zdf = zdf.resample('W-Mon', on='REPORT_DATE').sum().reset_index().sort_values(by='Date')
zdf['New_cases'] = zdf['CASE_CNT'].diff(1)

grp = zdf.groupby(by=['Month'])['New_cases'].sum().reset_index()

print(grp)
totes = zdf['New_cases'].sum()

grp['Percentage'] = round((grp['New_cases'] /totes)*100, 2)

grp['Sort'] = pd.to_datetime(grp['Month'], format="%b/%y")
grp = grp.sort_values(by='Sort', ascending=True)

grp = grp[['Month', 'Percentage']]

p = grp

print(p)
print(p.columns.tolist())
print("totes",totes)
# %%

def makeTestingLine(df):
	
    template = [
            {
                "title": "Percentage of Australian Covid infections by month reported",
                "subtitle": f"""Showing the percentage of all Australian cases throughout the pandemic, nomatter where infection occured.""",
                "footnote": "",
                "source": "| Sources: Covidlive.com.au",
                "dateFormat": "%b/%y",
                "minY": "0",
                "maxY": "",
                "xAxisDateFormat":"%b %y",
                "tooltip":"Share of all cases: {{groupValue}}%",
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


    yachtCharter(template=template, labels=labels, data=chartData, options=[{"colorScheme":"guardian"}], key=[{"key":"Gap", "colour":"#fc9272"}], chartId=[{"type":"stackedbar"}], chartName=f"{chart_key}")

makeTestingLine(grp)