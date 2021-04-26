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

rollout_begin = datetime.date(2021, 2, 22)
rollout_end = datetime.date(2021, 10, 31)

# chart_truncate =  datetime.date(2021, 5, 31)
chart_truncate =  datetime.date(2021, 6, 30)

### ORIGINAL GOAL

## Dose counts

onea_doses = 1400000
oneb_doses = 14800000

twoa_doses = 15800000
twob_doses = 6600000 * 2

two_doses = twoa_doses + twob_doses

## Readjust doses for changing goals

sixty_k_doses = 60000
four_mil_doses = 4000000 - sixty_k_doses
oneb_doses = oneb_doses + onea_doses - four_mil_doses - sixty_k_doses

# Set out timelines

sixty_end = rollout_begin + datetime.timedelta(days=7)
sixty_delta = 7

four_mil_end = datetime.date(2021, 3, 31)
four_mil_delta = four_mil_end - sixty_end
four_mil_delta  = four_mil_delta.days

oneb_begin = four_mil_end + datetime.timedelta(days=1)
oneb_end = datetime.date(2021, 5, 31)
oneb_delta = oneb_end - oneb_begin
oneb_delta = oneb_delta.days

two_begin = oneb_end + datetime.timedelta(days=1)
two_end = rollout_end

two_delta = two_end - two_begin
two_delta = two_delta.days

# Call function

original_rollout = [(sixty_k_doses, sixty_delta), (four_mil_doses, four_mil_delta),
(oneb_doses, oneb_delta), (two_doses, two_delta)]

original_target = second_builder(rollout_begin, original_rollout, "Original")

### SECOND GOAL
#source for following: https://www.health.gov.au/resources/publications/covid-19-vaccine-rollout-update-on-14-march-2021

# Deltas are the number of days to the end of that week from the end of the previous target
week_1_delta = 7
week_1_target = 60000

week_2_delta = 7
week_2_target = 120000 - week_1_target

week_4_delta = 14
week_4_target = 1000000 - week_2_target - week_1_target

week_6_delta = 14
week_6_target = 2000000 - week_4_target - week_2_target - week_1_target

week_8_delta = 14
week_8_target = 3000000 - week_6_target - week_4_target - week_2_target - week_1_target

week_10_delta = 14
week_10_target = 4500000 - week_8_target - week_6_target - week_4_target - week_2_target - week_1_target

second_target_rollout = [(week_1_target, week_1_delta), (week_2_target, week_2_delta), (week_4_target, week_4_delta),
(week_6_target, week_6_delta), (week_8_target, week_8_delta), (week_10_target, week_10_delta)]

# Call function

second_target = second_builder(rollout_begin, second_target_rollout, "Second")

second_target['Date'] = pd.to_datetime(second_target['Date'])

# Combine two target lines

combo_targets = pd.merge(original_target, second_target, on="Date", how="left")

## READ IN ACTUAL VACCINATIONS

oz = pd.read_json(oz_json)
oz['REPORT_DATE'] = pd.to_datetime(oz['REPORT_DATE'])
oz = oz.sort_values(by="REPORT_DATE", ascending=True)

## Calculate latest count

latest_count = oz['VACC_DOSE_CNT'].max()
last_date = datetime.datetime.strftime(oz['REPORT_DATE'].max(), "%Y-%m-%d")
first_date = datetime.datetime.strftime(oz['REPORT_DATE'].min(), "%Y-%m-%d")

oz = oz[['REPORT_DATE', 'PREV_VACC_DOSE_CNT']]

## Merge current vaccine total with goal dataframes
combo = pd.merge(combo_targets, oz, left_on="Date", right_on="REPORT_DATE", how="left")

combo.rename(columns={'PREV_VACC_DOSE_CNT': "Doses given"}, inplace=True)

combo = combo.sort_values(by="Date", ascending=True)

## Work out goals at cutoff
goal_1 = round(int(combo.loc[combo['Date'] == np.datetime64(chart_truncate)]['Original goal'].values[0]), -3)
# goal_2 = round(int(combo.loc[combo['Date'] == np.datetime64(chart_truncate)]["Second goal"].values[0]), -3)

# Work out vaccination gap
# combo['Vaccination gap'] = combo["Original goal"] - combo['Doses given']
combo['Vaccination gap'] = combo["Second goal"] - combo['Doses given']
latest_gap = combo.loc[combo["REPORT_DATE"] == last_date]['Vaccination gap'].values[0]
middle_gap = latest_count + latest_gap/2

## Truncate dataset at the end of April
combo = combo.loc[combo['Date'] <= np.datetime64(chart_truncate)]

combo['Date'] = combo['Date'].dt.strftime('%Y-%m-%d')
combo.rename(columns={"Doses given":f"Doses given: {numberFormat(latest_count)}", "Second goal":"Revised rollout"}, inplace=True)
# combo.rename(columns={"Original goal":f"Original goal: {numberFormat(goal_1)}"}, inplace=True)
# combo.rename(columns={"Second goal":f"Second goal: {numberFormat(goal_2)}"}, inplace=True)



combo = combo[['Date', f"Doses given: {numberFormat(latest_count)}", f"Original goal", f"Revised rollout"]]

## Work out rolling average

how_many_days = 7

combo['Incremental'] = combo[f"Doses given: {numberFormat(latest_count)}"].diff(periods=1)
combo[f'{how_many_days} day rolling average'] = combo['Incremental'].rolling(how_many_days).mean()

# print(combo)

## Get latest rolling average and use it to extrapolate trend
averager = combo.dropna()
latest_average = averager[-1:][f'{how_many_days} day rolling average'].values[0]

combo['Trend'] = combo['Incremental']
combo.loc[combo['Date'] == first_date, 'Trend'] = 20
combo.loc[combo['Date'] > last_date, 'Trend'] = latest_average
combo['Trend'] = round(combo['Trend'].cumsum())
combo.loc[combo['Date'] < last_date, 'Trend'] = np.nan


# # Work out herd immunity
# # source: https://www.abs.gov.au/statistics/people/population/national-state-and-territory-population/sep-2020
# oz_pop = 25693.1 * 1000
# herd_immunity = (oz_pop*2) * 0.85

# rollout_begin = datetime.date(2021, 2, 22)
# today = datetime.datetime.today().date()

# days_running = today - rollout_begin
# days_running = days_running.days


# num_days = (herd_immunity-latest_count)/latest_average
# # num_days =  round(num_days - days_running)

# end_date = today + datetime.timedelta(days=num_days)
# months_to_go = (end_date.year - today.year) * 12 + end_date.month - today.month

# Work out time to 45 million
goal = 45000000

rollout_begin = datetime.date(2021, 2, 22)
today = datetime.datetime.today().date()

days_running = today - rollout_begin
days_running = days_running.days

# Work out number of days to finish given latest average
num_days = round((goal-latest_count)/latest_average)

end_date = today + datetime.timedelta(days=num_days)
months_to_go = (end_date.year - today.year) * 12 + end_date.month - today.month

# combo = combo[['Date', f"Doses given: {numberFormat(latest_count)}", 'Original goal', 'Revised rollout','Trend']]

# print(combo)

### Work out trendline for first vaccines by EOY

first_goal = 22500000

eoy_days = datetime.date(2021, 12, 31) - rollout_begin
eoy_days = eoy_days.days

first_doses_per_day_eoy = first_goal / eoy_days

# print(first_doses_per_day_eoy)

til_nov_one = datetime.date(2021, 11, 1) - rollout_begin
til_nov_one = til_nov_one.days

second_doses_til_nov_one = first_doses_per_day_eoy * til_nov_one

doses_left = (first_goal + second_doses_til_nov_one) - latest_count

daily_til_year_end = doses_left / (eoy_days - days_running)

combo['First dose by EOY'] = round(daily_til_year_end)

combo.loc[combo['Date'] <= last_date, 'First dose by EOY'] = combo['Incremental']

combo['First dose by EOY'] = combo['First dose by EOY'].cumsum()

combo.loc[combo['Date'] < last_date, 'First dose by EOY'] = np.nan

combo = combo[['Date', f"Doses given: {numberFormat(latest_count)}", 'Original goal', 'First dose by EOY', 'Revised rollout','Trend']]
# combo = combo[['Date', f"Doses given: {numberFormat(latest_count)}", 'First dose by EOY','Trend']]

display_date = datetime.datetime.strptime(last_date, "%Y-%m-%d")
display_date = datetime.datetime.strftime(display_date, "%d/%m/%Y")

def makeTestingLine(df):

    template = [
            {
                "title": "Tracking the Covid-19 vaccine rollout in Australia",
                "subtitle": f"""Showing doses administered as well as the federal government's <a href='https://www.theguardian.com/news/datablog/2021/feb/28/is-australias-goal-of-vaccinating-the-entire-adult-population-by-october-achievable' target='_blank'>original</a> and <a href='https://www.health.gov.au/resources/publications/covid-19-vaccine-rollout-update-on-14-march-2021' target='_blank'>revised</a> goals.<br>
                At the 7 day rolling average of {numberFormat(latest_average)} doses, <strong>it will take <red>{months_to_go}</red> more months</strong> to administer 45m doses. <br>
                <small>Last updated {display_date}.</small>""",
                "footnote": "",
                "source": "Covidlive.com.au, Department of Health 14 March 2021 COVID-19 vaccine rollout update",
                "dateFormat": "%Y-%m-%d",
                "yScaleType":"",
                "xAxisLabel": "Date",
                "yAxisLabel": "Cumulative vaccinations",
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
    options=[{"colorScheme":"guardian", "lineLabelling":"TRUE"}], chartName="oz_vaccine_tracker_goals_trend_two_trend_test")

makeTestingLine(combo)
