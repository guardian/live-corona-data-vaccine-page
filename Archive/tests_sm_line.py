#%%
import requests
import pandas as pd
from modules.yachtCharter import yachtCharter
import datetime
chart_key = f"oz-covid-small-tests-small-multiples-line"

testo = ''

day = datetime.datetime.today().weekday()

#%%

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

#%%

## Grab Covid Live Data

data = r.json()
df = pd.read_json(r.text)
df = df.sort_values(by='REPORT_DATE', ascending=True)

df = df[['REPORT_DATE', 'CODE', 'TEST_CNT']]
# oz = df.loc[df['CODE'] == 'AUS'].copy()

df = df.loc[df["REPORT_DATE"] > "2021-01-01"]

df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
df['REPORT_DATE'] = df['REPORT_DATE'].dt.strftime("%Y-%m-%d")

population = {
	"NSW":8166.4* 1000,"VIC":6680.6* 1000,
	"QLD":5184.8* 1000,"SA":1770.6* 1000,
	"WA":2667.1* 1000,"TAS":541.1* 1000,"NT":246.5* 1000,
	"ACT":431.2* 1000,"AUS":25693.1 * 1000}


#%%
## Work out national tests per 100 people

oz = df.loc[df['CODE'] == 'AUS'].copy()

oz['New_tests'] = oz['TEST_CNT'].diff(1)

oz['New_tests'] = (oz['New_tests'] / population["AUS"])* 100

oz['Tests, 7 day avg'] = oz['New_tests'].rolling(window=7).mean()
oz = oz[['REPORT_DATE','Tests, 7 day avg']]


oz.columns = ['Date', 'National 7 day avg']


#%%


### WORK OUT FOR EVERYONE ELSE

other = df.loc[df['CODE']  != "AUS"].copy()

listo = []

for state in other['CODE'].unique().tolist():
    inter = other.loc[other['CODE'] == state].copy()

    inter['New_tests'] = inter['TEST_CNT'].diff(1)
    inter['New_tests'] = (inter['New_tests'] / population[state])* 100
    
    inter['Tests, 7 day avg'] = inter['New_tests'].rolling(window=7).mean()
    inter = inter[['REPORT_DATE','CODE', 'Tests, 7 day avg']]

    inter.columns = ['Date', 'State', f'State 7 day avg']

    listo.append(inter)


states = pd.concat(listo)


#%%

### Combine

combo = pd.merge(states, oz, on='Date', how='left')

combo = combo.sort_values(by='Date', ascending=True)

# final = combo.to_dict(orient='records')

combo.set_index('Date', inplace=True)
p = combo

print(p)
print(p.columns.tolist())

def makeStateVaccinations(df):
	
	template = [
			{
				"title": "Trend in daily Covid tests by state and territory",
				"subtitle": "Showing the seven-day rolling average of tests per day per 100 people in each state and territory, compared with the national rate",
				"footnote": "",
				"source": " | Source: CovidLive.com.au, Guardian Australia analysis",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "",
				"timeInterval":"day",
				# "tooltip":"<strong>Date: </strong>{{#nicedate}}Date{{/nicedate}}<br/><strong>Count: </strong>{{State or territory}}",
				"periodDateFormat":"",
				"margin-left": "25",
				"margin-top": "25",
				"margin-bottom": "22",
				"margin-right": "22",
				"xAxisDateFormat": "%b %d"
			}
		]
	key = []
	# periods = [{"label":"Data change", "start":"2021-08-16","end":"","textAnchor":"start"}]
	labels = []
	options = [{"numCols":2, "chartType":"line", "height":150, "scaleBy":"group"}]
	chartId = [{"type":"smallmultiples"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template,options=options, data=chartData, chartId=chartId, chartName=f"{chart_key}")

makeStateVaccinations(combo)
# %%
