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

print("updating vaccine global bar chart")

row_csv = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv'

df = pd.read_csv(row_csv)

oecd = [
"Austria", "Australia", "Belgium", "Canada", "Chile", "Colombia", 
"Czech Republic", "Denmark", "Estonia", "Finland", "France", "Germany", 
"Greece", "Hungary", "Iceland", "Ireland", "Israel", "Italy", "Japan", "Korea", 
"Latvia", "Lithuania", "Luxembourg", "Mexico", "Netherlands", 
"New Zealand", "Norway", "Poland", "Portugal", "Slovak Republic", 
"Slovenia", "Spain", "Sweden", "Switzerland", "Turkey", "United Kingdom", "United States"

]

df = df.loc[df['location'].isin(oecd)]

listo = []

for country in df['location'].unique().tolist():
    inter = df.loc[df['location'] == country].copy()
    latest = inter.loc[inter['people_fully_vaccinated_per_hundred'] == inter['people_fully_vaccinated_per_hundred'].max()]
    listo.append(latest)

final = pd.concat(listo)

latest_date = final['date'].max()
latest_date = datetime.datetime.strptime(latest_date, '%Y-%m-%d')
latest_date = datetime.datetime.strftime(latest_date, '%d/%m/%Y')

final = final[['location', 'people_fully_vaccinated_per_hundred']]
final.columns = ['Country', 'Fully vaccinated']

final = final.dropna(subset=["Fully vaccinated"])

final = final.sort_values(by="Fully vaccinated", ascending=False)

final['Color'] = 'rgb(4, 109, 161)'
final.loc[final['Country'] == "Australia", "Color"] = "rgb(204, 10, 17)"



def makebarChart(df):
	
    template = [
            {
                "title": "Percentage of the population fully vaccinated by country",
                "subtitle": f"""Showing percentage of the population in OECD countries that have received two doses of a Covid-19 vaccine. Data unavaiablle for some countries. Last updated {latest_date}""",
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


    yachtCharter(template=template, dropdown=[],labels=labels,options=[{"enableShowMore":"TRUE", "autoSort":"FALSE"}], data=chartData, chartId=[{"type":"horizontalbar"}], chartName="oecd-covid-fully-vaccinated")

makebarChart(final)