from modules.yachtCharter import yachtCharter
from modules.numberFormat import numberFormat
import pandas as pd 
import datetime 
import numpy as np 
import os, ssl

print("Updating vaccine goals chart")

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

oz_json = 'https://interactive.guim.co.uk/2021/02/coronavirus-widget-data/aus-vaccines.json'

## Dose counts
onea_doses = 1400000
oneb_doses = 14800000

twoa_doses = 15800000
twob_doses = 6600000 * 2

two_doses = twoa_doses + twob_doses

print(f"Total: {onea_doses + oneb_doses + two_doses}")

rollout_begin = datetime.date(2021, 2, 22)
rollout_end = datetime.date(2021, 10, 31)

## Start date of phases
onea_begin = rollout_begin
oneb_begin = datetime.date(2021, 3, 31)
two_begin = datetime.date(2021, 3, 31)

## End date of phases 
onea_end = datetime.date(2021, 4, 30)
oneb_end = datetime.date(2021, 5, 31)
two_end = rollout_end

## Deltas between start and end
onea_delta = onea_end - onea_begin
onea_delta = onea_delta.days

oneb_delta = oneb_end - oneb_begin
oneb_delta = oneb_delta.days

two_delta = two_end - two_begin
two_delta = two_delta.days


phases = [["onea", onea_doses, onea_begin, onea_end, onea_delta], 
        ["oneb", oneb_doses, oneb_begin, oneb_end, oneb_delta], 
        ["two", two_doses, two_begin, two_end, two_delta]]

# phases = [["onea", onea_doses, onea_begin, onea_end, onea_delta]]


oz = pd.read_json(oz_json)
oz['REPORT_DATE'] = pd.to_datetime(oz['REPORT_DATE'])
oz = oz.sort_values(by="REPORT_DATE", ascending=True)

latest_count = oz[-1:]['VACC_DOSE_CNT'].values[0]
last_date = str(oz[-1:]["LAST_UPDATED_DATE"].values[0])
last_date = datetime.datetime.strptime(last_date, "%Y-%m-%d %H:%M:%S")
last_date = last_date.strftime("%Y-%m-%d")

oz = oz[['REPORT_DATE', 'VACC_DOSE_CNT']]

def create_frame(listo):
    ## Divide total doses for phase by number of days in phase range
    divided = [round(listo[1]/listo[4]) for x in range(0, listo[4])]
    ## Create list of dates for each day in phase range
    daterange = [listo[2] + datetime.timedelta(days=x) for x in range(0, listo[4])]
    ## Combine lists
    zipped = list(zip(daterange, divided))
    ## Create pandas dataframe from combined lists
    inter = pd.DataFrame(zipped)
    ## Add name of phase
    inter['Phase'] = listo[0]
    ## Rename columns
    inter.rename(columns={0:"Date", 1:"Vaccines needed per day"}, inplace=True)
    return inter

# Iterate through phases and call function on each one
listo = [create_frame(x) for x in phases]

# Combine into dataframe
combined_phases = pd.concat(listo)
combined_phases['Date'] = pd.to_datetime(combined_phases['Date'])

combined_phases = combined_phases.groupby(['Date'])['Vaccines needed per day'].sum().reset_index()

## Add current Oz vaccine total to dataframe
combo = pd.merge(combined_phases, oz, left_on="Date", right_on="REPORT_DATE", how="left")

combo['Phase 1a target'] = combo['Vaccines needed per day'].cumsum()
combo.rename(columns={'VACC_DOSE_CNT': "Doses given"}, inplace=True)

combo = combo.sort_values(by="Date", ascending=True)
combo['Date'] = combo['Date'].dt.strftime('%Y-%m-%d')

## Work out vaccination gap
combo['Vaccination gap'] = combo['Phase 1a target'] - combo['Doses given']
combo['Vaccination gap'] = combo['Vaccination gap'].cumsum()

# print(combo)

combo.rename(columns={"Doses given":f"Doses given: {numberFormat(latest_count)}"}, inplace=True)
combo = combo[['Date', f"Doses given: {numberFormat(latest_count)}", 'Phase 1a target']]


# pd.set_option("display.max_rows", None, "display.max_columns", None)
# print(combo)

def makeTestingLine(df):
	
    template = [
            {
                "title": "Tracking the Covid-19 vaccine rollout in Australia",
                "subtitle": f"Comparing the number of vaccine doses per day with the rate needed to meet the government's goals. Last updated {last_date }",
                "footnote": "",
                "source": "Covidlive.com.au, Department of Health",
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

    yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], 
    options=[{"colorScheme":"guardian", "lineLabelling":"TRUE"}], chartName="Covid-19_oz_vaccine_tracker_all_phases")

makeTestingLine(combo)
