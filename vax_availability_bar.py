#%%

from modules.yachtCharter import yachtCharter
from modules.numberFormat import numberFormat
import pandas as pd
import datetime
import numpy as np
import os, ssl

#%%

## Work out previous vaccine doses available


previous_vaccines = {"Date":[datetime.date(2021, 4, 4),datetime.date(2021, 4, 11),
datetime.date(2021, 4, 18),datetime.date(2021, 4, 25),datetime.date(2021, 5, 2),
datetime.date(2021, 5, 9),datetime.date(2021, 5, 16),datetime.date(2021, 5, 23),
datetime.date(2021, 5, 30),datetime.date(2021, 6, 6),datetime.date(2021, 6, 13)], "Available":[
    1905294, 2447865, 3025852, 3601029, 4086946, 4622610, 
    5540846, 6416656, 7168372, 8097906, 9148616]}
prev = pd.DataFrame.from_records(previous_vaccines)
prev['Name'] = "Unknown"

prev['Available'] = prev['Available'].diff(periods=1)



print(prev)

#%%

#### ADDING HORIZONS

# Source: https://www.health.gov.au/sites/default/files/documents/2021/06/covid-19-vaccination-covid-vaccination-allocations-horizons.pdf

## Horizon 1
horizon_one_begin = datetime.date(2021, 7, 1)
horizon_one_end = datetime.date(2021, 8, 31)
horizon_one_delta = horizon_one_end - horizon_one_begin
horizon_one_weeks = round(horizon_one_delta.days/7)
# States:
astra_one = 2200000 
pfizer_one = 650000 
vaccines_one = astra_one + pfizer_one

horizon_one_vaccines = vaccines_one * horizon_one_weeks 
horizon_one_vaccines_per_day = horizon_one_vaccines / horizon_one_delta.days

## Horizon 2
horizon_two_begin = horizon_one_end + datetime.timedelta(days=1)
horizon_two_end = datetime.date(2021, 9, 30)
horizon_two_delta = horizon_two_end - horizon_two_begin
horizon_two_weeks = round(horizon_two_delta.days/7)

astra_two = 880000 
pfizer_two = 930000
moderna_two = 87000

horizon_two_vaccines = (astra_two + pfizer_two + moderna_two) * horizon_two_weeks
horizon_two_vaccines_per_day = horizon_two_vaccines / horizon_two_delta.days

# Horizon 3

horizon_three_begin = horizon_two_end + datetime.timedelta(days=1)
horizon_three_end = datetime.date(2021, 12, 31)
horizon_three_delta = horizon_three_end - horizon_three_begin
horizon_three_weeks = round(horizon_three_delta.days/7)

pfizer_three = 1700000
moderna_three = 430000

horizon_three_vaccines = (pfizer_three + moderna_three) * horizon_three_weeks
horizon_three_vaccines_per_day = horizon_three_vaccines / horizon_three_delta.days

# horizon_rollout = [(astra_one, horizon_one_delta.days + 1, "Astra"), (pfizer_one, horizon_one_delta.days + 1, "Pfizer"), 
# (astra_two, horizon_two_delta.days + 1, "Astra"), (pfizer_two, horizon_two_delta.days + 1, "Pfizer"), (pfizer_three, horizon_two_delta.days + 1, "Moderna"), 
# (pfizer_three, horizon_three_delta.days + 1, "Pfizer"), (moderna_three, horizon_three_delta.days + 1, "Moderna")]

astra = [(horizon_one_begin, horizon_one_end, astra_one, "Astrazeneca"), (horizon_two_begin, horizon_two_end, astra_two,  "Astrazeneca")]
pfizer = [(horizon_one_begin, horizon_one_end , pfizer_one,  "Pfizer"),(horizon_two_begin, horizon_two_end, pfizer_two,  "Pfizer"),
(horizon_three_begin, horizon_three_end, pfizer_three, "Pfizer")]
moderna = [(horizon_two_begin, horizon_two_end, moderna_two,  "Moderna"), (horizon_three_begin, horizon_three_end, moderna_three, "Moderna")]

def fourth_builder(start, end, num_vax, name):

    inter = pd.date_range(start=start, end=end, freq="W")
    inter = inter.to_frame(name="Date", index=False)
    inter['Available'] = num_vax
    inter['Name'] = name

    return inter

moderna = [fourth_builder(x[0], x[1], x[2], x[3]) for x in moderna]
pfizer = [fourth_builder(x[0], x[1], x[2], x[3]) for x in pfizer]
astra = [fourth_builder(x[0], x[1], x[2], x[3]) for x in astra]

moderna = pd.concat(moderna)
pfizer = pd.concat(pfizer)
astra = pd.concat(astra)

combo = moderna.append(pfizer)
combo = combo.append(astra)


combo = combo.append(prev)

combo['Date'] = pd.to_datetime(combo['Date'])
combo = combo.sort_values(by="Date", ascending=True)

pivoted = combo.pivot(index="Date", columns="Name")['Available'].reset_index()
pivoted['Date'] = pivoted['Date'].dt.strftime('%Y-%m-%d')

# print(pivoted)
# print(combo)

# print(combo)


# %%

def makeTestingLine(df):
	
    template = [
            {
                "title": "New vaccine doses available in Australia",
                "subtitle": f"""Showing previous and planned vaccine availability by week""",
                "footnote": "",
                "source": "| Sources: Department of Health Covid Vaccination Allocation Horizons",
                "dateFormat": "%Y-%m-%d",
                "minY": "0",
                "maxY": "",
                "xAxisDateFormat":"%b %d",
                "tooltip":"<strong>{{#formatDate}}{{data.Date}}{{/formatDate}}</strong><br/>{{group}}: {{groupValue}}<br/>Total: {{total}}",
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
    labels = []


    yachtCharter(template=template, labels=labels, data=chartData, chartId=[{"type":"stackedbar"}], chartName="oz-vaccine-availability")

makeTestingLine(pivoted)