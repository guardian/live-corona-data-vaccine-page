#%%
import requests
import pandas as pd 
import datetime
chart_key = f"oz-covid-act-july2021-outbreak"
import os 
# from modules.yachtCharter import yachtCharter

#%%

# fillo = 'https://docs.google.com/spreadsheets/d/1QPWOLzfqyNC8Voe-d-I-TQ5EfJ1dAuzp8CevkD01RiA/pub?gid=1454102594&single=True&output=csv'
fillo = 'https://docs.google.com/spreadsheets/d/10PqRjyk5yfPYgekNaNJ7T4pGNGwy_7-6VCZJkxuIlE0/pub?gid=1454102594&single=True&output=csv'
statto = "ACT"
init = "2021-08-11"

#%%

# GRAB Current data

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

new = r.json()
new = pd.read_json(r.text)


#%%

znew = new.copy()

def together(state, new_data, past, start):

    ### Grab old data 

    old_data = pd.read_csv(past)

    ## Subset data
    inter = new_data.loc[new_data['CODE'] == state].copy()

    inter['REPORT_DATE'] = pd.to_datetime(inter['REPORT_DATE'])
    inter = inter.sort_values(by=['REPORT_DATE'], ascending=True)

    # Reduce days by one day to get the actual date
    inter['REPORT_DATE'] = inter['REPORT_DATE'] - datetime.timedelta(days=1)


    inter['REPORT_DATE'] = inter['REPORT_DATE'].dt.strftime("%Y-%m-%d")

    ## Calculate new local cases
    inter['New_local'] = inter['CASE_CNT'] - inter['SRC_OVERSEAS_CNT']
    inter['New_local'] = inter['New_local'].diff(1)

    inter = inter[['REPORT_DATE','New_local']]

    inter.columns = ['Date', 'Locally-acquired cases']

    old_data['Date'] = pd.to_datetime(old_data['Date'], format="%d/%m/%Y")
    old_data['Date'] = old_data['Date'].dt.strftime("%Y-%m-%d")

    latest_date = old_data['Date'].max()

    new_index = pd.date_range(start, inter['Date'].max())

    old_data.index = pd.DatetimeIndex(old_data['Date'])
    old_data = old_data.reindex(new_index, fill_value='NaN').reset_index()
    old_data = old_data[['index', 'Locally-acquired cases']]
    old_data.columns = ['Date', 'Locally-acquired cases']
    old_data['Date'] = old_data['Date'].dt.strftime("%Y-%m-%d")

    inter = inter.loc[inter['Date'] >= start]

    old_data = old_data.reset_index()
    inter = inter.reset_index()

    ## Combine and update missing values
    print(statto)
    print("sheet",old_data.tail())

    # old_data['Locally-acquired cases'].update(inter['Locally-acquired cases'])
    old_data.update(inter)
    


    old_data = old_data[['Date', 'Locally-acquired cases']]

    print(old_data.tail())

    return old_data


old = together(statto, znew, fillo, init)  

print(old.tail())

# %%

## Get the trendline

roll = old.copy()
roll['Trend'] = roll['Locally-acquired cases'].rolling(window=7).mean()

roll = roll[['Date', 'Trend']]


## Combine for export 

tog = pd.merge(old, roll, on='Date', how='left')

# with open(f"state_outbreaks/output/{statto}.csv", "w") as f:
#     tog.to_csv(f, index=False, header=True)


roll.fillna('', inplace=True)
roll = roll.to_dict(orient='records')
# p = roll

# print(p)
# print(p.columns.tolist())

last_updated = old['Date'].max()
last_updated = datetime.datetime.strptime(last_updated, "%Y-%m-%d")
last_updated = last_updated + datetime.timedelta(days=1)
display_date = datetime.datetime.strftime(last_updated, "%-d %B %Y")


# %%


def makeTestingLine(df):

    template = [
            {
                "title": "Covid cases announced daily in the ACT",
                "subtitle": f"""Showing the number of locally-acquired cases announced daily and the trend as a 7-day rolling average. Last updated {display_date}.""",
                "footnote": "",
                "source": "Sources: ACT Health, CovidLive.com.au, Guardian Australia",
                "dateFormat": "%Y-%m-%d",
                "xAxisDateFormat":"%b %d",
                "minY": "0",
                "maxY": "",
                "x_axis_cross_y":"",
                "periodDateFormat":"",
                "margin-left": "50",
                "margin-top": "30",
                "margin-bottom": "20",
                "margin-right": "10"
            }
        ]
    key = [{"key":"Locally-acquired cases", "colour":"#fc9272"}]
    periods = []
    labels = []
    df.fillna("", inplace=True)
    chartData = df.to_dict('records')


    yachtCharter(template=template, labels=labels, key=key, trendline=roll, data=chartData, chartId=[{"type":"stackedbar"}],
    options=[{"colorScheme":"guardian"}], chartName=f"{chart_key}")

# makeTestingLine(old)

