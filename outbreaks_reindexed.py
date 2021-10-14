#%%

import pandas as pd
from modules.yachtCharter import yachtCharter
import datetime

today = datetime.datetime.today()
today = datetime.datetime.strftime(today, "%Y-%m-%d")

# print(today)

chart_key = f"oz-outbreaks--cases-reindexed"
# chart_key = f"oz-outbreaks--cases-reindexed-testo"

fillo = "https://covidlive.com.au/covid-live.json"

#%%

print("updating re-indexed state rollout chart")

df = pd.read_json(fillo)

# 'REPORT_DATE', 'LAST_UPDATED_DATE',
# 'CODE', 'NAME', 'CASE_CNT', 'TEST_CNT',
# 'DEATH_CNT', 'RECOV_CNT', 'MED_ICU_CNT',
# 'MED_VENT_CNT', 'MED_HOSP_CNT', 'SRC_OVERSEAS_CNT',
# 'SRC_INTERSTATE_CNT', 'SRC_CONTACT_CNT', 'SRC_UNKNOWN_CNT',
# 'SRC_INVES_CNT', 'PREV_CASE_CNT', 'PREV_TEST_CNT',
# 'PREV_DEATH_CNT', 'PREV_RECOV_CNT', 'PREV_MED_ICU_CNT',
# 'PREV_MED_VENT_CNT', 'PREV_MED_HOSP_CNT', 'PREV_SRC_OVERSEAS_CNT',
# 'PREV_SRC_INTERSTATE_CNT', 'PREV_SRC_CONTACT_CNT',
# 'PREV_SRC_UNKNOWN_CNT', 'PREV_SRC_INVES_CNT', 'PROB_CASE_CNT',
# 'PREV_PROB_CASE_CNT', 'ACTIVE_CNT', 'PREV_ACTIVE_CNT',
# 'NEW_CASE_CNT', 'PREV_NEW_CASE_CNT', 'VACC_DIST_CNT',
# 'PREV_VACC_DIST_CNT', 'VACC_DOSE_CNT', 'PREV_VACC_DOSE_CNT',
# 'VACC_PEOPLE_CNT', 'PREV_VACC_PEOPLE_CNT', 'VACC_AGED_CARE_CNT',
# 'PREV_VACC_AGED_CARE_CNT', 'VACC_GP_CNT', 'PREV_VACC_GP_CNT',
# 'VACC_FIRST_DOSE_CNT', 'PREV_VACC_FIRST_DOSE_CNT'

df['CASE_CNT'] = pd.to_numeric(df['CASE_CNT'])

df['SRC_OVERSEAS_CNT'] = pd.to_numeric(df['SRC_OVERSEAS_CNT'])

df['Local_cnt'] = df['CASE_CNT'] - df['SRC_OVERSEAS_CNT']

df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
df = df.sort_values(by=['REPORT_DATE'], ascending=True)
df['REPORT_DATE'] = df['REPORT_DATE'].dt.strftime("%Y-%m-%d")

pops = {'NT':246.5* 1000, 'NSW':8166.4* 1000,
'VIC':6680.6* 1000, 'QLD':5184.8* 1000,
'ACT':431.2* 1000, 'SA':1770.6* 1000,
 'WA':2667.1* 1000, 'TAS':541.1* 1000}


#%%

def work_since_begin(code, frame, start, line_name, end_date=today):
    inter = frame.loc[df['CODE'] == code].copy()


    inter['New_local_cnt'] = inter['Local_cnt'].diff(1)
    # inter['New_local_cnt'] = (inter['New_local_cnt'] / pops[code]) * 1000000







    # inter[code] = inter['New_local_cnt'].rolling(window=7).mean()

    inter = inter.loc[(inter['REPORT_DATE'] > start) & (inter['REPORT_DATE'] <= end_date)]
    # print(inter['New_local_cnt'])
    inter[code] = inter['New_local_cnt'].cumsum()

    inter['Days'] = 1
    inter['Days'] = inter['Days'].cumsum()

    inter = inter[['Days', code]]
    inter.columns = ['Days', line_name]

    # print(inter)

    return (inter)

## USE THE DAY BEFORE THE FIRST CASE
nsw = work_since_begin("NSW", df, "2021-06-16", "NSW")
vic1 = work_since_begin("VIC", df, "2021-07-12", "VIC")
# vic1 = work_since_begin("VIC", df, "2021-07-12", "VIC Wave 1", "2021-08-03")
# vic2 = work_since_begin("VIC", df, "2021-08-04", "VIC Wave 2")
act = work_since_begin("ACT", df, "2021-08-11", "ACT")


combo = pd.merge(nsw, vic1, on="Days", how="left")
# combo = pd.merge(combo, vic2, on="Days", how="left")
combo = pd.merge(combo, act, on="Days", how="left")


df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
updated_date = df['REPORT_DATE'].max()
updated_date = datetime.datetime.strftime(updated_date, "%d %B %Y")

# print(combo)

nsw_max = combo['NSW'].max()
vic_max = combo['VIC'].max()
act_max = combo['ACT'].max()

def makeLineChart(df):

    template = [
            {
                "title": "Comparing 2021 Delta outbreaks in New South Wales, Victoria and the ACT",
                "subtitle": f"Showing cumulative local cases since the first day of each outbreak. Last updated {updated_date}",
                "footnote": "",
                "source": "Guardian analysis of CovidLive.com.au data | Based on a chart by Covid19data.com.au",
                # "dateFormat": "%Y-%m-%d",
                "yScaleType":"",
                "xAxisLabel": "Days",
                # "yAxisLabel": "Cases",
                "minY": "",
                "maxY": "",
                # "periodDateFormat":"",
                "margin-left": "30",
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
    # df = df.reset_index()
    chartData = df.to_dict('records')

    yachtCharter(template=template, data=chartData, periods=periods, chartId=[{"type":"linechart"}], options=[{"colorScheme":"guardian", "lineLabelling":"FALSE"}], chartName=f"{chart_key}")


makeLineChart(combo)
# %%


print(f"NSW so far: {nsw_max}")
print(f"VIC so far: {vic_max}")
print(f"ACT so far: {act_max}")