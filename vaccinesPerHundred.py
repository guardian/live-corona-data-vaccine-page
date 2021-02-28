import pandas as pd 
from modules.yachtCharter import yachtCharter
import datetime 
import os, ssl

#%%
print("Updating vaccines per hundred people chart")

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

#%%
oz_json = 'https://interactive.guim.co.uk/2021/02/coronavirus-widget-data/aus-vaccines.json'
row_csv = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv'

oz_pop = 25203000
# https://ourworldindata.org/grapher/population


# Sort out Australia's vaccination per hundred

oz = pd.read_json(oz_json)

#%%
oz['REPORT_DATE'] = pd.to_datetime(oz['REPORT_DATE'])
# oz = oz.sort_values(by ="REPORT_DATE", ascending=True)

oz['total_vaccinations_per_hundred'] = (oz["VACC_DOSE_CNT"] / oz_pop) * 100
oz['location'] = "Australia"
oz = oz.sort_values(by="REPORT_DATE", ascending=True)
#%%
last_date = oz[-2:-1]["REPORT_DATE"].dt.strftime("%Y-%m-%d").values[0]
#%%
oz.rename(columns={"REPORT_DATE":"date"}, inplace=True)

oz = oz[['location', 'date', 'total_vaccinations_per_hundred']]

# oz = oz.dropna(subset=['total_vaccinations_per_hundred'])


# Sort out everyone else from Our World in Data

our_world = pd.read_csv(row_csv, parse_dates=['date'])
our_world = our_world.sort_values(by="date", ascending=True)


# our_world = our_world.sort_values(by="date", ascending=True)

countries = ['Israel', 'United Kingdom', 'United States', "European Union"]
our_world = our_world.loc[our_world["location"].isin(countries)]

# Following code is if we want to fill gaps with rolling average

# dates = our_world['date'].unique()
# listo = []
# for country in countries:
#     inter = pd.DataFrame(dates)
#     inter.rename(columns={0:"date"}, inplace=True)
#     merged = pd.merge(inter, our_world.loc[our_world['location'] == country], on="date", how="left")
#     merged['location'] = country
#     merged['total_vaccinations_per_hundred'] = merged['total_vaccinations_per_hundred'].rolling(15, min_periods=1).mean()
#     listo.append(merged)
# our_world = pd.concat(listo)

our_world = our_world[['date','total_vaccinations_per_hundred', 'location']]

# Append Australia to rest of the world

combined = our_world.append(oz)
combined = combined.sort_values(by="date", ascending=True)
combined['date'] = combined['date'].dt.strftime('%Y-%m-%d')

# Pivot the dataframe

pivoted = combined.pivot(index="date", columns='location')['total_vaccinations_per_hundred'].reset_index()

def makeTestingLine(df):

	
    template = [
            {
                "title": "Covid-19 vaccinations per hundred people, selected countries",
                "subtitle": f"Last updated {last_date }",
                "footnote": "",
                "source": "Covidlive.com.au, Our World in Data ",
                "dateFormat": "%Y-%m-%d",
                "yScaleType":"",
                "xAxisLabel": "Date",
                "yAxisLabel": "Vaccinations per hundred people",
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
    key = [     {"key": "Australia", "colour": "#bbce00"},
                {"key":"Israel","colour":"#e5005a"},
                {"key":"United Kingdom","colour":"#f9b000"},
                {"key":"United States","colour":"#ffe500"},
                {"key":"European Union","colour":"#00a194"}
            ]
    periods = []
    labels = []

    # chartId = [{"type":"linechart"}]
    df.fillna("", inplace=True)
    # df = df.reset_index()
    chartData = df.to_dict('records')

    yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], 
    options=[{"colorScheme":"guardian", "lineLabelling":"TRUE"}], chartName="vaccines_per_hundred")

# makeTestingLine(pivoted)