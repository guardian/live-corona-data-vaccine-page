#%%
import simplejson as json
import boto3
import os
import requests
import pandas as pd
from modules.syncData import syncData
import numpy as np
import math

print("Checking covidlive")

#%%

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)


#%%

## Grab Covid Live Data

data = r.json()

clive = pd.read_json(r.text)

## Get the latest hostpital count
hospital = round( clive["MED_HOSP_CNT"][0] )

## Get the vaccine total count
total = round( clive["VACC_DOSE_CNT"][0] )

### Get boosters
if np.isnan(clive['VACC_BOOSTER_CNT'][0]):
	boost = round( clive['PREV_VACC_BOOSTER_CNT'][0])
else:
	boost = round( clive['VACC_BOOSTER_CNT'][0])

updated = clive["LAST_UPDATED_DATE"][0]
# 'REPORT_DATE', 'LAST_UPDATED_DATE', 'CODE', 'NAME', 'CASE_CNT', 
# 'TEST_CNT', 'DEATH_CNT', 'RECOV_CNT', 'MED_ICU_CNT', 'MED_VENT_CNT',
# 'MED_HOSP_CNT', 'SRC_OVERSEAS_CNT', 'SRC_INTERSTATE_CNT', 'SRC_CONTACT_CNT',
# 'SRC_UNKNOWN_CNT', 'SRC_INVES_CNT', 'PREV_CASE_CNT', 'PREV_TEST_CNT',
# 'PREV_DEATH_CNT', 'PREV_RECOV_CNT', 'PREV_MED_ICU_CNT', 'PREV_MED_VENT_CNT',
# 'PREV_MED_HOSP_CNT', 'PREV_SRC_OVERSEAS_CNT', 'PREV_SRC_INTERSTATE_CNT', 
# 'PREV_SRC_CONTACT_CNT', 'PREV_SRC_UNKNOWN_CNT', 'PREV_SRC_INVES_CNT', 
# 'PROB_CASE_CNT', 'PREV_PROB_CASE_CNT', 'ACTIVE_CNT', 'PREV_ACTIVE_CNT', 
# 'NEW_CASE_CNT', 'PREV_NEW_CASE_CNT', 'VACC_DIST_CNT', 'PREV_VACC_DIST_CNT',
# 'VACC_DOSE_CNT', 'PREV_VACC_DOSE_CNT', 'VACC_PEOPLE_CNT', 'PREV_VACC_PEOPLE_CNT',
# 'VACC_AGED_CARE_CNT', 'PREV_VACC_AGED_CARE_CNT', 'VACC_GP_CNT', 'PREV_VACC_GP_CNT', 
# 'VACC_FIRST_DOSE_CNT', 'PREV_VACC_FIRST_DOSE_CNT', 'VACC_FIRST_DOSE_CNT_12_15', 'PREV_VACC_FIRST_DOSE_CNT_12_15', 
# 'VACC_PEOPLE_CNT_12_15', 'PREV_VACC_PEOPLE_CNT_12_15', 'VACC_BOOSTER_CNT', 'PREV_VACC_BOOSTER_CNT'

# clive['PREV_VACC_PEOPLE_CNT'] = clive['PREV_VACC_PEOPLE_CNT'].astype('Int64', errors='raise')

clive = clive[['REPORT_DATE', 'CODE', 'NAME','PREV_CASE_CNT','CASE_CNT', 'NEW_CASE_CNT','PREV_NEW_CASE_CNT', 'PREV_VACC_DOSE_CNT', 'PREV_VACC_PEOPLE_CNT','ACTIVE_CNT', 'PREV_ACTIVE_CNT', "PREV_VACC_FIRST_DOSE_CNT_12_15", "PREV_VACC_PEOPLE_CNT_12_15", 'PREV_VACC_BOOSTER_CNT']]

# clive = clive[['REPORT_DATE', 'CODE', 'NAME', 'PREV_VACC_DOSE_CNT', 'PREV_VACC_PEOPLE_CNT','ACTIVE_CNT', 'PREV_ACTIVE_CNT']]

#print(type(clive))
# num = clive.select_dtypes(np.number)
# clive[num.columns ]= num.astype('Int64', errors='ignore')
#print(clive[['REPORT_DATE','CODE','ACTIVE_CNT', 'PREV_ACTIVE_CNT']].head(20))
#%%

#%%
# Population counts:
oz_pop = 25693.1 * 1000
oz_16_pop = 20619959
nsw_pop = 8166.4* 1000
vic_pop = 6680.6* 1000
qld_pop = 5184.8* 1000
sa_pop = 1770.6* 1000
wa_pop = 2667.1* 1000
tas_pop = 541.1* 1000
nt_pop = 246.5* 1000
act_pop = 431.2* 1000

areas = [('NT', nt_pop), ('NSW', nsw_pop), ('VIC', vic_pop), ('ACT', act_pop), ('WA', wa_pop), ('SA', sa_pop), ('TAS', tas_pop), ('QLD', qld_pop), ('AUS', oz_pop)]

first_listo = []

for area in areas:
	inter = clive.loc[clive['CODE'] == area[0]].copy()
	inter['Change_active_last_seven'] = inter['PREV_ACTIVE_CNT'].diff(-7)
	inter['Vax_per_hundred'] = round((inter['PREV_VACC_DOSE_CNT']/area[1])*100, 2)
	inter['Fully_vaxxed_per_hundred'] = round((inter['PREV_VACC_PEOPLE_CNT']/area[1])*100, 2)
	

	
	inter = inter.sort_values(by='REPORT_DATE', ascending=True)


	# CHECK IF ACTIVE IS NULL, IF SO USE PREVIOUS
	latest = inter.loc[inter['REPORT_DATE'] == inter['REPORT_DATE'].max()].copy()


	if np.isnan(latest['NEW_CASE_CNT'].values[-1]):
		inter['New_cases'] = inter['PREV_NEW_CASE_CNT']
	else:
		inter['New_cases'] = inter['NEW_CASE_CNT']
	# inter['New_cases'].diff(0)
	inter['New_cases'].fillna(0, inplace=True)

	inter['Cases_last_14'] = inter['New_cases'].rolling(window=14).sum()



	print(area[0])
	print(inter[['REPORT_DATE','New_cases','Cases_last_14']].tail())

	inter = inter.loc[inter['REPORT_DATE'] == inter['REPORT_DATE'].max()]
	inter['Active'] = inter['ACTIVE_CNT']
	if np.isnan(latest['ACTIVE_CNT'].values[0]):
		inter['Active'] = inter['PREV_ACTIVE_CNT']

	if area[0] == "AUS":
		 inter['Fully_vaxxed_per_16_plus'] = round(((inter['PREV_VACC_PEOPLE_CNT'] - inter["PREV_VACC_PEOPLE_CNT_12_15"])/oz_16_pop)*100, 2)
# 		inter['Fully_vaxxed_per_16_plus'] = round(((inter['PREV_VACC_PEOPLE_CNT'])/oz_16_pop)*100, 2)

	first_listo.append(inter)


clive = pd.concat(first_listo)






# %%

## GRAB AND WORK OUT OECD RANK

row_csv = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv'

row = pd.read_csv(row_csv)

oecd = [
"Austria", "Australia", "Belgium", "Canada", "Chile", "Colombia", "Costa Rica",
"Czechia", "Denmark", "Estonia", "Finland", "France", "Germany", 
"Greece", "Hungary", "Iceland", "Ireland", "Israel", "Italy", "Japan", "South Korea", 
"Latvia", "Lithuania", "Luxembourg", "Mexico", "Netherlands", 
"New Zealand", "Norway", "Poland", "Portugal", "Slovakia", 
"Slovenia", "Spain", "Sweden", "Switzerland", "Turkey", "United Kingdom", "United States"
]

row = row.loc[row['location'].isin(oecd)]

listo = []

for country in row['location'].unique().tolist():
	inter = row.loc[row['location'] == country].copy()
	latest = inter.loc[inter['people_fully_vaccinated_per_hundred'] == inter['people_fully_vaccinated_per_hundred'].max()]
	listo.append(latest)

final = pd.concat(listo)

final = final.drop_duplicates(subset='location')
final = final[['location', 'people_fully_vaccinated_per_hundred']]
final.columns = ['Country', 'Fully vaccinated']
final['Rank'] = final['Fully vaccinated'].rank(method='max', ascending=False)

# print(final)
# %%

## Combine and sync

print("Updating thrasher data")

aus_rank = final.loc[final['Country'] == "Australia"]['Rank'].values[0]


clive.loc[clive['NAME'] == "Australia", 'OECD_rank'] = aus_rank

clive['REPORT_DATE'] = pd.to_datetime(clive['REPORT_DATE'])

clive['REPORT_DATE'] = clive['REPORT_DATE'].dt.strftime('%Y-%m-%d')

#print(clive)
#print(clive.columns)

cliveJson = clive.to_json(orient='records')


#print(type(clive))






feed = []

for item in first_listo:

# 	listicle = item.values.tolist()

	value = round( item['PREV_ACTIVE_CNT'].iloc[-1] ) if math.isnan(item['ACTIVE_CNT'].iloc[-1]) else round( item['ACTIVE_CNT'].iloc[-1])

	feed.append([ item['CODE'].iloc[-1] , value ])

	if item['Change_active_last_seven'].iloc[-1] < 0:
		status = 'decrease'
	elif item['Change_active_last_seven'].iloc[-1]  > 0:
		status = 'increase'
	else:
		status = 'none'

	feed.append([ item['CODE'].iloc[-1] + "_status" , status ])

australia = clive.loc[clive['NAME'] == "Australia"]

print(australia)

### Get cases last 14
last_14 = round( australia["Cases_last_14"].iloc[-1])

print(last_14)


print(australia['Fully_vaxxed_per_hundred'].iloc[-1])

#%%
feed.append(["FULL" , australia['Fully_vaxxed_per_hundred'].iloc[0] ])

feed.append(["SIXTEEN" , australia['Fully_vaxxed_per_16_plus'].iloc[0]])

feed.append(["OECD" , round( australia['OECD_rank'].iloc[0] ) ])

feed.append(["HOSPITAL" , hospital ])

feed.append(["TOTAL" , total ])

feed.append(['BOOSTERS', boost])

feed.append(["UPDATED" , updated ])

feed.append(['CASES_LAST_14', last_14])

consolidated = {}
for row in feed:
	consolidated[row[0]] = row[1]

#with open("consolidated.json", "w") as data_file: 
#   json.dump(consolidated, data_file, indent=2)

boom = json.dumps(consolidated)

syncData(boom, "2021/06/coronavirus-thrasher-data", "covid-vaccines-consolidated.json")

# %%
