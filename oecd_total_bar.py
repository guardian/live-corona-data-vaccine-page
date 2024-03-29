#%%
from modules.yachtCharter import yachtCharter
import pandas as pd
import os
import datetime

here = os.path.dirname(__file__)
data_path = os.path.dirname(__file__) + "/data/"
output_path = os.path.dirname(__file__) + "/output/"

# fillo = f"{data_path}"
#%%

# testo = '_'
testo = ''

print("updating vaccine global bar chart")

row_csv = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv'

df = pd.read_csv(row_csv)

oecd = [
"Austria", "Australia", "Belgium", "Canada", "Chile", "Colombia", "Costa Rica",
"Czechia", "Denmark", "Estonia", "Finland", "France", "Germany",
"Greece", "Hungary", "Iceland", "Ireland", "Israel", "Italy", "Japan", "South Korea",
"Latvia", "Lithuania", "Luxembourg", "Mexico", "Netherlands",
"New Zealand", "Norway", "Poland", "Portugal", "Slovakia",
"Slovenia", "Spain", "Sweden", "Switzerland", "Turkey", "United Kingdom", "United States"

]

df = df.loc[df['location'].isin(oecd)]

# print(df)
# print(df.columns.tolist())

cut_off = datetime.datetime.today().date()
cut_off = cut_off - datetime.timedelta(days=30)
cut_off = datetime.datetime.strftime(cut_off, '%Y-%m-%d')


inter = df.loc[df['location'] == 'Luxembourg'].copy()

# print(inter['total_vaccinations_per_hundred'].unique().tolist())

listo = []

for country in df['location'].unique().tolist():
    inter = df.loc[df['location'] == country].copy()
    inter = inter.drop_duplicates(subset=['total_vaccinations_per_hundred'], keep='first')
    latest = inter.loc[inter['total_vaccinations_per_hundred'] == inter['total_vaccinations_per_hundred'].max()].copy()

    ## ADD LATEST DATE
    datto = latest['date'].values[0]
    datto = datetime.datetime.strptime(datto, '%Y-%m-%d')
    datto = datetime.datetime.strftime(datto, '%d %B')


    latest['location'] = latest['location'].values[0] + f" ({datto})"
    
    # print(latest['location'])
    listo.append(latest)

final = pd.concat(listo)

latest_date = final['date'].max()
latest_date = datetime.datetime.strptime(latest_date, '%Y-%m-%d')
latest_date = datetime.datetime.strftime(latest_date, '%d %B %Y')

final = final.drop_duplicates(subset='location')

### CUT OFF COUNTRIES OLDER THAN A MONTH

final = final.loc[final['date'] >= cut_off]

final = final[['location', 'total_vaccinations_per_hundred']]
final.columns = ['Country', 'Fully vaccinated']

final = final.dropna(subset=["Fully vaccinated"])

final = final.sort_values(by="Fully vaccinated", ascending=False)

final['Color'] = 'rgb(4, 109, 161)'
final.loc[final['Country'].str.contains("Australia"), "Color"] = "rgb(204, 10, 17)"



def makebarChart(df):

    template = [
            {
                "title": "Total vaccinations per hundred population, by country",
                "subtitle": f"""Showing only OECD member countries. Date of latest data for each country in brackets. Last updated {latest_date}""",
                "footnote": "",
                "source": "Our World in Data",
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