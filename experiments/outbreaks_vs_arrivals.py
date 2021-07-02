#%%

from modules.yachtCharter import yachtCharter
import pandas as pd 
import os 
import pytz
import datetime
import numpy

today = datetime.datetime.now(pytz.timezone("Australia/Sydney"))
today = datetime.datetime.strftime(today, '%Y-%m-%d')
today = datetime.datetime.strptime(today, '%Y-%m-%d')

caps_introduced = datetime.date(2020, 7, 1)

days_since_cap = today.date() - caps_introduced
days_since_cap = days_since_cap.days
weeks_since_cap = round(days_since_cap/7)

here = os.path.dirname(__file__)
data_path = os.path.dirname(__file__) + "/data/"
output_path = os.path.dirname(__file__) + "/output/"

fillo = f"experiments/breaches.csv"

#%%

df = pd.read_csv(fillo, skiprows=4)
df = df.dropna(subset=['LINK'])
df = df[['NO', 'STATE', 'DATE', 'FACILITY',
       'CASE NAME', 'VARIANT', 'ONWARD', 'VAX', 'LINK']]
df = df.loc[df['STATE'] != "STATE"]

df['DATE'] = pd.to_datetime(df['DATE'])

# print(df)
# print(df.columns)


#%%

## WORK OUT DAYS SINCE LAST BREACH

listo = []

for state in df['STATE'].unique().tolist():
    inter = df.loc[df["STATE"] == state].copy()
    latest = inter.loc[inter['DATE'] == inter['DATE'].max()].copy()

    latest_date = latest['DATE'].values[0]
    latest_date = pd.Timestamp(latest_date).to_pydatetime()

    delta = today - latest_date
    delta = delta.days

    latest['Days since'] = delta

    # print(type(latest_date))

    listo.append(latest)

final = pd.concat(listo)

final = final[["STATE", "Days since"]]
final.columns = ['State', "Days since last quarantine breach"]




#%%

## WORK OUT TOTAL NUMBER OF BREACHES BY STATE


grouped = df.groupby(by="STATE").count().reset_index()
grouped = grouped[['STATE', 'NO']]
grouped.columns = ["State", "Number of breaches"]

### Combine

combo = pd.merge(grouped, final, on="State")




### WORK OUT TOTAL 



#%%
import datetime
import pandas as pd 
import os

here = os.path.dirname(__file__)
data_path = os.path.dirname(__file__) + "/data/"
output_path = os.path.dirname(__file__) + "/output/"

sheet = 'experiments/data/3401055004_OTSP_State_May21.xlsx'


#%%

## WORK OUT VISITOR REASONS

df2 = pd.read_excel(sheet, skiprows=7, sheet_name="Table 1.1")

df2 = df2[['Month', 'New South Wales', 'Victoria', 'Queensland', 'South Australia',
       'Western Australia', 'Tasmania', 'Northern Territory', 'ACT']]

df2.columns = ['Date', 'New South Wales', 'Victoria', 'Queensland', 'South Australia',
       'Western Australia', 'Tasmania', 'Northern Territory', 'ACT']

# df = df[:58]
df2 = df2.dropna(subset=['New South Wales'])

df2['Date'] = pd.to_datetime(df2['Date'])
df2['Date'] = df2['Date'].dt.strftime('%Y-%m-%d')
df2 = df2.loc[df2['Date'] > "2020-04-01"]

df2 = df2.append(df2.sum(), ignore_index=True)
df2 = df2.loc[df2['New South Wales'] == df2['New South Wales'].max()]
df2 = df2[['New South Wales', 'Victoria', 'Queensland', 'South Australia',
       'Western Australia', 'Tasmania', 'Northern Territory', 'ACT']]

df2 = df2.T.reset_index()

df2.columns = ['State', "Total arrivals"]
df2 = df2.sort_values(by="Total arrivals", ascending=False)

state_list = [("NSW", "New South Wales"), ("VIC", "Victoria"), ("QLD", "Queensland"),
 ("SA", "South Australia"), ("WA", "Western Australia"), ("TAS", "Tasmania"), ("NT", "Northern Territory"), "ACT", "ACT"]




for state in state_list:
    df2.loc[df2['State'] == state[1], 'State'] = state[0]


combo = pd.merge(df2, combo, on="State")

combo['Breaches per arrival'] = round(combo['Total arrivals'] / combo['Number of breaches'])
combo['Avg days between breach'] = round(days_since_cap / combo['Number of breaches'])

combo.columns = ['State','Arrivals', 'Breaches', 'Days since breach', 'Breaches per arrival', 'Avg days between breach']
combo = combo[['State', 'Arrivals', 'Breaches',
       'Breaches per arrival', 'Avg days between breach', 'Days since breach']]

nice_today = datetime.datetime.strftime(today, "%d/%m/%Y")

def makeTable(df):

    template = [
            {
                "title": "Quarantine breaches by state",
                "subtitle": f"""Showing international arrivals and quarantine breaches per state. Last updated {nice_today}.""",
                "footnote": "",
                "source": "Australian Bureau of Statistics, CovidLive.com.au",
                "yScaleType":"",
                "minY": "0",
                "maxY": "",
                "margin-left": "50",
                "margin-top": "30",
                "margin-bottom": "0",
                "margin-right": "10"
            }
        ]
    key = [{"key":"Breaches", 
    "values": f"",
     "colours":"#ffffff, #d10a10", 
     "scale":"linear"},
     {"key":"Breaches per arrival", 
    "values": "",
     "colours":"#ffffff, #d10a10", 
     "scale":"linear"}
     ,
     {"key":"Days since breach", 
    "values": f"{combo['Days since breach'].max()},{combo['Days since breach'].min()}",
     "colours":"#ffffff, #d10a10", 
     "scale":"linear"}]
    # key = []
    # labels = []
    df.fillna("", inplace=True)
    chartData = df.to_dict('records')
    # labels = []


    yachtCharter(template=template, data=chartData, chartId=[{"type":"table"}],
    options=[{"format": "scrolling","enableSearch": "FALSE","enableSort": "FALSE"}], key=key, chartName=f"oz-covid-outbreaks-table")


makeTable(combo)