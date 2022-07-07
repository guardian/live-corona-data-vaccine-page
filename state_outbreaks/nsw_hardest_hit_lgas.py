#%%

import pandas as pd 
# pd.set_option("display.max_rows", 100)
import datetime
import pytz
from yachtcharter import yachtCharter
chart_key = f"oz-covid-nsw-lgas-active-table"

# fillo = "https://data.nsw.gov.au/data/dataset/aefcde60-3b0c-4bc0-9af1-6fe652944ec2/resource/21304414-1ff1-4243-a5d2-f52778048b29/download/confirmed_cases_table1_location.csv"

fillo = 'https://covidlive.com.au/report/cases-by-lga/nsw'

testo = "-testo"
# testo = ''

#%%

# df = pd.read_csv(fillo)
df = pd.read_html(fillo)[1]

df = df[['LGA', 'ACTIVE', 'CASES', 'NET']]


# #%%
# %%


### Read in LGA pops

pops = pd.read_excel('state_outbreaks/32180DS0002_2019-20.xls', sheet_name='Table 1', skiprows=6)
pops = pops[['Unnamed: 1', 2020]]

pops.dropna(subset=[2020], inplace=True)
pops.columns = pops.iloc[0]
pops = pops[1:]

pops = pops.loc[~pops['Local Government Area'].str.contains("TOTAL")]
pops = pops.loc[~pops['Local Government Area'].str.contains("Unincorporated")]

pops['LGA'] = pops['Local Government Area'].str.split("(").str[0].str.strip()

pops.loc[pops['LGA'] == 'Nambucca Valley', 'LGA'] = 'Nambucca'

pops = pops[['LGA', 'no.']]
pops.columns = ['LGA', 'Population']


# %%
zdf = df.copy()
pop = pops.copy()

combo = pd.merge(pop, zdf, on='LGA', how='left')

combo.columns = ['LGA', 'Population', 'Current Active', 'Total Cases', 'New Cases']

combo['Current Active'] = pd.to_numeric(combo['Current Active'])
combo['Population'] = pd.to_numeric(combo['Population'])
combo['New Cases'] = pd.to_numeric(combo['New Cases'])

combo['Active per 1k'] = round((combo['Current Active']/combo['Population'])*1000,2)
combo['New cases per 1k'] = round((combo['New Cases']/combo['Population'])*1000,2)

combo = combo[['LGA', 'New Cases', 'Current Active', 'Total Cases', 'Active per 1k', 'New cases per 1k']]

combo = combo.sort_values(by='Current Active', ascending=False)

today = datetime.datetime.now()
format_date = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%-d %B %Y')

# p = combo

# vchecker = 'ACTIVE'
# print(p.loc[p[vchecker].isna()])
# print(p)
# print(p.columns.tolist())
# %%

final = combo.to_dict(orient='records')
template = [
	{
	"title": "New and active cases by New South Wales Local Government Area",
	"subtitle": f"Per 1k stats calculated using the estimated resident population of each LGA. Most recent day's data may be incomplete. Last updated {format_date}",
	"footnote": "",
	"source": "CovidLive.com.au, Australian Bureau of Statistics, Guardian Australia analysis",
	"margin-left": "20",
	"margin-top": "30",
	"margin-bottom": "20",
	"margin-right": "10"
	}
]

yachtCharter(template=template, 
            options=[{"colorScheme":"guardian","format": "scrolling",
            "enableSearch": "TRUE","enableSort": "TRUE"}],
			data=final,
			chartId=[{"type":"table"}],
			chartName=f"{chart_key}")


# def makeTable(df):
	
#     template = [
#             {
#                 "title": "Victoria Covid Hotspots",
#                 "subtitle": f"""""",
#                 "footnote": """""",
#                 "source": """Victorian government | Notes: Tier 1: Anyone who has visited this location during these times must get tested immediately and quarantine for 14 days from the exposure. 
#                 Tier 2: Anyone who has visited this location during these times should urgently get tested, then isolate until confirmation of a negative result. Continue to monitor for symptoms, get tested again if symptoms appear.
#                 Tier 3: Anyone who has visited this location during these times should monitor for symptoms - If symptoms develop, immediately get tested and isolate until you receive a negative result.""",
#                 "yScaleType":"",
#                 "minY": "0",
#                 "maxY": "",
#                 "x_axis_cross_y":"",
#                 "periodDateFormat":"",
#                 "margin-left": "50",
#                 "margin-top": "30",
#                 "margin-bottom": "20",
#                 "margin-right": "10"
#             }
#         ]
#     key = []
#     # labels = []
#     df.fillna("", inplace=True)
#     chartData = df.to_dict('records')
#     labels = []


#     yachtCharter(template=template, labels=labels, data=chartData, chartId=[{"type":"table"}], 
#     options=[{"colorScheme":"guardian","format": "scrolling","enableSearch": "TRUE","enableSort": "TRUE"}], chartName=f"vic_covid_hotspots{testo}")

# makeTable(df)