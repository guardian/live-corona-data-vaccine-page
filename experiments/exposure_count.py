#%%
from modules.yachtCharter import yachtCharter
import pandas as pd 

import datetime
import pytz

today = datetime.datetime.now(pytz.timezone("Australia/Sydney"))
today = datetime.datetime.strftime(today, '%d/%m/%Y')

nsw = 'https://raw.githubusercontent.com/joshnicholas/exposure_site_scrapers/main/data/nsw_exposure_sites.csv'
vic = 'https://raw.githubusercontent.com/joshnicholas/exposure_site_scrapers/main/data/vic_exposure_sites.csv'
qld = 'https://raw.githubusercontent.com/joshnicholas/exposure_site_scrapers/main/data/qld_exposure_sites.csv'
wa = 'https://raw.githubusercontent.com/joshnicholas/exposure_site_scrapers/main/data/wa_exposure_sites.csv'

#%%

nsw = pd.read_csv(nsw)
vic = pd.read_csv(vic)
qld = pd.read_csv(qld)
wa = pd.read_csv(wa)




#%%

## GRAB QUEENSLAND

nsw = nsw[['Date', 'Suburb']]
vic = vic[['Exposure day', 'Suburb']]
qld = qld[['Date', 'Suburb']]
wa = wa[['Date', 'Location']]

vic.columns = ['Date', 'Suburb']

vic['Date'] = pd.to_datetime(vic['Date'], format="%d/%m/%Y")
qld['Date'] = pd.to_datetime(qld['Date'], format="%A %d %B %Y")
wa['Date'] = pd.to_datetime(wa['Date'], format="%d/%m/%Y")

nsw.loc[nsw['Date'] == 'Friday 25 June 2021 to Saturday 26 June 2021', 'Date'] = "Friday 25 June 2021"
nsw.loc[nsw['Date'] == 'Tuesday 22 June 2021 - Wednesday 23 June 2021', 'Date'] = "Tuesday 22 June 2021"

nsw['Date'] = nsw['Date'].apply(lambda x: x + " 2021" if "2021" not in x else x)
nsw['Date'] = pd.to_datetime(nsw['Date'], format="%A %d %B %Y")

wa.columns = ['Date', 'Suburb']

nsw['State'] = "NSW"
vic['State'] = 'VIC'
qld['State'] = 'QLD'
wa['State'] = 'WA'

combo = pd.concat([nsw, vic, qld, wa])


# %%

# combo['Date'] = combo['Date'].str.split(" to ")[0]


combo['Date'] = pd.to_datetime(combo['Date'])
combo['Count'] = 1



combo = combo.groupby(by=["Date", "State"])['Count'].sum().reset_index()

combo['Date'] = combo['Date'].dt.strftime('%Y-%m-%d')

combo = combo.pivot(index="Date", columns="State")['Count'].reset_index()

# combo.columns.name=None
# combo.index.name = None

# combo.set_index('Date', inplace=True)

# print(combo)
# print(combo.columns)
# %%

# print(nsw['Date'].unique().tolist())
# %%

def makestackedbar(df):
	
    template = [
            {
                "title": "Exposure sites by state",
                "subtitle": f"""Showing the number of exposure sites by day of exposure. Last updated {today}""",
                "footnote": "",
                "source": "| Sources: State government websites",
                "dateFormat": "%Y-%m-%d",
                "minY": "0",
                "maxY": "",
                "xAxisDateFormat":"%b %d",
                "tooltip":"<strong>{{#formatDate}}{{data.Date}}{{/formatDate}}</strong><br/>{{group}}: {{groupValue}}<br/>Total: {{total}}",
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


    yachtCharter(template=template, labels=labels, data=chartData, chartId=[{"type":"stackedbar"}], chartName="oz-exposure-sites")

makestackedbar(combo)
