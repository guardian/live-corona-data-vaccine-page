#%%

import pandas as pd
import os
import datetime
import requests
import simplejson as json 

here = os.path.dirname(__file__)
data_path = os.path.dirname(__file__) + "/data/"
output_path = os.path.dirname(__file__) + "/output/"

# fillo = f"{data_path}"
#%%

# testo = '_'
testo = ''

print("updating vaccine global bar chart")

who_csv = 'https://covid19.who.int/who-data/vaccination-data.csv'
df = pd.read_csv(who_csv)
# 'COUNTRY', 'ISO3', 'WHO_REGION', 'DATA_SOURCE', 'DATE_UPDATED', 
# 'TOTAL_VACCINATIONS', 'PERSONS_VACCINATED_1PLUS_DOSE', 
# 'TOTAL_VACCINATIONS_PER100', 'PERSONS_VACCINATED_1PLUS_DOSE_PER100', 
# 'PERSONS_FULLY_VACCINATED', 'PERSONS_FULLY_VACCINATED_PER100', 
# 'VACCINES_USED', 'FIRST_VACCINE_DATE', 'NUMBER_VACCINES_TYPES_USED', 
# 'PERSONS_BOOSTER_ADD_DOSE', 'PERSONS_BOOSTER_ADD_DOSE_PER100'

df = df[['COUNTRY', 'DATE_UPDATED','TOTAL_VACCINATIONS_PER100']]

df.rename(columns={'COUNTRY': 'Country', 'DATE_UPDATED': "Date",'TOTAL_VACCINATIONS_PER100': "Total vaccination per 100"}, inplace=True)

oecd = [
"Austria", "Belgium", "Canada", "Chile", "Colombia", "Costa Rica",
"Czechia", "Denmark", "Estonia", "Finland", "France", "Germany",
"Greece", "Hungary", "Iceland", "Ireland", "Israel", "Italy", "Japan", "Republic of Korea",
"Latvia", "Lithuania", "Luxembourg", "Mexico", "Netherlands",
"New Zealand", "Norway", "Poland", "Portugal", "Slovakia",
"Slovenia", "Spain", "Sweden", "Switzerland", "Turkey", "The United Kingdom", "United States of America"

]


oe = df.loc[df['Country'].isin(oecd)]


#%%

### Grab Australian data from the Covid Live

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

#%%

oz = pd.read_json(r.text)
# 'REPORT_DATE', 'LAST_UPDATED_DATE', 'CODE', 'NAME',
# 'CASE_CNT', 'TEST_CNT', 'DEATH_CNT', 'RECOV_CNT', 
# 'MED_ICU_CNT', 'MED_VENT_CNT', 'MED_HOSP_CNT', 
# 'SRC_OVERSEAS_CNT', 'SRC_INTERSTATE_CNT', 'SRC_CONTACT_CNT', 
# 'SRC_UNKNOWN_CNT', 'SRC_INVES_CNT', 'PREV_CASE_CNT', 
# 'PREV_TEST_CNT', 'PREV_DEATH_CNT', 'PREV_RECOV_CNT', 
# 'PREV_MED_ICU_CNT', 'PREV_MED_VENT_CNT', 'PREV_MED_HOSP_CNT', 
# 'PREV_SRC_OVERSEAS_CNT', 'PREV_SRC_INTERSTATE_CNT', 
# 'PREV_SRC_CONTACT_CNT', 'PREV_SRC_UNKNOWN_CNT', 'PREV_SRC_INVES_CNT', 
# 'PROB_CASE_CNT', 'PREV_PROB_CASE_CNT', 'ACTIVE_CNT', 'PREV_ACTIVE_CNT', 
# 'NEW_CASE_CNT', 'PREV_NEW_CASE_CNT', 'VACC_DIST_CNT', 'PREV_VACC_DIST_CNT', 
# 'VACC_DOSE_CNT', 'PREV_VACC_DOSE_CNT', 'VACC_PEOPLE_CNT', 'PREV_VACC_PEOPLE_CNT', 
# 'VACC_AGED_CARE_CNT', 'PREV_VACC_AGED_CARE_CNT', 'VACC_GP_CNT', 'PREV_VACC_GP_CNT', 
# 'VACC_FIRST_DOSE_CNT', 'PREV_VACC_FIRST_DOSE_CNT', 'VACC_FIRST_DOSE_CNT_12_15', 
# 'PREV_VACC_FIRST_DOSE_CNT_12_15', 'VACC_PEOPLE_CNT_12_15', 'PREV_VACC_PEOPLE_CNT_12_15', 
# 'VACC_BOOSTER_CNT', 'PREV_VACC_BOOSTER_CNT', 'VACC_FIRST_DOSE_CNT_5_11', 
# 'PREV_VACC_FIRST_DOSE_CNT_5_11', 'VACC_PEOPLE_CNT_5_11', 'PREV_VACC_PEOPLE_CNT_5_11', 
# 'NEW_PROB_CASE_CNT', 'PREV_NEW_PROB_CASE_CNT', 'VACC_WINTER_CNT', 'PREV_VACC_WINTER_CNT'

oz = oz[['REPORT_DATE','NAME','VACC_DOSE_CNT']]

oz = oz.loc[oz['NAME'] == 'Australia']
oz = oz.loc[oz['VACC_DOSE_CNT'] == oz['VACC_DOSE_CNT'].max()]
oz = oz.loc[oz['REPORT_DATE'] == oz['REPORT_DATE'].min()]


oz.rename(columns={'NAME': 'Country', 
'REPORT_DATE': "Date",
'VACC_DOSE_CNT': "Total vaccination per 100"}, inplace=True)

oz["Total vaccination per 100"] = pd.to_numeric(oz["Total vaccination per 100"])

oz["Total vaccination per 100"] = round((oz["Total vaccination per 100"] / 25890773) * 100,3)

print(oz)
print(oz.columns.tolist())



#%%

final = pd.concat([oz, oe])

latest_date = final['Date'].max()
latest_date = datetime.datetime.strptime(latest_date, '%Y-%m-%d')
latest_date = datetime.datetime.strftime(latest_date, '%d %B %Y')

final['Date'] = pd.to_datetime(final['Date'])
final['Date'] = final['Date'].dt.strftime('%d %B')

for country in final['Country'].unique().tolist():
  datto = final.loc[final['Country'] == country]['Date'].values[0]
  final.loc[final['Country'] == country, 'Country'] = f"{country} ({datto})"

final = final[['Country', 'Total vaccination per 100']]

final = final.dropna(subset=["Total vaccination per 100"])


final = final.sort_values(by="Total vaccination per 100", ascending=False)

final['Color'] = 'rgb(4, 109, 161)'
final.loc[final['Country'].str.contains("Australia"), "Color"] = "rgb(204, 10, 17)"




print(final)
from modules.yachtCharter import yachtCharter
def makebarChart(df):

    template = [
            {
                "title": "Total vaccinations per hundred population, by country",
                "subtitle": f"""Showing only OECD member countries. Date of latest data for each country in brackets. Last updated {latest_date}""",
                "footnote": "",
                "source": "Our World in Data, CovidLive.com.au",
                # "dateFormat": "%Y-%m-%d",
                # "minY": "0",
                # "maxY": "",
                # "xAxisDateFormat":"%b %d",
                # "tooltip":"<strong>{{#formatDate}}{{data.Date}}{{/formatDate}}</strong><br/>{{group}}: {{groupValue}}<br/>Total: {{total}}",
                "margin-left": "20",
                "margin-top": "30",
                "margin-bottom": "20",
                "margin-right": "10"
            }
        ]
    # key = [{"Key": "Australia", "colour":"#197caa"}]
    key = []
    periods = []
    # labels = []
    df.fillna("", inplace=True)
    chartData = df.to_dict('records')
    labels = []


    yachtCharter(template=template, dropdown=[],labels=labels,options=[{"enableShowMore":"TRUE", "autoSort":"FALSE"}], data=chartData, chartId=[{"type":"horizontalbar"}], chartName=f"oecd-covid-total-vax-per-hundred{testo}")

makebarChart(final)


# %%