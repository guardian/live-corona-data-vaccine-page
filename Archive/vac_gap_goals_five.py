from modules.yachtCharter import yachtCharter
from modules.numberFormat import numberFormat
import pandas as pd
import datetime
import numpy as np
import os, ssl
import requests

pd.set_option("display.max_rows", None, "display.max_columns", None)

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

oz_json = 'https://interactive.guim.co.uk/2021/02/coronavirus-widget-data/aus-vaccines2.json'

# test = "_test"
test = ""

def second_builder(start, listers, which):
    # To calculate number of days for the date range
    num_days = 0
    listo = []
    for tupple in listers:
        num_days += tupple[1]
        # Divide total in phase by number of days in phase
        inter = [(tupple[0]//tupple[1]) for x in range(0, tupple[1])]
        listo.append(inter)
    # Flatten list of lists
    divided = [item for sublist in listo for item in sublist]
    # Create date range
    dates = [start + datetime.timedelta(days=x) for x in range(0, num_days)]
    # Zip together
    zipped = list(zip(dates, divided))
    # Make dataframe
    inter = pd.DataFrame(zipped)
    #Rename
    inter.rename(columns={0:"Date", 1:f"{which} target needed per day"}, inplace=True)
    inter['Date'] = pd.to_datetime(inter['Date'])
    inter[f"{which} goal"] = inter[f"{which} target needed per day"].cumsum()

    return inter
#%%

### WORK OUT ROLLOUTS

rollout_begin = datetime.date(2021, 2, 22)
rollout_end = datetime.date(2021, 10, 31)

# second_dose_begin = rollout_begin + datetime.timedelta(days=84)
second_dose_begin = datetime.date(2021, 3, 20)

# chart_truncate =  datetime.date(2022, 1, 31)

## READ IN ACTUAL VACCINATIONS

oz = pd.read_json(oz_json)

oz['REPORT_DATE'] = pd.to_datetime(oz['REPORT_DATE'])
oz = oz.sort_values(by="REPORT_DATE", ascending=True)

### ORIGINAL GOAL

## Dose counts

Original_goal = 45000000 / 2

original_goal_days = rollout_end - second_dose_begin
origina_goal_delta = original_goal_days.days

original_rollout = [(Original_goal, origina_goal_delta)]

original_target = second_builder(second_dose_begin, original_rollout, "Original")

original_start = oz.loc[oz['REPORT_DATE'] == "2021-03-19"].copy()
original_start = original_start[['REPORT_DATE','PREV_VACC_PEOPLE_CNT']]
original_start.columns = ['Date', 'Original goal']

original_target = original_start.append(original_target)


## Calculate latest count

latest_count = oz['PREV_VACC_PEOPLE_CNT'].max()
last_date = datetime.datetime.strftime(oz['REPORT_DATE'].max(), "%Y-%m-%d")
first_date = datetime.datetime.strftime(oz['REPORT_DATE'].min(), "%Y-%m-%d")

# Remove 12 - 15 yos

oz['PREV_VACC_PEOPLE_CNT'] = oz['PREV_VACC_PEOPLE_CNT'] - oz["PREV_VACC_PEOPLE_CNT_12_15"]
# oz['PREV_VACC_DOSE_CNT'] = oz['PREV_VACC_DOSE_CNT'] - oz["VACC_FIRST_DOSE_CNT_12_15"]

# oz['first_dose'] = oz['PREV_VACC_DOSE_CNT'] - oz['PREV_VACC_PEOPLE_CNT'] - oz["VACC_FIRST_DOSE_CNT_12_15"]

oz = oz[['REPORT_DATE', 'PREV_VACC_PEOPLE_CNT', 'PREV_VACC_DOSE_CNT']]

#%%

projections = requests.get("https://interactive.guim.co.uk/yacht-charter-data/new-model-state-projections.json").json()['sheets']['data']

# tested = [x for x in projections if x['state'] == "AUS"]
# print(tested[0])
# tested = sorted(tested, key=lambda x: x['ninety_finish_second'])
# print(tested[0])

projections = [x for x in projections if x['state'] == "AUS"][0]




#%%
### APPEND GOALS TO DUMMY DATASET

dummy_vals = [x for x in range(0, 500)]

dummy_date = '2021-02-22'

dummy_df = pd.DataFrame({"Units":1,
                "Date": pd.date_range(start=dummy_date, periods=len(dummy_vals))})


dummy_df = dummy_df.loc[dummy_df['Date'] >= "2021-02-22"]

dummy_combo = pd.merge(dummy_df, original_target, left_on="Date", right_on="Date", how="left")

## Merge current vaccine total with goal dataframes
combo = pd.merge(dummy_combo, oz, left_on="Date", right_on="REPORT_DATE", how="left")

combo.rename(columns={'PREV_VACC_PEOPLE_CNT': "Fully vaccinated"}, inplace=True)

combo = combo.sort_values(by="Date", ascending=True)
#%%
# print(combo)

## Truncate dataset
# combo = combo.loc[combo['Date'] <= np.datetime64(chart_truncate)]

combo['Date'] = combo['Date'].dt.strftime('%Y-%m-%d')
combo.rename(columns={"Fully vaccinated":f"Fully vaccinated: {numberFormat(latest_count)}", "Second goal":"Revised rollout"}, inplace=True)


combo = combo[['Date', f"Fully vaccinated: {numberFormat(latest_count)}", f"Original goal"]]

## Work out rolling average

how_many_days = 7

combo['Incremental'] = combo[f"Fully vaccinated: {numberFormat(latest_count)}"].diff(periods=1)
combo[f'{how_many_days} day rolling average'] = combo['Incremental'].rolling(how_many_days).mean()

## Get latest rolling average and use it to extrapolate trend
averager = combo.dropna()
averager = combo.loc[~combo[f"Fully vaccinated: {numberFormat(latest_count)}"].isna()]
## THIS IS WHERE I FIXED TO CORRECT THE MOVING AVERAGE

# with open("state_by_state/new-projections.json", 'r') as f:
# 	projections = json.load(f)

latest_average = averager[-1:][f'{how_many_days} day rolling average'].values[0]
# latest_average = projections[0]['second_doses_rate_needed']
print("average", latest_average)


combo['Trend'] = combo['Incremental']
combo.loc[combo['Date'] == first_date, 'Trend'] = 20
combo.loc[combo['Date'] > last_date, 'Trend'] = projections['ninety_second_doses_needed']
# combo.loc[combo['Date'] > last_date, 'Trend'] = latest_average
combo['Trend'] = round(combo['Trend'].cumsum())
combo.loc[combo['Date'] <= last_date, 'Trend'] = np.nan

#%%

### WORK OUT TIME TO 80% OF 16+

over_16 = 20619959

eighty = over_16*0.8
ninety = over_16 * 0.9

combo['80% vaxxed'] = combo['Trend']
# combo.loc[combo['80% vaxxed'] > eighty, '80% vaxxed'] = np.nan
# combo.loc[combo['80% vaxxed'] > over_16, '80% vaxxed'] = np.nan
# combo.loc[combo['80% vaxxed'] > ninety, '80% vaxxed'] = np.nan

# goal = over_16 * 0.8

# rollout_begin = datetime.date(2021, 2, 22)
# today = datetime.datetime.today().date()

# days_running = today - rollout_begin
# days_running = days_running.days

# # Work out number of days to get to 80% given latest average

# num_days = round((goal-latest_count)/latest_average)

# end_date = today + datetime.timedelta(days=num_days)

# months_to_go = (end_date.year - today.year) * 12 + end_date.month - today.month

projection_end_date = datetime.datetime.strptime(projections['ninety_finish_second'], "%Y-%m-%d")
end_date_formated = datetime.datetime.strftime(projection_end_date, "%-d %B, %Y")
# end_date_label = datetime.datetime.strftime(end_date, "%Y-%m-%d")

# # Work out number of days to get to 80% given latest average

# seventy_num = round(((over_16*0.7)-latest_count)/latest_average)

# seventy_end_date = today + datetime.timedelta(days=seventy_num)

# seventy_end_date_formated = datetime.datetime.strftime(seventy_end_date, "%d/%m/%Y")
# seventy_end_date_label = datetime.datetime.strftime(seventy_end_date, "%Y-%m-%d")

# ### WORK OUT 80% AND 70% BY EOY

# eighty_goal = goal
# eighty_goal_text = f"80% by <br>{datetime.datetime.strftime(end_date, '%-d %B')}"

# eighty_doses_so_far = combo.loc[combo["Date"] == "2021-07-28"][f"Fully vaccinated: {numberFormat(latest_count)}"].values[0]

# eighty_doses_left = eighty_goal - eighty_doses_so_far

# eighty_days = datetime.date(2021, 12, 31) - datetime.date(2021, 7, 30)
# eighty_days = eighty_days.days

# eighty_eoy = eighty_doses_left / eighty_days

# # print(eighty_eoy)

# combo['80% by EOY'] = combo['Incremental']
# combo.loc[combo['Date'] >= "2021-07-28", '80% by EOY'] = eighty_eoy

# combo['80% by EOY'] = combo['80% by EOY'].cumsum()

# combo.loc[combo['Date'] < "2021-07-28", '80% by EOY'] = np.nan

# seventy_goal = (over_16)*0.7
# seventy_goal_text = f"70% by <br>{datetime.datetime.strftime(seventy_end_date, '%-d %B')}"


# seventy_doses_so_far = combo.loc[combo["Date"] == "2021-07-28"][f"Fully vaccinated: {numberFormat(latest_count)}"].values[0]

# seventy_doses_left = seventy_goal - seventy_doses_so_far

# seventy_days = datetime.date(2021, 12, 31) - datetime.date(2021, 7, 30)
# seventy_days = seventy_days.days

# seventy_eoy = seventy_doses_left / seventy_days


# combo['70% by EOY'] = combo['Incremental']
# combo.loc[combo['Date'] >= "2021-07-28", '70% by EOY'] = seventy_eoy

# combo['70% by EOY'] = combo['70% by EOY'].cumsum()

# combo.loc[combo['Date'] < "2021-07-28", '70% by EOY'] = np.nan

combo = combo[['Date', 'Original goal', '80% vaxxed', f"Fully vaccinated: {numberFormat(latest_count)}"]]
combo.columns = ['Date', 'Original goal', 'Trend', f"Fully vaccinated: {numberFormat(latest_count)}"]

# print(combo)

display_date = datetime.datetime.strptime(last_date, "%Y-%m-%d")
display_date = datetime.datetime.strftime(display_date, "%-d %B, %Y")

# print(combo)
# print(combo)


# chart_truncate = end_date + datetime.timedelta(days=50)

chart_truncate = datetime.date(2022,2,28)

combo['Date'] = pd.to_datetime(combo['Date'])

combo = combo.loc[combo['Date'] <= np.datetime64(chart_truncate)]

combo['Date'] = combo['Date'].dt.strftime('%Y-%m-%d')

#%%

# hit_80 = ['70% by EOY']


def makeTestingLine(df):

    template = [
            {
                "title": "Tracking the Covid-19 vaccine rollout in Australia",
                "subtitle": f"""Showing the number of Australians that are fully vaccinated, the federal government's <a href='https://www.theguardian.com/news/datablog/2021/feb/28/is-australias-goal-of-vaccinating-the-entire-adult-population-by-october-achievable' target='_blank'>original rollout goal</a>, and theshholds for 70, 80 and 90% of the 16+ population. Last updated {display_date}<br>""",
                # "subtitle": f"""Showing the number of Australians that are fully vaccinated, the federal government's <a href='https://www.theguardian.com/news/datablog/2021/feb/28/is-australias-goal-of-vaccinating-the-entire-adult-population-by-october-achievable' target='_blank'>original rollout goal</a>, and theshholds for 70, 80 and 90% of the 16+ population; and a <b style="color:rgb(245, 189, 44)">trend</b> based on the current seven-day average of first doses per day and the lag time between first and second dose numbers. Last updated {display_date}<br>""",
                "footnote": "",
                "source": "| Sources: Covidlive.com.au, Department of Health 14 March 2021 COVID-19 vaccine rollout update",
                "dateFormat": "%Y-%m-%d",
                "yScaleType":"",
                "xAxisLabel": "Date",
                "yAxisLabel": "Second doses",
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
    periods = []
    labels = []
    df.fillna("", inplace=True)
    chartData = df.to_dict('records')
    # labels = [{"x":f"{end_date_label}", "y":f"{eighty_goal}", "offset":30,
    # "text":f"{eighty_goal_text}",
    #  "align":"right", "direction":"left"},
    #  {"x":f"{seventy_end_date_label}", "y":f"{seventy_goal}", "offset":30,
    #  "text":f"{seventy_goal_text}",
    #   "align":"right", "direction":"left"}]


    yachtCharter(template=template, labels=labels, data=chartData, chartId=[{"type":"linechart"}],
    options=[{"colorScheme":"guardian", "lineLabelling":"TRUE"}], chartName=f"oz_vaccine_tracker_goals_trend_five_trend{test}")

makeTestingLine(combo)
