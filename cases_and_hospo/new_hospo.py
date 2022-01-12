#%%
import pandas as pd 
pd.set_option("display.max_rows", 100)
from yachtcharter import yachtCharter
chart_key = f"oz-covid-hospitalisation-percentage-ward-beds"

fillo = 'https://interactive.guim.co.uk/2022/01/oz-covid-health-data/cases.json'
testo = "-testo"
# testo = ''

#%%

df = pd.read_json(fillo)

# 'REPORT_DATE', 'CODE', 'ACTIVE_CNT', 'CASE_CNT', 'DEATH_CNT', 
# 'TEST_CNT', 'MED_HOSP_CNT', 'MED_ICU_CNT', 'NAME', 'PREV_ACTIVE_CNT',
# 'PREV_CASE_CNT', 'PREV_DEATH_CNT', 'PREV_TEST_CNT', 'PREV_MED_HOSP_CNT', '
# PREV_MED_ICU_CNT', 'NEW_CASE_CNT', 'PREV_NEW_CASE_CNT', 'LAST_UPDATED_DATE'


#%%
zdf = df.copy()

# thresh = {"AUS":67000, "ACT":1100, "NSW":24000, "NT":700,
# "QLD":18000, "SA":3000, "TAS":1600, "VIC": 17000, "WA": 1600}
## These numbers were calculated by reverse engineering the percentages in the Common Operating Picture. 
# There were no hospitalisations for WA and TAS, so I subtracted all the other states from national
# and divided the remainder by two 
# https://www.health.gov.au/sites/default/files/documents/2022/01/coronavirus-covid-19-common-operating-picture-3-january-2022.pdf

thresh = {"AUS":62575, "ACT":1151, "NSW":20722, "NT":977,
"QLD":12889, "SA":4532, "TAS":1472, "VIC": 14949, "WA": 5883}
# Using AIHW numbers from here:
# https://docs.google.com/spreadsheets/d/1tQOACyj-UGzcukpGp2Rz3jKMMTje5uTWmFRSvQU_ZRs/edit#gid=0

zdf = zdf.loc[zdf['REPORT_DATE'] > "2021-06-01"]
# zdf = zdf.loc[zdf['CODE'] == "AUS"]

listo = []
for juri in zdf['CODE'].unique().tolist():
    inter = zdf.loc[zdf['CODE'] == juri].copy()

    ## Drop successive duplicates
    inter = inter.loc[inter['TEST_CNT'] != inter['TEST_CNT'].shift(-1)]


    inter['MED_HOSP_CNT'] = pd.to_numeric(inter['MED_HOSP_CNT'])


    # inter[juri] = round((inter['MED_HOSP_CNT'] / thresh[juri])*100,2)

    inter[juri] = inter['MED_HOSP_CNT']
    inter = inter[['REPORT_DATE', juri]]

    inter.set_index('REPORT_DATE', inplace=True)

    listo.append(inter)

fin = pd.concat(listo,axis=1,sort=False)
fin = fin.reset_index()

fin.loc[fin["REPORT_DATE"] > "2021-12-19", "AUS"] = fin[['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'ACT', "NT"]].sum(axis=1)


for col in fin.columns.tolist():
    if col != "REPORT_DATE":
        fin[col] = round((fin[col] / thresh[col])*100,2)

print(fin)
print(fin.columns)

fin = fin[['REPORT_DATE', 'AUS']]


# #%%
fin.fillna("", inplace=True)
final = fin.to_dict(orient='records')

template = [
	{
	"title": "Estimated percentage of Australian hospital ward beds occupied by Covid patients",
	"subtitle": "Showing the total number of hospitalised Covid patients divided by the estimated number of hospital ward beds in the Australian Common Operating Picture 2.0. Hospital admissions scraped from the department of health, the most recent data may be incomplete.",
	"footnote": "",
    "dateFormat": "%Y-%m-%d",
	"source": "Department of health, Guardian Australia analysis",
	"margin-left": "30",
	"margin-top": "30",
	"margin-bottom": "20",
	"margin-right": "10"
	}
]

yachtCharter(template=template, 
            data=final,
            chartId=[{"type":"linechart"}],
            options=[{"colorScheme":"guardian", "lineLabelling":"FALSE"}],
            chartName=f"{chart_key}{testo}")

# #%%
# %%
