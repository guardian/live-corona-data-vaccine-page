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

test = "_test"
# test = ""

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
# chart_truncate =  datetime.date(2021, 7, 31)
chart_truncate =  datetime.date(2022, 1, 31)



######### ORIGINAL GOAL



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




######### READ IN ACTUAL VACCINATIONS



oz = pd.read_json(oz_json)
oz['REPORT_DATE'] = pd.to_datetime(oz['REPORT_DATE'])
oz = oz.sort_values(by="REPORT_DATE", ascending=True)

## Calculate latest count

latest_count = oz['VACC_DOSE_CNT'].max()
last_date = datetime.datetime.strftime(oz['REPORT_DATE'].max(), "%Y-%m-%d")
first_date = datetime.datetime.strftime(oz['REPORT_DATE'].min(), "%Y-%m-%d")

oz = oz[['REPORT_DATE', 'PREV_VACC_DOSE_CNT']]


######### APPEND GOALS TO DUMMY DATASET

dummy_vals = [x for x in range(0, 400)]

dummy_date = '2021-02-22'

dummy_df = pd.DataFrame({"Units":1,
                "Date": pd.date_range(start=dummy_date, periods=len(dummy_vals))})


dummy_df = dummy_df.loc[dummy_df['Date'] >= "2021-02-22"]

dummy_combo = pd.merge(dummy_df, original_target, left_on="Date", right_on="Date", how="left")

## Merge current vaccine total with goal dataframes
combo = pd.merge(dummy_combo, oz, left_on="Date", right_on="REPORT_DATE", how="left")

combo.rename(columns={'PREV_VACC_DOSE_CNT': "Doses given"}, inplace=True)

combo = combo.sort_values(by="Date", ascending=True)

## Truncate dataset
combo = combo.loc[combo['Date'] <= np.datetime64(chart_truncate)]

combo['Date'] = combo['Date'].dt.strftime('%Y-%m-%d')
combo.rename(columns={"Doses given":f"Doses given: {numberFormat(latest_count)}"}, inplace=True)

combo = combo[['Date', f"Doses given: {numberFormat(latest_count)}", f"Original goal"]]




####### WORK OUT NEW 80% AND 70% GOAL LINES

over_16 = 20619959

seventy = (over_16 * 2)*0.7

eighty = (over_16 * 2)*0.8

how_many_days = 7

combo['Incremental'] = combo[f"Doses given: {numberFormat(latest_count)}"].diff(periods=1)
combo[f'{how_many_days} day rolling average'] = combo['Incremental'].rolling(how_many_days).mean()

## Get latest rolling average and use it to extrapolate trend
averager = combo.dropna()
averager = combo.loc[~combo[f"Doses given: {numberFormat(latest_count)}"].isna()]
## THIS IS WHERE I FIXED TO CORRECT THE MOVING AVERAGE

latest_average = averager[-1:][f'{how_many_days} day rolling average'].values[0]
# print(latest_average)

combo['Trend'] = combo['Incremental']
combo.loc[combo['Date'] == first_date, 'Trend'] = 20
combo.loc[combo['Date'] >= last_date, 'Trend'] = latest_average
combo['Trend'] = round(combo['Trend'].cumsum())
combo.loc[combo['Date'] < last_date, 'Trend'] = np.nan

combo['80% vaxxed'] = combo['Trend']
combo.loc[combo['80% vaxxed'] > eighty, '80% vaxxed'] = np.nan


# combo['70% vaxxed'] = combo['Trend']
# combo.loc[combo['70% vaxxed'] > seventy, '70% vaxxed'] = np.nan

# combo['Fully vaxxed'] = combo['Trend']
# combo.loc[combo['Fully vaxxed'] > (over_16*2), 'Fully vaxxed'] = np.nan


print(combo)

# print(combo)




goal = (20619959 * 2)

rollout_begin = datetime.date(2021, 2, 22)
today = datetime.datetime.today().date()

days_running = today - rollout_begin
days_running = days_running.days

# Work out number of days to finish given latest average
num_days = round((goal-latest_count)/latest_average)

end_date = today + datetime.timedelta(days=num_days)
months_to_go = (end_date.year - today.year) * 12 + end_date.month - today.month


combo = combo[['Date', f"Doses given: {numberFormat(latest_count)}", 'Original goal','80% vaxxed']]
# combo = combo[['Date', f"Doses given: {numberFormat(latest_count)}", 'Original goal','80% vaxxed', '70% vaxxed', 'Fully vaxxed']]
# combo.columns = ['Date', f"Doses given: {numberFormat(latest_count)}", 'Original goal', 'Trend']

# print(combo.loc[combo['Trend'] == combo['Trend'].min()])

# combo = combo[['Date', f"Doses given: {numberFormat(latest_count)}", 'First dose by EOY','Trend']]

display_date = datetime.datetime.strptime(last_date, "%Y-%m-%d")
display_date = datetime.datetime.strftime(display_date, "%d/%m/%Y")

# print(combo)

def makeTestingLine(df):

    template = [
            {
                "title": "Tracking the Covid-19 vaccine rollout in Australia",
                "subtitle": f"""Showing doses administered as well as the federal government's <a href='https://www.theguardian.com/news/datablog/2021/feb/28/is-australias-goal-of-vaccinating-the-entire-adult-population-by-october-achievable' target='_blank'>original</a> and <a href='https://www.pm.gov.au/media/press-conference-canberra-act-8' target='_blank'>revised</a> goals.<br>
                At the 7 day rolling average of {numberFormat(latest_average)} doses, <strong>it will take <red>{months_to_go}</red> more months</strong> to vaccinate everyone over 16. <br>
                The current vaccination gap is <b style="color:rgb(245, 189, 44)">doses</b>.<br>
                <small>Last updated {display_date}.</small>""",
                "footnote": "Current goal is calculated as a first dose for every Australian by the end of the year. Calculation starts as of the Prime Minister's press conference on the 15th of April. Target includes a second dose for those who receive their first shot before the 1st of October.",
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
    labels = []
    df.fillna("", inplace=True)
    chartData = df.to_dict('records')
    # labels = [{"x":f"{last_date}", "y":f"{middle_gap}", "offset":50,
    # "text":f"Current gap is {numberFormat(latest_gap)}",
    #  "align":"right", "direction":"right"}]

    yachtCharter(template=template, labels=labels, data=chartData, chartId=[{"type":"linechart"}],
    options=[{"colorScheme":"guardian", "lineLabelling":"TRUE"}], chartName=f"oz_vaccine_tracker_goals_trend_four_trend{test}")

makeTestingLine(combo)
