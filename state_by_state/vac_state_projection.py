#%%
import pandas as pd
import requests
import os
import ssl
from modules.yachtCharter import yachtCharter
import numpy as np
import datetime

testo = "_test"
# testo = ''

state_json = "https://covidlive.com.au/covid-live.json"

#%%

print("updating re-indexed state rollout chart")

# fixes ssl error on OSX???

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


pops = {'NT':246.5* 1000, 'NSW':8166.4* 1000, 
'VIC':6680.6* 1000, 'QLD':5184.8* 1000, 
'ACT':431.2* 1000, 'SA':1770.6* 1000, 
 'WA':2667.1* 1000, 'TAS':541.1* 1000}

# source: https://www.abs.gov.au/statistics/people/population/national-state-and-territory-population/sep-2020



# 16+ population counts:

sixteen_pop = {
    'NT':190571, 'NSW':6565651, 'VIC':5407574,
    'QLD':4112707, 'ACT':344037,
    'SA':1440400, 'WA':2114978, 'TAS':440172,
    'NT Trend':190571, 'NSW Trend':6565651, 
    'VIC Trend':5407574, 'QLD Trend':4112707,
    'ACT Trend':344037, 'SA Trend':1440400, 
    'WA Trend':2114978, 'TAS Trend':440172}


# source: https://www.health.gov.au/sites/default/files/documents/2021/07/covid-19-vaccine-rollout-update-5-july-2021.pdf


first = pd.read_json(state_json)

# 'REPORT_DATE', 'LAST_UPDATED_DATE', 'CODE', 'NAME', 'CASE_CNT',
#        'TEST_CNT', 'DEATH_CNT', 'RECOV_CNT', 'MED_ICU_CNT', 'MED_VENT_CNT',
#        'MED_HOSP_CNT', 'SRC_OVERSEAS_CNT', 'SRC_INTERSTATE_CNT',
#        'SRC_CONTACT_CNT', 'SRC_UNKNOWN_CNT', 'SRC_INVES_CNT', 'PREV_CASE_CNT',
#        'PREV_TEST_CNT', 'PREV_DEATH_CNT', 'PREV_RECOV_CNT', 'PREV_MED_ICU_CNT',
#        'PREV_MED_VENT_CNT', 'PREV_MED_HOSP_CNT', 'PREV_SRC_OVERSEAS_CNT',
#        'PREV_SRC_INTERSTATE_CNT', 'PREV_SRC_CONTACT_CNT',
#        'PREV_SRC_UNKNOWN_CNT', 'PREV_SRC_INVES_CNT', 'PROB_CASE_CNT',
#        'PREV_PROB_CASE_CNT', 'ACTIVE_CNT', 'PREV_ACTIVE_CNT', 'NEW_CASE_CNT',
#        'PREV_NEW_CASE_CNT', 'VACC_DIST_CNT', 'PREV_VACC_DIST_CNT',
#        'VACC_DOSE_CNT', 'PREV_VACC_DOSE_CNT', 'VACC_PEOPLE_CNT',
#        'PREV_VACC_PEOPLE_CNT', 'VACC_AGED_CARE_CNT', 'PREV_VACC_AGED_CARE_CNT',
#        'VACC_GP_CNT', 'PREV_VACC_GP_CNT'

first = first[['REPORT_DATE', 'LAST_UPDATED_DATE', 'CODE','VACC_PEOPLE_CNT',
       'PREV_VACC_PEOPLE_CNT']]

first.fillna({"PREV_VACC_AGED_CARE_CNT":0, "PREV_VACC_GP_CNT":0}, inplace=True)
non_aus = first.loc[first['CODE'] != "AUS"].copy()

## Get last date for updated date in subhead


# df = non_aus.append(aus)

#%%

df = non_aus
df = df[['REPORT_DATE', 'CODE', 'VACC_PEOPLE_CNT']].copy()
df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
df = df.sort_values(by="REPORT_DATE", ascending=True)

# print(df)

last_date = datetime.datetime.strftime(df['REPORT_DATE'].max(), "%Y-%m-%d")

current_date = df['REPORT_DATE'].max()

# idx = pd.period_range(min(current_date), max())

### WORK OUT THE ROLLING AVERAGES

print(df['CODE'].unique().tolist())

latest_counts = {}

rolling_averages = {}

for state in df['CODE'].unique().tolist():
    inter = df.loc[df['CODE'] == state].copy()
    inter['Incremental'] = inter['VACC_PEOPLE_CNT'].diff(1)
    inter['Rolling'] = inter['Incremental'].rolling(window=7).mean()

    latest = inter.loc[inter['REPORT_DATE'] == inter['REPORT_DATE'].max()].copy()

    latest_count = latest['VACC_PEOPLE_CNT'].values[0]
    # latest_counts[state] = latest_count
    
    latest_rolling = latest['Rolling'].values[0]
    # rolling_averages[state] = latest_rolling

    ### WORK OUT HOW MANY MORE DAYS TO GO

    vax_target = sixteen_pop[state] * 0.8

    vax_to_go = vax_target - latest_count

    days_to_go = vax_to_go / latest_rolling

    dates = [current_date + datetime.timedelta(days=x) for x in range(0, int(days_to_go))]

    next = pd.DataFrame(dates, columns=['REPORT_DATE'])
    next[f'VACC_PEOPLE_CNT'] = latest_rolling
    next.loc[next['REPORT_DATE'] == current_date, f'VACC_PEOPLE_CNT'] = latest_count
    next[f'VACC_PEOPLE_CNT'] = next[f'VACC_PEOPLE_CNT'].cumsum()
    next['CODE'] = f"{state} Trend"

    df = df.append(next)



#%%
## Calculate doses per hundred people
# pivoted['Day'] = pivoted.index
pivoted = df.pivot(index='REPORT_DATE', columns='CODE')['VACC_PEOPLE_CNT'].reset_index()

for col in pivoted.columns:
    # print(col)
    if col != "REPORT_DATE":
        # print(col)
        pivoted[col] = pd.to_numeric(pivoted[col])
        pivoted[col] = round((pivoted[col]/sixteen_pop[col])*100, 2)


pivoted = pivoted.replace({'0':np.nan, 0:np.nan})
pivoted.columns.name = None

# pivoted.drop(columns={'REPORT_DATE'}, inplace=True)

pivoted.to_csv('state-comparison.csv', index=False)

colours = ['#e5005a', "#f9b000", "#ffe500", "#bbce00", "#00a194", "#61c3d9", "#ea5a0b", "#4f524a", "#af1674"]
display_date = datetime.datetime.strptime(last_date, "%Y-%m-%d")
display_date = datetime.datetime.strftime(display_date, "%d/%m/%Y")

pivoted = pivoted.loc[pivoted['REPORT_DATE'] > "2021-03-01"]

pivoted['REPORT_DATE'] = pivoted['REPORT_DATE'].dt.strftime("%d/%m/%Y")

pivoted.set_index('REPORT_DATE', inplace=True)
print(pivoted)

#%%

def makeSince100Chart(df):

    template = [
            {
                "title": "Australia's state vaccine rollout",
                "subtitle": f"Showing the number of fully vaccinated people per 100 residents in each state. Projection shows when 80% of the 16+ population will be vaccinated. Last updated {display_date}.",
                "footnote": "",
                "source": "Covidlive.com.au, Australian Bureau of Statistics",
                "dateFormat": "",
                "yScaleType":"",
                "xAxisLabel": "Date",
                "yAxisLabel": "Full vaccinated",
                "minY": "",
                "maxY": "",
                "dateFormat":"%d/%m/%Y",
                "margin-left": "50",
                "margin-top": "15",
                "margin-bottom": "20",
                "margin-right": "20",
                "breaks":"no"
            }
        ]
    key = []
    periods = []
    labels = []
    chartId = [{"type":"linechart"}]
    df.fillna('', inplace=True)
    df = df.reset_index()
    chartData = df.to_dict('records')
    # print(since100.head())
    # print(chartData)
    # yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], options=[{"colorScheme":colours, "lineLabelling":"FALSE"}], chartName="state_rollout_per_hundred_test")
    yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], options=[{"colorScheme":colours, "lineLabelling":"FALSE"}], chartName=f"state_rollout_per_hundred_projection{testo}")


makeSince100Chart(pivoted)

