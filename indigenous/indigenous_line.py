#%%

import pandas as pd 
import datetime
from yachtcharter import yachtCharter
chart_key = f"oz-covid-indigenous_vs_non_indigenous_vax_rates"

fillo = 'https://vaccinedata.covid19nearme.com.au/data/all.csv'

#%%

### THESE ARE 12+ POPULATIONS, AS USED IN OUR SPREADSHEET
# https://docs.google.com/spreadsheets/d/1cR0XSzndyV7J4IbNzvnKBK2diuOB6Bo0FUBzztcPlCk/edit#gid=71499319
pops = {"indig":591170, 'non_indig': 21272779}

df = pd.read_csv(fillo)

# 'DATE_AS_AT', 'TOTALS_NATIONAL_TOTAL',
#  'TOTALS_NATIONAL_LAST_24HR', 'TOTALS_CWTH_ALL_TOTAL',
#  'FIRST_NATIONS_AUS_FIRST_DOSE_TOTAL', 'FIRST_NATIONS_AUS_SECOND_DOSE_TOTAL

#%%

zdf = df[['DATE_AS_AT','FIRST_NATIONS_AUS_FIRST_DOSE_TOTAL', 'FIRST_NATIONS_AUS_SECOND_DOSE_TOTAL']]

zdf.columns = ['Date', 'Indig_first', 'Indig_second']

## Drop duplicates so we just have weekly data

zdf = zdf.drop_duplicates(subset=['Indig_first', 'Indig_second'], keep='first')
zdf = zdf.dropna(subset=['Indig_first', 'Indig_second'])


#%%

### READ IN NATIONAL FIGURES

nat = pd.read_csv('https://vaccinedata.covid19nearme.com.au/data/air.csv')

#%%
## Cut down and join

oz = nat[['DATE_AS_AT','AIR_AUS_16_PLUS_FIRST_DOSE_COUNT', 
'AIR_AUS_16_PLUS_SECOND_DOSE_COUNT','AIR_12_15_FIRST_DOSE_COUNT',
'AIR_12_15_SECOND_DOSE_COUNT']]

# oz = oz.loc[oz['DATE_AS_AT'] == '2021-10-31']

oz = oz.copy()

oz['AIR_12_15_FIRST_DOSE_COUNT'] = oz['AIR_12_15_FIRST_DOSE_COUNT'].fillna(0)
oz['AIR_12_15_SECOND_DOSE_COUNT'] = oz['AIR_12_15_SECOND_DOSE_COUNT'].fillna(0)

oz['All_first_doses'] = oz['AIR_AUS_16_PLUS_FIRST_DOSE_COUNT'] + oz['AIR_12_15_FIRST_DOSE_COUNT']
oz['All_second_doses'] = oz['AIR_AUS_16_PLUS_SECOND_DOSE_COUNT'] + oz['AIR_12_15_SECOND_DOSE_COUNT']

oz = oz[['DATE_AS_AT', 'All_first_doses', 'All_second_doses']]
oz.columns = ['Date', 'All_first_doses', 'All_second_doses']


#%%

## Bring together and do calcs

combo = pd.merge(zdf, oz, on='Date', how='left')

# combo = combo.drop_duplicates(subset=['Indig_first', 'Indig_second', 'Indig_one_dose_%', 'Indig_fully_vax_%', 'All_first_doses', 'All_second_doses'])

combo['Non_indig_first'] = combo['All_first_doses'] - combo['Indig_first'] 
combo['Non_indig_second'] = combo['All_second_doses'] - combo['Indig_second']

combo['Non_indig_first_%'] = (combo['Non_indig_first'] / pops['non_indig']) * 100
combo['Non_indig_second_%'] = (combo['Non_indig_second'] / pops['non_indig']) * 100

combo['Indig_first_%'] = (combo['Indig_first'] / pops['indig']) * 100
combo['Indig_second_%'] = (combo['Indig_second'] / pops['indig']) * 100


#%%

fin = combo.copy()
fin = fin[['Date', 'Indig_first_%', 'Indig_second_%',
 'Non_indig_first_%', 'Non_indig_second_%']]

## Quick calcs
last_updated = fin['Date'].max()
last_updated = datetime.datetime.strptime(last_updated, "%Y-%m-%d")
last_updated = datetime.datetime.strftime(last_updated, '%d %B %Y')

latest = fin.loc[fin['Date'] == fin['Date'].max()]
current_gap = round(latest['Non_indig_second_%'].values[0] - latest['Indig_second_%'].values[0],1)


fin.columns = ['Date', "Indigenous % at least one dose (12+)", 
'Indigenous % fully vaccinated (12+)', 'Non-Indigenous % at least one dose (12+)',
'Non-Indigenous % fully vaccinated (12+)']



final = fin.to_dict(orient='records')

p = fin


# print(p)
# print(p.columns.tolist())

# cols = [x for x in nat.columns.tolist() if "AUS" in x]

# print(cols)

# #%%

template = [
	{
	"title": "Indigenous vaccination rates v non-Indigenous rates over time",
	"subtitle": f"Comparing Indigenous and non-Indigenous vaccination rates (12+ populations). The current gap between the percentage of fully vaccinated Indigenous and non-Indigenous people is {current_gap}. This data is released weekly. Last updated {last_updated}.",
	"footnote": "Footnote",
	"source": "Guardian graphic | Source: Guardian Australia analysis of Department of Health data, scraped by Ken Tsang. Indigenous population numbers from the AIR, non-Indigenous population numbers from ABS estimated residental population, less the Indigenous number.",
	"margin-left": "35",
	"margin-top": "30",
	"margin-bottom": "20",
	"margin-right": "10",
    "dateFormat": "%Y-%m-%d",
    "yScaleType":"",
    "xAxisLabel": "Date",
    "yAxisLabel": "Percentage",
	}
]

yachtCharter(template=template, 
			data=final,
			chartId=[{"type":"linechart"}],
			chartName=f"{chart_key}")

# #%%
# %%
