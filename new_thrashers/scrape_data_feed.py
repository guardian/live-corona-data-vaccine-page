#%%

from numpy import short
import pandas as pd 
pd.set_option("display.max_columns", 100)
from modules.syncData import syncData
import datetime 
import pytz
import json 

yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
yesterday = yesterday.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y-%m-%d')

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

five_plus = {"AUS":20619959 + 1243990 + 2276638}

#%%

## Read in scrape data

df= pd.read_json('https://interactive.guim.co.uk/2022/01/oz-covid-health-data/cases.json')
# 'REPORT_DATE', 'CODE', 'ACTIVE_CNT', 'CASE_CNT', 
# 'DEATH_CNT', 'TEST_CNT', 'MED_HOSP_CNT', 'MED_ICU_CNT', 
# 'NAME', 'PREV_ACTIVE_CNT', 'PREV_CASE_CNT', 'PREV_DEATH_CNT',
# 'PREV_TEST_CNT', 'PREV_MED_HOSP_CNT', 'PREV_MED_ICU_CNT', 
# 'NEW_CASE_CNT', 'PREV_NEW_CASE_CNT', 'LAST_UPDATED_DATE'

#%%

fin = df.copy()

# ### NEED TO ADJUST THE NATIONAL HOSPITALISATION FIGURES

# fin['MED_HOSP_CNT'] = pd.to_numeric(fin['MED_HOSP_CNT'])

# med = fin[['REPORT_DATE', 'CODE','MED_HOSP_CNT']]

# ## Have to remove hospital column to readd later
# fin = fin[['REPORT_DATE', 'CODE', 'ACTIVE_CNT', 'CASE_CNT',
# 'DEATH_CNT', 'TEST_CNT', 'MED_ICU_CNT',
# 'NAME', 'PREV_ACTIVE_CNT', 'PREV_CASE_CNT',
# 'PREV_DEATH_CNT', 'PREV_TEST_CNT', 'PREV_MED_HOSP_CNT',
# 'PREV_MED_ICU_CNT', 'NEW_CASE_CNT', 'PREV_NEW_CASE_CNT',
# 'LAST_UPDATED_DATE']]

# # print("LENGTHS")
# # print(len(fin))

# ### Create one df from before the change
# bef = med.loc[med['REPORT_DATE'] < "2021-12-20"]

# ## One df from after
# aff = med.loc[med['REPORT_DATE'] > "2021-12-19"]

# ## Exclude nation figures
# oz_aff = aff.loc[aff['CODE'] != "AUS"]

# ## Groupby states and sum to get new national
# grp = oz_aff.groupby(by=['REPORT_DATE'])['MED_HOSP_CNT'].sum().reset_index()
# grp['CODE'] = "AUS"

# ### Add everything back together
# grp = oz_aff.append(grp)

# tog = bef.append(grp)
# tog = tog.sort_values(by=['REPORT_DATE'], ascending=True)

zfin = fin.copy()

# zfin = pd.merge(fin, tog, on=['REPORT_DATE', "CODE"], how='left')



# print(len(zfin))
# p = zfin.loc[zfin['CODE'] == "AUS"]

# print(p)
# print(p.columns.tolist())

# %%


### Read in Vaccine data from Ken


url = 'https://vaccinedata.covid19nearme.com.au/data/air.json'

air = pd.read_json(url)

#%%

### Work out booster eligibility

dair = air.copy()

dair['AIR_AUS_16_PLUS_SECOND_DOSE_COUNT'] = dair['AIR_AUS_16_PLUS_SECOND_DOSE_COUNT'].fillna(0)
dair['AIR_12_15_SECOND_DOSE_COUNT'] = dair['AIR_12_15_SECOND_DOSE_COUNT'].fillna(0)
dair['AIR_AUS_16_PLUS_SECOND_DOSE_COUNT'] = pd.to_numeric(dair['AIR_AUS_16_PLUS_SECOND_DOSE_COUNT'])
dair['AIR_12_15_SECOND_DOSE_COUNT'] = pd.to_numeric(dair['AIR_12_15_SECOND_DOSE_COUNT'])

dair['Second_doses'] = dair['AIR_12_15_SECOND_DOSE_COUNT'] + dair['AIR_AUS_16_PLUS_SECOND_DOSE_COUNT']

dair = dair[['DATE_AS_AT','Second_doses']]
dair['Eligible'] = dair['Second_doses'].shift(120)

print(dair.tail(30))

booster_eligible = round(((dair['Eligible'].max()/five_plus["AUS"]) * 100), 2)


## Work out rest of vax

states =['NSW','VIC','QLD','WA','SA','TAS','NT','ACT','AUS']
short_cols = ['DATE_AS_AT']

for state in states:


    if state == "AUS":
        
        air[f"Two_doses"] = round((((air[f'AIR_12_15_SECOND_DOSE_COUNT'] + air[f'AIR_AUS_16_PLUS_SECOND_DOSE_COUNT'])/five_plus[state]) * 100), 2)
        short_cols.append(f"Two_doses")
        air['Boosters'] = round((((air[f"AIR_AUS_16_PLUS_THIRD_DOSE_COUNT"])/five_plus[state]) * 100), 2)
        short_cols.append('Boosters')


z_air = air[short_cols]
z_air = z_air.copy()
z_air['CODE'] = "AUS"

z_air.rename(columns={f"DATE_AS_AT":'REPORT_DATE'}, inplace=True)
z_air['REPORT_DATE'] = pd.to_datetime(z_air['REPORT_DATE'])
z_air['REPORT_DATE'] = z_air['REPORT_DATE'].dt.strftime("%Y-%m-%d")

# p = z_air

# print(p)
# print(p.columns.tolist())

#%%


# ### BRING ALL TOGETHER

combo = pd.merge(zfin, z_air, on=['CODE', 'REPORT_DATE'], how='left')

combo = combo.sort_values(by=['REPORT_DATE'], ascending=True)

oz = combo.loc[combo['CODE'] == "AUS"].copy()
latest_tests = oz.iloc[-1]['TEST_CNT']
second_latest_tests = oz.iloc[-2]['TEST_CNT']

# %%

prok = combo.copy()

juris = prok.columns.tolist()
juris = [x for x in juris if x != "REPORT_DATE"]


feed = []

for juri in prok['CODE'].unique().tolist():
    inter = prok.loc[prok['CODE'] == juri].copy()

    ## Check to make sure we aren't working with old data:
    if latest_tests == second_latest_tests:
        inter = inter[:-1]

    if juri == "AUS":
        
        inter['DEATH_CNT'] = inter['DEATH_CNT'].ffill()

        inter['MED_HOSP_CNT'] = pd.to_numeric(inter['MED_HOSP_CNT'])
        inter['MED_HOSP_CNT'] = inter['MED_HOSP_CNT'].ffill()


        inter['NEW_DEATHS'] = inter['DEATH_CNT'].diff(1)

        inter['DEATH_SHIFTED'] = round(inter['NEW_DEATHS'].rolling(window=30).sum(),0)

        inter['HOSPITALISATION_SHIFTED'] = inter['MED_HOSP_CNT'].shift(7)

        latest = inter.loc[inter['REPORT_DATE'] == inter['REPORT_DATE'].max()]

        two_doses = inter['Two_doses'].max()
        boosters = inter['Boosters'].max()

        deaths_shifted = latest['DEATH_SHIFTED'].values[0]

        hospitalised = latest['MED_HOSP_CNT'].values[0]
        hospitalised_week_ago = latest['HOSPITALISATION_SHIFTED'].values[0]

        if hospitalised > hospitalised_week_ago:
            hospitalised_status = "Increasing"
        elif round(hospitalised,0) == round(hospitalised_week_ago,0):
            hospitalised_status = "No_change"
        else:
            hospitalised_status = "Decreasing"

        feed.append([ juri + "_hospitalised" , hospitalised])
        feed.append([ juri + "_PREV_WEEK_hospitalised" , hospitalised_week_ago])
        feed.append([ juri + "_status" , hospitalised_status])

        feed.append([juri + '_boosters_percent', boosters])
        feed.append([juri + '_boosters_eligible_percent', booster_eligible])
        feed.append([juri + '_two_doses_percent', two_doses])
        feed.append([juri + '_deaths_last_thirty', deaths_shifted])



    else:

        inter['HOSPITALISATION_SHIFTED'] = inter['MED_HOSP_CNT'].shift(7)

        latest = inter.loc[inter['REPORT_DATE'] == inter['REPORT_DATE'].max()]

        hospitalised = latest['MED_HOSP_CNT'].values[0]
        hospitalised_week_ago = latest['HOSPITALISATION_SHIFTED'].values[0]

        if hospitalised > hospitalised_week_ago:
            hospitalised_status = "Increasing"
        elif round(hospitalised,0) == round(hospitalised_week_ago,0):
            hospitalised_status = "No_change"
        else:
            hospitalised_status = "Decreasing"

        feed.append([ juri + "_hospitalised" , hospitalised])
        feed.append([ juri + "_PREV_WEEK_hospitalised" , hospitalised_week_ago])
        feed.append([ juri + "_status" , hospitalised_status])

consolidated = {}
for row in feed:
    consolidated[row[0]] = row[1]
    # print(row)

print(consolidated)

boom = json.dumps(consolidated)

syncData(boom, "2021/06/coronavirus-thrasher-data", "thrasher-health-scrape-data-new.json")