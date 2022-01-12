#%%

from numpy import short
import pandas as pd 
from modules.syncData import syncData
import datetime 
import pytz
import json 

yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
yesterday = yesterday.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y-%m-%d')

#%%

sixteen_pop = {
    'NT':190571, 'NSW':6565651, 'VIC':5407574,
    'QLD':4112707, 'ACT':344037,
    'SA':1440400, 'WA':2114978, 'TAS':440172, "AUS":20619959}

twelve_pop = {
    'NT':190571 + 13060, 'NSW':6565651 + 390330, 
    'VIC':5407574 + 308611,
    'QLD':4112707 + 141934 , 'ACT':344037 + 18930 ,
    'SA':1440400 + 82747, 'WA':2114978 + 132869,
     'TAS':440172 + 26308 , "AUS":20619959 + 1243990}

cases = pd.read_csv('https://raw.githubusercontent.com/joshnicholas/oz-covid-data/main/output/total_cases.csv')
cases = cases.loc[cases['Date'] <= yesterday]
# 'Jurisdiction', 'Overseas', 'Locally acquired - contact of confirmed case',
# 'Locally acquired - unknown contact*', 'Locally acquired - interstate travel', 
# 'Under investigation*', 'Total cases', 'Total deaths', 
# 'Date', 'Locally acquired - unknown contact', 'Under investigation'

hospo = pd.read_csv('https://raw.githubusercontent.com/joshnicholas/oz-covid-data/main/output/hospitalisations.csv')
hospo = hospo.loc[hospo['Date'] <= yesterday]
# 'Jurisdiction', 'Not in ICU', 'ICU', 'Date'

recent = pd.read_csv('https://raw.githubusercontent.com/joshnicholas/oz-covid-data/main/output/recent_cases.csv')
recent = recent.loc[recent['Date'] <= yesterday]
# 'Jurisdiction', 'Active cases^', 'Locally acquired last 24 hours*', 
# 'Overseas acquired last 24 hours', "'Under investigation last 24 hours*'",
#  'Locally acquired last 7 days', 'Overseas acquired last 7 days', 
#  'Under investigation last 7 days', 'Date', 
# 'Locally acquired last 24 hours', 'Under investigation last 24 hours'



#%%
## Cases first

# listo = []

# for juri in cases['Jurisdiction'].unique().tolist():
#     inter = cases.loc[cases['Jurisdiction'] == juri].copy()
#     inter['New cases'] = inter['Total cases'].diff(1)

#     listo.append(inter)

#     cases = pd.concat(listo)

cases = cases[['Jurisdiction','Total cases', 'Date']]


## Then hospitalisations

hospo['Hospitalised'] = hospo['Not in ICU'] + hospo['ICU']
hospo = hospo[['Jurisdiction', 'Date', 'Hospitalised']]

## Then recents
# recent = recent.loc[recent['Date'] == yesterday]
recent['New cases'] = recent['Locally acquired last 24 hours*'] + recent['Overseas acquired last 24 hours'] + recent["'Under investigation last 24 hours*'"]
recent = recent[['Jurisdiction', 'Date', 'Active cases^', 'New cases']]
recent.columns = ['Jurisdiction', 'Date', 'Active cases', 'New cases']

#%%

### Bring together Health dept data

combo = pd.merge(cases, hospo, on=['Jurisdiction', 'Date'])
combo = pd.merge(combo, recent, on=['Jurisdiction', 'Date'])

combo.loc[combo['Jurisdiction'] == 'Australia', 'Jurisdiction'] = "AUS"


#%%

### Read in Vaccine data from Ken


url = 'https://vaccinedata.covid19nearme.com.au/data/air.json'

air = pd.read_json(url)

#%%

states =['NSW','VIC','QLD','WA','SA','TAS','NT','ACT','AUS']
short_cols = ['DATE_AS_AT']

for state in states:


    if state == "AUS":
        
        air[f"Two_doses_12+"] = round((((air[f'AIR_12_15_SECOND_DOSE_COUNT'] + air[f'AIR_AUS_16_PLUS_SECOND_DOSE_COUNT'])/twelve_pop[state]) * 100), 2)
        short_cols.append(f"Two_doses_12+")

        # air.rename(columns={f"AIR_AUS_16_PLUS_THIRD_DOSE_COUNT":'AUS_third_16+'}, inplace=True)
        air['Boosters_16+'] = round((((air[f"AIR_AUS_16_PLUS_THIRD_DOSE_COUNT"])/sixteen_pop[state]) * 100), 2)
        short_cols.append('Boosters_16+')
        # short_cols.append("AIR_AUS_16_PLUS_THIRD_DOSE_COUNT")

    # if state != "AUS":
    #     air[f"{state}_second_12+"] = round((((air[f'AIR_{state}_12_15_SECOND_DOSE_COUNT'] + air[f'AIR_{state}_16_PLUS_SECOND_DOSE_COUNT'])/twelve_pop[state]) * 100), 2)
    #     short_cols.append(f"{state}_second_12+")


z_air = air[short_cols]
z_air['Jurisdiction'] = "AUS"

z_air.rename(columns={f"DATE_AS_AT":'Date'}, inplace=True)
z_air['Date'] = pd.to_datetime(z_air['Date'])
z_air['Date'] = z_air['Date'].dt.strftime("%Y-%m-%d")


#%%


### BRING ALL TOGETHER

combo = pd.merge(combo, z_air, on=['Jurisdiction', 'Date'], how='left')


#%%

## Work out cases in the past two weeks

fin = combo.copy()

oz = fin.loc[fin['Jurisdiction'] == "AUS"].copy()

two_doses = oz['Two_doses_12+'].max()
boosters = oz['Boosters_16+'].max()
hospital = oz['Hospitalised'].values[-1]

updated = oz['Date'].max()

states =['NSW','VIC','QLD','WA','SA','TAS','NT','ACT', "AUS"]
import numpy as np
listo = []

feed = []

fin['Hospitalised'] = fin['Hospitalised'].astype(float)

for state in states:
    inter = fin.loc[fin['Jurisdiction'] == state].copy()
    inter['Cases_last_14'] = inter['New cases'].rolling(window=14).sum()
    inter.loc[np.isnan(inter['Cases_last_14']), 'Cases_last_14'] = 0
    inter['Change_14'] = inter['Cases_last_14'].diff(14)

    inter.loc[inter['Change_14'] < 0, 'Change_14_status'] = 'Decreasing'
    inter.loc[inter['Change_14'] > 0, 'Change_14_status'] = 'Increasing'

    latest = inter.loc[inter['Date'] == inter['Date'].max()]

    feed.append([ state + "_cases_last_14", latest['Cases_last_14'].values[-1]])

    feed.append([ state + "_status" , latest['Change_14_status'].values[-1]])

    feed.append([ state + "_hospitalised" , latest['Hospitalised'].values[-1]])


# feed.append(["HOSPITAL" , hospital ])

feed.append(['Fully_vaccinated_12+', two_doses])

feed.append(['BOOSTERS', boosters])

feed.append(["UPDATED" , updated ])


consolidated = {}
for row in feed:
    consolidated[row[0]] = row[1]
    print(row)



boom = json.dumps(consolidated)

syncData(boom, "2021/06/coronavirus-thrasher-data", "thrasher-health-scrape-data.json")
