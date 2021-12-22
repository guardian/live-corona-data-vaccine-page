#%%
import requests
import pandas as pd 
import time
import random
import datetime
# pd.set_option("display.max_rows", 100)
from yachtcharter import yachtCharter
chart_key = f"oz-covid-rolling-cases-hospos-state"

#%%

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

#%%

## Grab Covid Live Data

data = r.json()
df = pd.read_json(r.text)
df = df.sort_values(by='REPORT_DATE', ascending=True)

# 'REPORT_DATE', 'LAST_UPDATED_DATE', 
# 'CODE', 'NAME', 'CASE_CNT', 'TEST_CNT', 
# 'DEATH_CNT', 'RECOV_CNT', 'MED_ICU_CNT', 'MED_VENT_CNT',
# 'MED_HOSP_CNT', 'SRC_OVERSEAS_CNT', 'SRC_INTERSTATE_CNT', 
# 'SRC_CONTACT_CNT', 'SRC_UNKNOWN_CNT', 'SRC_INVES_CNT', 
# 'PREV_CASE_CNT', 'PREV_TEST_CNT', 'PREV_DEATH_CNT', 
# 'PREV_RECOV_CNT', 'PREV_MED_ICU_CNT', 'PREV_MED_VENT_CNT', 
# 'PREV_MED_HOSP_CNT', 'PREV_SRC_OVERSEAS_CNT', 'PREV_SRC_INTERSTATE_CNT',
# 'PREV_SRC_CONTACT_CNT', 'PREV_SRC_UNKNOWN_CNT', 'PREV_SRC_INVES_CNT', 
# 'PROB_CASE_CNT', 'PREV_PROB_CASE_CNT', 'ACTIVE_CNT', 'PREV_ACTIVE_CNT',
# 'NEW_CASE_CNT', 'PREV_NEW_CASE_CNT', 'VACC_DIST_CNT', 'PREV_VACC_DIST_CNT',
# 'VACC_DOSE_CNT', 'PREV_VACC_DOSE_CNT', 'VACC_PEOPLE_CNT',
# 'PREV_VACC_PEOPLE_CNT', 'VACC_AGED_CARE_CNT', 'PREV_VACC_AGED_CARE_CNT',
# 'VACC_GP_CNT', 'PREV_VACC_GP_CNT', 'VACC_FIRST_DOSE_CNT',
# 'PREV_VACC_FIRST_DOSE_CNT', 'VACC_FIRST_DOSE_CNT_12_15',
# 'PREV_VACC_FIRST_DOSE_CNT_12_15', 'VACC_PEOPLE_CNT_12_15',
# 'PREV_VACC_PEOPLE_CNT_12_15', 'VACC_BOOSTER_CNT', 'PREV_VACC_BOOSTER_CNT'

#%%

zdf = df.copy()

zdf = zdf[['REPORT_DATE','CODE', 'CASE_CNT', 'MED_HOSP_CNT',]]

def charter(frame, chart_base, state):

    print(f"\nThis is {state}")

    inter = frame.loc[frame['CODE'] == state].copy()

    inter['CASE_CNT'] = inter['CASE_CNT'].diff(1)
    inter['Cases_rolling'] = round(inter['CASE_CNT'].rolling(window=7).mean(),2)

    inter = inter[['REPORT_DATE', 'MED_HOSP_CNT', 'Cases_rolling']]
    inter.columns = ['Date', 'In hospital', 'New cases, 7 day avg']

    inter_chart_key = chart_base + f"_{state}"

    current_date = inter['Date'].max()
    init_date = datetime.datetime.strptime(current_date, "%Y-%m-%d")
    format_date = datetime.datetime.strftime(init_date, '%-d %B %Y')

    six_months = init_date - datetime.timedelta(days=180)

    cutoff_date = datetime.datetime.strftime(six_months, "%Y-%m-%d")

    inter = inter.loc[inter['Date'] >= cutoff_date]

    inter.fillna('', inplace=True)

    final = inter.to_dict(orient='records')

    # print("Six months", six_months)

    if state == "VIC":
        state_name = "Victorian"
    elif state == "AUS":
        state_name = "National"
    elif state == "QLD":
        state_name = "Queensland"
    elif state == "SA":
        state_name = "South Australian"  
    # elif state == "ACT":
    #     state_name = "Australian Capital Territory"      
    else:
        state_name = state

    template = [
        {
        "title": f"{state_name} daily new Covid-19 cases and hospitalisations",
        "subtitle": f"Showing the rolling seven-day average of daily new cases, and the total count of Covid-19 patients in hospital on each day. Last updated {format_date}",
        "footnote": "",
        "source": "CovidLive.com.au",
        "margin-left": "35",
        "margin-top": "30",
        "margin-bottom": "20",
        "margin-right": "10",
        "tooltip":"<strong>{{#formatDate}}{{Date}}{{/formatDate}}</strong><br/> New cases: {{New cases, 7 day avg}}<br/>In hospital: {{In hospital}}<br/>"
        }
    ]

    yachtCharter(template=template, 
                data=final,
                chartId=[{"type":"linechart"}],
                options=[{"colorScheme":"guardian", "lineLabelling":"TRUE"}],
                chartName=f"{inter_chart_key}")

    time.sleep(random.random())

    # p = inter
    # print(p)
    # print(p.columns.tolist())

for state in ['AUS', 'NSW', 'VIC', 'ACT', 'QLD', 'SA']:

    charter(zdf, chart_key, state)

# print(zdf['CODE'].unique().tolist())
# %%
