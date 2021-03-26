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

chart_truncate =  datetime.date(2021, 4, 30)

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

latest_count = oz[-1:]['VACC_DOSE_CNT'].values[0]
last_date = oz.iloc[-1:]["REPORT_DATE"].dt.strftime("%Y-%m-%d").values[0]
oz = oz[['REPORT_DATE', 'VACC_DOSE_CNT']]

## Merge current vaccine total with goal dataframes
combo = pd.merge(combo_targets, oz, left_on="Date", right_on="REPORT_DATE", how="left")

combo.rename(columns={'VACC_DOSE_CNT': "Doses given"}, inplace=True)

combo = combo.sort_values(by="Date", ascending=True)

## Truncate dataset at the end of April
combo = combo.loc[combo['Date'] <= np.datetime64(chart_truncate)]

## Work out goals at cutoff
goal_1 = round(int(combo.loc[combo['Date'] == np.datetime64(chart_truncate)]['Original goal'].values[0]), -3)
goal_2 = round(int(combo.loc[combo['Date'] == np.datetime64(chart_truncate)]["Second goal"].values[0]), -3)

# Work out vaccination gap
# combo['Vaccination gap'] = combo["Original goal"] - combo['Doses given']
combo['Vaccination gap'] = combo["Second goal"] - combo['Doses given']
latest_gap = combo.loc[combo["REPORT_DATE"] == last_date]['Vaccination gap'].values[0]
middle_gap = latest_count + latest_gap/2

combo['Date'] = combo['Date'].dt.strftime('%Y-%m-%d')
combo.rename(columns={"Doses given":f"Doses given: {numberFormat(latest_count)}", "Second goal":"Revised goal"}, inplace=True)
# combo.rename(columns={"Original goal":f"Original goal: {numberFormat(goal_1)}"}, inplace=True)
# combo.rename(columns={"Second goal":f"Second goal: {numberFormat(goal_2)}"}, inplace=True)

combo = combo[['Date', f"Doses given: {numberFormat(latest_count)}", f"Original goal", f"Revised goal"]]
# combo = combo[['Date', "Second target needed per day", "Second goal"]]

def makeTestingLine(df):
	
    template = [
            {
                "title": "Tracking the Covid-19 vaccine rollout in Australia",
                "subtitle": f"""Comparing vaccine doses administered with the rate 
                needed for the government's goals. Showing trajectories based on the original goals of 60,000 in the first week, 4m doses by the end of March and the entire adult population vaccinated by October; and the <a href='https://www.health.gov.au/resources/publications/covid-19-vaccine-rollout-update-on-14-march-2021' target='_blank'>revised estimates from the Health Department</a>. Last updated {last_date}""",
                "footnote": "",
                "source": "| Sources: Covidlive.com.au, Department of Health 14 March 2021 COVID-19 vaccine rollout update",
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
    # labels = []
    df.fillna("", inplace=True)
    chartData = df.to_dict('records')
    labels = [
    {"x":"2021-02-28", "y":sixty_k_doses, "offset":100, 
    "text":"First week goal was 60,000, we managed 31,000", "align":"right", "direction":"top"}, 
    {"x":f"{last_date}", "y":f"{middle_gap}", "offset":190, 
    "text":f"Current gap is {numberFormat(latest_gap)}",
     "align":"middle", "direction":"right"},
    {"x": "2021-03-30", "y": 4000000, "offset": 50,
    "text": "Original goal of 4m doses by end of March",
    "align":"left", "direction":"top"
    }]


    yachtCharter(template=template, labels=labels, data=chartData, chartId=[{"type":"linechart"}], 
    options=[{"colorScheme":"guardian", "lineLabelling":"TRUE"}], chartName="Covid_oz_vac_gap_two_goals_feed")

makeTestingLine(combo)