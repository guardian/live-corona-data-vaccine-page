from modules.yachtCharter import yachtCharter
from modules.numberFormat import numberFormat
import pandas as pd
import datetime
import numpy as np
import os, ssl
pd.set_option("display.max_rows", None, "display.max_columns", None)

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

oz_json = 'https://interactive.guim.co.uk/2021/02/coronavirus-widget-data/aus-vaccines.json'

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

oz = oz[['REPORT_DATE', 'PREV_VACC_PEOPLE_CNT']]

#%%
### APPEND GOALS TO DUMMY DATASET

dummy_vals = [x for x in range(0, 400)]

dummy_date = '2021-02-22'

dummy_df = pd.DataFrame({"Units":1,
                "Date": pd.date_range(start=dummy_date, periods=len(dummy_vals))})


dummy_df = dummy_df.loc[dummy_df['Date'] >= "2021-02-22"]



dummy_combo = pd.merge(dummy_df, original_target, left_on="Date", right_on="Date", how="left")

## Merge current vaccine total with goal dataframes
combo = pd.merge(dummy_combo, oz, left_on="Date", right_on="REPORT_DATE", how="left")

combo.rename(columns={'PREV_VACC_PEOPLE_CNT': "Fully vaccinated"}, inplace=True)

combo = combo.sort_values(by="Date", ascending=True)

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

latest_average = averager[-1:][f'{how_many_days} day rolling average'].values[0]
# print(latest_average)


combo['Trend'] = combo['Incremental']
combo.loc[combo['Date'] == first_date, 'Trend'] = 20
combo.loc[combo['Date'] >= last_date, 'Trend'] = latest_average
combo['Trend'] = round(combo['Trend'].cumsum())
combo.loc[combo['Date'] < last_date, 'Trend'] = np.nan


### WORK OUT TIME TO 80% OF 16+

over_16 = 20619959

eighty = over_16*0.8

combo['80% vaxxed'] = combo['Trend']
combo.loc[combo['80% vaxxed'] > eighty, '80% vaxxed'] = np.nan


goal = over_16 * 0.8

rollout_begin = datetime.date(2021, 2, 22)
today = datetime.datetime.today().date()

days_running = today - rollout_begin
days_running = days_running.days

# Work out number of days to finish given latest average
num_days = round((goal-latest_count)/latest_average)

end_date = today + datetime.timedelta(days=num_days)

months_to_go = (end_date.year - today.year) * 12 + end_date.month - today.month

end_date_formated = datetime.datetime.strftime(end_date, "%d/%m/%Y")


### WORK OUT 80% AND 70% BY EOY

eighty_goal = goal

eighty_doses_so_far = combo.loc[combo["Date"] == "2021-07-28"][f"Fully vaccinated: {numberFormat(latest_count)}"].values[0]

eighty_doses_left = eighty_goal - eighty_doses_so_far

eighty_days = datetime.date(2021, 12, 31) - datetime.date(2021, 7, 30)
eighty_days = eighty_days.days

eighty_eoy = eighty_doses_left / eighty_days

# print(eighty_eoy)

combo['80% by EOY'] = combo['Incremental']
combo.loc[combo['Date'] >= "2021-07-28", '80% by EOY'] = eighty_eoy

combo['80% by EOY'] = combo['80% by EOY'].cumsum()

combo.loc[combo['Date'] < "2021-07-28", '80% by EOY'] = np.nan



seventy_goal = (over_16)*0.7

seventy_doses_so_far = combo.loc[combo["Date"] == "2021-07-28"][f"Fully vaccinated: {numberFormat(latest_count)}"].values[0]

seventy_doses_left = seventy_goal - seventy_doses_so_far

seventy_days = datetime.date(2021, 12, 31) - datetime.date(2021, 7, 30)
seventy_days = seventy_days.days

seventy_eoy = seventy_doses_left / seventy_days


combo['70% by EOY'] = combo['Incremental']
combo.loc[combo['Date'] >= "2021-07-28", '70% by EOY'] = seventy_eoy

combo['70% by EOY'] = combo['70% by EOY'].cumsum()

combo.loc[combo['Date'] < "2021-07-28", '70% by EOY'] = np.nan

combo = combo[['Date', 'Original goal', '80% vaxxed', '80% by EOY', '70% by EOY', f"Fully vaccinated: {numberFormat(latest_count)}"]]
combo.columns = ['Date', 'Original goal', 'Trend', '80% by EOY', '70% by EOY', f"Fully vaccinated: {numberFormat(latest_count)}"]

# print(combo)

display_date = datetime.datetime.strptime(last_date, "%Y-%m-%d")
display_date = datetime.datetime.strftime(display_date, "%d/%m/%Y")

# print(combo)
# print(combo)



chart_truncate = end_date + datetime.timedelta(days=31)

combo['Date'] = pd.to_datetime(combo['Date'])

combo = combo.loc[combo['Date'] <= np.datetime64(chart_truncate)]

combo['Date'] = combo['Date'].dt.strftime('%Y-%m-%d')

def makeTestingLine(df):

    template = [
            {
                "title": "Tracking the Covid-19 vaccine rollout in Australia",
                "subtitle": f"""Showing Australians getting second doses, the federal government's <a href='https://www.theguardian.com/news/datablog/2021/feb/28/is-australias-goal-of-vaccinating-the-entire-adult-population-by-october-achievable' target='_blank'>original rollout goal</a> and thresholds for opening up.
                At the 7 day rolling average of {numberFormat(latest_average)} second doses per day, Australia will vaccinate 80% of the 16+ population <b style="color:rgb(245, 189, 44)">around {end_date_formated}</b>. <br>
                <small>Last updated {display_date}.</small>""",
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
    # labels = [{"x":f"{last_date}", "y":f"{middle_gap}", "offset":50,
    # "text":f"Current gap is {numberFormat(latest_gap)}",
    #  "align":"right", "direction":"right"}]

    yachtCharter(template=template, labels=labels, data=chartData, chartId=[{"type":"linechart"}],
    options=[{"colorScheme":"guardian", "lineLabelling":"TRUE"}], chartName=f"oz_vaccine_tracker_goals_trend_five_trend{test}")

makeTestingLine(combo)
