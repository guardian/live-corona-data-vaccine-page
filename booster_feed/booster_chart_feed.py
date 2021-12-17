#%%
import requests
import pandas as pd 
import numpy as np
import datetime
pd.set_option("display.max_rows", 100)
from yachtcharter import yachtCharter
chart_key = f"oz-live-corona-page-boosters-second-doses-tracker"

#%%
## Read in Anthony's data
# headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
# r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

# data = r.json()
# df = pd.read_json(r.text)
# df = df.sort_values(by='REPORT_DATE', ascending=True)

# with open("booster_feed/Anthony_feed.csv", "w") as f:
#     df.to_csv(f, index=False, header=True)

ant = pd.read_csv('booster_feed/Anthony_feed.csv')
ant = ant.loc[ant['CODE'] == "AUS"]
ant = ant[['REPORT_DATE', 'VACC_PEOPLE_CNT']]
ant = ant.loc[(ant['REPORT_DATE'] < "2021-07-01") & (ant['REPORT_DATE'] > "2021-03-01")]

ant.columns = ['Date', 'Second doses']
ant['Boosters'] = 0

# %%
## Read in Ken's data 
ken = pd.read_csv('https://vaccinedata.covid19nearme.com.au/data/air.csv')
ken = ken.sort_values(by='DATE_AS_AT', ascending=True)
ken = ken.loc[ken['DATE_AS_AT'] >= "2021-07-01"]
ken.fillna(0, inplace=True)

ken['Second'] = ken['AIR_AUS_16_PLUS_SECOND_DOSE_COUNT'] + ken['AIR_12_15_SECOND_DOSE_COUNT']

ken = ken[['DATE_AS_AT','Second', 'AIR_AUS_16_PLUS_THIRD_DOSE_COUNT']]
ken.columns = ['Date', 'Second doses', 'Boosters']

latest_date = ken['Date'].max()
init_date = datetime.datetime.strptime(latest_date, "%Y-%m-%d")
display_date = datetime.datetime.strftime(init_date, "%-d %B %Y")
use_date = datetime.datetime.strftime(init_date, "%Y-%m-%d")

# %%
## Append Ken's data to Anthony

vax = ant.append(ken)

vax.fillna(0, inplace=True)

### Fill in the join between the Ken and Anthony datasets with interpolation
vax.loc[(vax['Date'] > "2021-06-28") & (vax['Date'] < "2021-07-02"), 'Second doses'] = np.nan
vax['Second doses'] = vax['Second doses'].interpolate(method='linear')

## Work out the trend line for boosters based on current gap

## Add days for the shirt
vax = vax.append(pd.DataFrame({'Date': pd.date_range(start=vax['Date'].max(), periods=200, freq='D')}))
vax['Date'] = pd.to_datetime(vax['Date'])
vax['Date'] = vax['Date'].dt.strftime("%Y-%m-%d")
# print(vax)

current_doses = vax['Boosters'].max()

print("Current doses", current_doses)

vax[f'Second doses'] = pd.to_numeric(vax[f'Second doses'])

difference = vax[vax[f'Second doses'] >= current_doses]

print("Difference", difference)

gap = difference['Date'].min()

gap = datetime.datetime.strptime(gap, "%Y-%m-%d")
print("Gap", gap)

current_lag = (init_date - gap).days+1

print("Lag", current_lag)

# print(vax.loc[vax['Date'] > "2021-06-20"])

vax['Trend'] = vax['Second doses'].shift(periods=current_lag, axis=0)

max_trend = vax.loc[vax['Trend'] == vax['Trend'].max()]['Date'].values[0]

vax.loc[vax['Date'] <= use_date, f'Trend'] = ''
vax.loc[vax['Date'] <= "2021-11-08", f'Boosters'] = ''

max_trend = datetime.datetime.strptime(max_trend, "%Y-%m-%d")

cut_off = max_trend + datetime.timedelta(days=14)
cut_off = datetime.datetime.strftime(cut_off, "%Y-%m-%d")

vax = vax.loc[vax['Date'] < cut_off]

# print(cut_off)
# print(max_trend)

print(vax)

    


# see = vax.loc[(vax['Date'] > "2021-06-25") & (vax['Date'] < "2021-07-10")]

# p = vax
# print(p)
# print(p.columns.tolist())
# %%

vax.fillna("", inplace=True)

final = vax.to_dict(orient='records')


template = [
	{
	"title": "Tracking second and booster doses in Australia",
	"subtitle": f"Showing the cumulative count of second and booster doses. Trend in booster doses based on current gap between doses. Last updated {display_date}.",
	"footnote": "Footnote",
	"source": "CovidLive.com.au, Ken Tsang, Guardian Australia analysis",
	"margin-left": "35",
	"margin-top": "30",
	"margin-bottom": "20",
	"margin-right": "10"
	}
]

yachtCharter(template=template, 
			data=final,
			chartId=[{"type":"linechart"}],
            options=[{"colorScheme":"guardian", "lineLabelling":"TRUE"}],
			chartName=f"{chart_key}")