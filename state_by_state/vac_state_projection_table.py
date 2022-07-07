#%%
import pandas as pd
import requests
import os
import ssl
from modules.yachtCharter import yachtCharter
import numpy as np
import datetime
import pytz

today = datetime.datetime.today().date()

testo = "_test"
# testo = ''
chart_key = "oz-live-corona-state-vax-table"
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
    'SA':1440400, 'WA':2114978, 'TAS':440172, "AUS":20619959}

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

non_aus = first.loc[first['CODE'] != "AUS"].copy()

#%%

df = non_aus
df = df[['REPORT_DATE', 'CODE', 'PREV_VACC_PEOPLE_CNT']].copy()
df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
df = df.sort_values(by="REPORT_DATE", ascending=True)

#%%
last_date = datetime.datetime.strftime(df['REPORT_DATE'].max(), "%Y-%m-%d")

current_date = df['REPORT_DATE'].max()

latest_counts = {}

rolling_averages = {}

days_to_80 = {}

projections_80 = {}
projections_70 = {}

listo = []

for state in df['CODE'].unique().tolist():
    inter = df.loc[df['CODE'] == state].copy()
    inter['Incremental'] = inter['PREV_VACC_PEOPLE_CNT'].diff(1)
    inter['Rolling'] = inter['Incremental'].rolling(window=7).mean()

    # print(inter)

    latest = inter.loc[inter['REPORT_DATE'] == inter['REPORT_DATE'].max()].copy()

    latest_count = latest['PREV_VACC_PEOPLE_CNT'].values[0]
    # latest_counts[state] = latest_count

    latest_rolling = latest['Rolling'].values[0]

    # rolling_averages[state] = latest_rolling

    ### WORK OUT HOW MANY MORE DAYS TO GO

    eighty_target = sixteen_pop[state] * 0.8
    seventy_target = sixteen_pop[state] * 0.7

    eighty_vax_to_go = eighty_target - latest_count
    seventy_vax_to_go = seventy_target - latest_count

    days_to_go_80 = int(round(eighty_vax_to_go / latest_rolling,0))
    days_to_go_70 = int(round(seventy_vax_to_go / latest_rolling,0))

    eighty_finish = today + datetime.timedelta(days=days_to_go_80)
    seventy_finish = today + datetime.timedelta(days=days_to_go_70)

    eighty_finish = datetime.datetime.strftime(eighty_finish, "%d/%m/%Y")

    seventy_finish = datetime.datetime.strftime(seventy_finish, "%d/%m/%Y")

    projections_80[state] = eighty_finish
    projections_70[state] = seventy_finish


    latest_count_hundred = round((latest_count/sixteen_pop[state])*100, 2)

    latest_rolling = round(latest_rolling,0)

    final = pd.DataFrame.from_dict({"State": state,
                                    "Percent of 16+ population fully vaccinated": latest_count_hundred,
                                    "Seven day average of second doses": latest_rolling,
                                    "To fully vaccinate 70% of 16+": f"{days_to_go_70} days ({seventy_finish})",
                                    "To fully vaccinate 80% of 16+": f"{days_to_go_80} days ({eighty_finish})"}, orient="index")
                                    # columns=(['Row', "Values"]))

    final = final.T

    # print(final)

    listo.append(final)
    # dates = [current_date + datetime.timedelta(days=x) for x in range(0, int(days_to_go))]

    # next = pd.DataFrame(dates, columns=['REPORT_DATE'])
    # next[f'VACC_PEOPLE_CNT'] = latest_rolling
    # next.loc[next['REPORT_DATE'] == current_date, f'VACC_PEOPLE_CNT'] = latest_count
    # next[f'VACC_PEOPLE_CNT'] = next[f'VACC_PEOPLE_CNT'].cumsum()
    # next['CODE'] = f"{state} Trend"

    # df = df.append(next)

final_final = pd.concat(listo)

final_final = final_final.sort_values(by="State", ascending=True)

# %%


updated_date = datetime.datetime.now()
updated_date = updated_date.astimezone(pytz.timezone("Australia/Sydney")).strftime('%d %B %Y')


def makeTable(df):

    template = [
            {
                "title": "When the states might hit vaccination thresholds",
                "subtitle": f"""Showing how many of the 16+ population has been fully vaccinated, and when the 70% and 80% thresholds will be reached based on a seven day rolling average. Last updated {updated_date}""",
                "footnote": "",
                "source": "CovidLive.com.au, Australian Bureau of Statistics, Department of Health",
                "yScaleType":"",
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
    key = []
    # labels = []
    df.fillna("", inplace=True)
    chartData = df.to_dict('records')
    labels = []


    yachtCharter(template=template, labels=labels, data=chartData, chartId=[{"type":"table"}],
    options=[{"colorScheme":"guardian","format": "vanilla","enableSearch": "FALSE","enableSort": "FALSE"}], chartName=f"{chart_key}{testo}")

makeTable(final_final)

# print(final_final)
# print(final_final.columns)

third = pd.read_json('https://vaccinedata.covid19nearme.com.au/data/air_residence.json')

# third.to_csv('air-residence.csv')
# 'AIR_RESIDENCE_FIRST_DOSE_APPROX_COUNT',
#        'AIR_RESIDENCE_SECOND_DOSE_APPROX_COUNT', 'ABS_ERP_JUN_2020_POP',
#        'VALIDATED', 'URL', 'AIR_RESIDENCE_FIRST_DOSE_COUNT',
#        'AIR_RESIDENCE_SECOND_DOSE_COUNT'

# %%
second = third.copy()

second['DATE_AS_AT'] = pd.to_datetime(second['DATE_AS_AT'])
second = second.sort_values(by='DATE_AS_AT', ascending=True)

listo = []

for state in second['STATE'].unique().tolist():
    inter = second.loc[second['STATE'] == state].copy()
    to_use = inter.loc[(inter["AGE_LOWER"] == 16) & (inter['AGE_UPPER'] == 999)].copy()

    to_use['Second_new'] = to_use['AIR_RESIDENCE_SECOND_DOSE_COUNT'].diff(1)
    to_use['Second_rolling'] = to_use['Second_new'].rolling(window=7).mean()

    latest = to_use.loc[to_use['DATE_AS_AT'] == to_use['DATE_AS_AT'].max()].copy()
    
    latest = latest[['STATE', 'AIR_RESIDENCE_FIRST_DOSE_PCT', 'AIR_RESIDENCE_SECOND_DOSE_PCT','AIR_RESIDENCE_SECOND_DOSE_COUNT', 'Second_rolling']]

    # print(latest)
    # latest_count = latest['AIR_RESIDENCE_SECOND_DOSE_COUNT'].values[0]
    # latest_rolling = latest['Second_rolling'].values[0]

    ### WORK OUT HOW MANY MORE DAYS TO GO

    

    # eighty_target = sixteen_pop[state] * 0.8
    # seventy_target = sixteen_pop[state] * 0.7

    # eighty_vax_to_go = eighty_target - latest_count
    # seventy_vax_to_go = seventy_target - latest_count



    # days_to_go_80 = int(round(eighty_vax_to_go / latest_rolling,0))
    # days_to_go_70 = int(round(seventy_vax_to_go / latest_rolling,0))

    # eighty_finish = today + datetime.timedelta(days=days_to_go_80)
    # seventy_finish = today + datetime.timedelta(days=days_to_go_70)

    eighty_finish = datetime.datetime.strptime(projections_80[state], "%d/%m/%Y")
    seventy_finish = datetime.datetime.strptime(projections_70[state], "%d/%m/%Y")
    eighty_finish = datetime.datetime.strftime(eighty_finish, "%d %B")
    seventy_finish = datetime.datetime.strftime(seventy_finish, "%d %B")

    final = pd.DataFrame.from_dict({"State": state,
                                    "First dose %": latest['AIR_RESIDENCE_FIRST_DOSE_PCT'].values[0],
                                    "Second dose %": latest['AIR_RESIDENCE_SECOND_DOSE_PCT'].values[0],
                                    "Reach 70% on": f"{seventy_finish}",
                                    "Reach 80% on": f"{eighty_finish}"}, orient="index")
                                    # columns=(['Row', "Values"]))

    final = final.T

    listo.append(final)

    
small = pd.concat(listo)

def makeTable(df):

    template = [
            {
                "title": "Current vaccination levels by jurisdiction",
                "subtitle": f"""Showing the percentage of the 16+ population vaccinated by dose and state of residence, and the date we could hit 70% and 80% of the 16+ population fully vaccinated based on the seven day moving average of second doses. Last updated {updated_date}""",
                "footnote": "",
                "source": "Department of Health, Ken Tsang",
                "yScaleType":"",
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
    key = []
    # labels = []
    df.fillna("", inplace=True)
    chartData = df.to_dict('records')
    labels = []


    yachtCharter(template=template, labels=labels, data=chartData, chartId=[{"type":"table"}],
    options=[{"colorScheme":"guardian","format": "vanilla","enableSearch": "FALSE","enableSort": "FALSE"}], chartName=f"oz-vax-percent-table-states{testo}")

makeTable(small)

# %%
