#%%
import pandas as pd
from modules.yachtCharter import yachtCharter
import numpy as np
import datetime
import pytz


chart_key = "oz-live-corona-state-vax-table-updated-trend"
test = ''
# test = '_testo'
#%%

pops = {'NT':246.5* 1000, 'NSW':8166.4* 1000,
'VIC':6680.6* 1000, 'QLD':5184.8* 1000,
'ACT':431.2* 1000, 'SA':1770.6* 1000,
 'WA':2667.1* 1000, 'TAS':541.1* 1000}

# source: https://www.abs.gov.au/statistics/people/population/national-state-and-territory-population/sep-2020

pd.options.mode.chained_assignment = None

# 16+ population counts:

sixteen_pop = {
    'NT':190571, 'NSW':6565651, 'VIC':5407574,
    'QLD':4112707, 'ACT':344037,
    'SA':1440400, 'WA':2114978, 'TAS':440172, "AUS":20619959}

twelve_pop = {
    'NT':190571 + 13060, 'NSW':6565651 + 390330, 
    'VIC':5407574 + 308611,
    'QLD':4112707 + 270146 , 'ACT':344037 + 18930 ,
    'SA':1440400 + 82747, 'WA':2114978 + 132869,
     'TAS':440172 + 26308 , "AUS":20619959 + 1243990}

five_plus = {'NT':190571 + 13060 + 24750, 'NSW':6565651 + 390330 + 716460, 
    'VIC':5407574 + 308611 +578499,
    'QLD':4112707 + 270146 +478731, 'ACT':344037 + 18930 +39789,
    'SA':1440400 + 82747 + 148816, 'WA':2114978 + 132869 + 244154,
     'TAS':440172 + 26308 + 45033, "AUS":20619959 + 1243990 + 2276638}

# source: https://www.health.gov.au/sites/default/files/documents/2021/07/covid-19-vaccine-rollout-update-5-july-2021.pdf

url = 'https://vaccinedata.covid19nearme.com.au/data/air.json'

# print(url.columns.tolist())

air_data = pd.read_json(url)

cols = list(air_data.columns)

states =['NSW','VIC','QLD','WA','SA','TAS','NT','ACT','AUS']
short_cols = ['DATE_AS_AT']

for state in states:
	short_cols.append(f'AIR_{state}_16_PLUS_FIRST_DOSE_COUNT')
	short_cols.append(f'AIR_{state}_16_PLUS_SECOND_DOSE_COUNT')

newData = pd.DataFrame(columns=['DATE_AS_AT','FIRST_DOSE_COUNT', 'SECOND_DOSE_COUNT'])

for state in states:
	temp = air_data[['DATE_AS_AT',f'AIR_{state}_16_PLUS_FIRST_DOSE_COUNT', f'AIR_{state}_16_PLUS_SECOND_DOSE_COUNT']]
	temp['STATE'] = state
	temp = temp.rename(columns={f'AIR_{state}_16_PLUS_FIRST_DOSE_COUNT':'FIRST_DOSE_COUNT',f'AIR_{state}_16_PLUS_SECOND_DOSE_COUNT':'SECOND_DOSE_COUNT'}) 
	newData = newData.append(temp)

#%%

def makeProjection(state, cutoff_date):
	
	# variables set up for state projections
	
	today = datetime.datetime.today().date()
	
	# assumptions_cutoff = datetime.datetime.strptime("2021-09-01", "%Y-%m-%d")
	end_year = datetime.datetime.strptime("2022-01-01", "%Y-%m-%d")
	temp_state = newData.loc[newData['STATE'] == state].copy()
	temp_state = temp_state[temp_state['DATE_AS_AT'] <= cutoff_date]
	temp_state['daily_first_dose'] = temp_state['FIRST_DOSE_COUNT'].diff(1)
	temp_state['daily_second_dose'] = temp_state['SECOND_DOSE_COUNT'].diff(1)
	temp_state['daily_first_dose_avg'] = temp_state['daily_first_dose'].rolling(window=7).mean()
	temp_state['daily_second_dose_avg'] = temp_state['daily_second_dose'].rolling(window=7).mean()
	
	temp_state.to_csv('temp-state-doses.csv')
	
	last_doses = temp_state['daily_first_dose_avg'].iloc[-1]
	
	current_second_doses = temp_state['SECOND_DOSE_COUNT'].iloc[-1]
	print("current second", current_second_doses)
	current_first_doses = temp_state['FIRST_DOSE_COUNT'].iloc[-1]
	current_date = temp_state['DATE_AS_AT'].iloc[-1]
# 	print("currentdate", current_date)
	current_rolling = int(temp_state['daily_first_dose_avg'].iloc[-1])
	current_rolling_sec = int(temp_state['daily_second_dose_avg'].iloc[-1])
	# Handle data change in NT and ACT
	change_date = "2021-07-28"
	if state == "ACT" or state == "NT":
		temp_temp_state = temp_state[temp_state['DATE_AS_AT'] >= change_date]
		first_dose_eq_second = temp_temp_state[temp_temp_state['FIRST_DOSE_COUNT'] >= current_second_doses]['DATE_AS_AT'].iloc[0]
	else:	
		first_dose_eq_second = temp_state[temp_state['FIRST_DOSE_COUNT'] >= current_second_doses]['DATE_AS_AT'].iloc[0]
	
	current_lag = (current_date - first_dose_eq_second).days + 1
	print("current_lag", current_lag)
	ninety_target = sixteen_pop[state] * 0.9
	eighty_target = sixteen_pop[state] * 0.8
	seventy_target = sixteen_pop[state] * 0.7
	# print("eighty_target", eighty_target)
	ninety_vax_to_go = ninety_target - current_first_doses
	eighty_vax_to_go = eighty_target - current_first_doses
	seventy_vax_to_go = seventy_target - current_first_doses
	# print("eighty_vax_to_go",eighty_vax_to_go)
	
	if (eighty_vax_to_go < 0):
		print("80 target already reached")
		days_to_go_80 = 0
		eighty_finish_first = temp_state[temp_state['FIRST_DOSE_COUNT'] > eighty_target]['DATE_AS_AT'].iloc[0]
		print(eighty_finish_first)
	else:
		# print("80 target not yet reached")
		days_to_go_80 = int(round(eighty_vax_to_go / current_rolling,0)) + 1
		# print("days to go 80", days_to_go_80)
		eighty_finish_first = current_date + datetime.timedelta(days=days_to_go_80) 
		# print("eighty_finish_first", eighty_finish_first)

	if (seventy_vax_to_go < 0):
		print("70 target already reached")
		days_to_go_70 = 0
		seventy_finish_first = temp_state[temp_state['FIRST_DOSE_COUNT'] > seventy_target]['DATE_AS_AT'].iloc[0]
	else:
		# print("70 target not yet reached")
		days_to_go_70 = int(round(seventy_vax_to_go / current_rolling,0)) + 1
		seventy_finish_first = current_date + datetime.timedelta(days=days_to_go_70) 
		# print("days to go 70", days_to_go_70)

### ADD 90 target

	if (ninety_vax_to_go < 0):
		print("90 target already reached")
		days_to_go_90 = 0
		ninety_finish_first = temp_state[temp_state['FIRST_DOSE_COUNT'] > ninety_target]['DATE_AS_AT'].iloc[0]
	else:
		# print("90 target not yet reached")
		days_to_go_90 = int(round(ninety_vax_to_go / current_rolling,0)) + 1
		ninety_finish_first = current_date + datetime.timedelta(days=days_to_go_90) 
		# print("days to go 90", days_to_go_90)

	ninety_vax_to_go_second = int(ninety_target - current_second_doses)
	
	eighty_vax_to_go_second = int(eighty_target - current_second_doses)
	seventy_vax_to_go_second = int(seventy_target - current_second_doses)

	# print("eighty_vax_to_go_second", eighty_vax_to_go_second, "seventy_vax_to_go_second", seventy_vax_to_go_second)
	
	# Check if seventy percent second dose target has already been met

	seventy_reached = False
	if (seventy_vax_to_go_second < 0):
		print("70% second dose target already reached")
		seventy_finish_second = temp_state[temp_state['SECOND_DOSE_COUNT'] > seventy_target]['DATE_AS_AT'].iloc[0]
		seventy_reached = True
	else:	
		seventy_finish_second = seventy_finish_first + datetime.timedelta(days=current_lag)
	
	# Check if eighty percent second dose target has already been met
	
	eighty_reached = False
	if (eighty_vax_to_go_second < 0):
		print("80% second dose target already reached")
		eighty_finish_second = temp_state[temp_state['SECOND_DOSE_COUNT'] > eighty_target]['DATE_AS_AT'].iloc[0]
		days_to_second_80 = 0
		eighty_reached = True
	else:	
		eighty_finish_second = eighty_finish_first + datetime.timedelta(days=current_lag)
		days_to_second_80 = (eighty_finish_second - current_date).days + 1
	
	ninety_reached = False
	if (ninety_vax_to_go_second < 0):
		print("90% second dose target already reached")
		ninety_finish_second = temp_state[temp_state['SECOND_DOSE_COUNT'] > ninety_target]['DATE_AS_AT'].iloc[0]
		days_to_second_90 = 0
		ninety_reached = True
	else:	
		ninety_finish_second = ninety_finish_first + datetime.timedelta(days=current_lag)
		days_to_second_90 = (ninety_finish_second - current_date).days + 1


	
# 	print("days_to_second_80", days_to_second_80)
# 	print("eighty_finish_second",eighty_finish_second)

# 	
# 	eighty_vax_to_go_second = int(eighty_target - current_second_doses)
# 	print(eighty_vax_to_go_second,days_to_go_80,current_lag)


	## 21/10 New conditional to stop the divsion error:

	if days_to_second_80 == 0:
		second_doses_rate_needed = 0
	else:
		second_doses_rate_needed = int(round(eighty_vax_to_go_second / days_to_second_80,0))
# 	print("eighty_finish", eighty_finish_second)
	results = {"current_lag":current_lag, "current_rolling":current_rolling,  "second_doses_rate_needed":second_doses_rate_needed,
	"eighty_finish_first": eighty_finish_first, "seventy_finish_first":seventy_finish_first, "ninety_finish_first": ninety_finish_first,
	"eighty_finish_second":eighty_finish_second, "seventy_finish_second":seventy_finish_second, "ninety_finish_second": ninety_finish_second,
	"eighty_target":eighty_target, "seventy_target":seventy_target, "ninety_target":ninety_target,
	"seventy_reached":seventy_reached, "eighty_reached":eighty_reached, "ninety_reached": ninety_reached}
  # 	print(results)
	return results

#%%

latest_date = newData['DATE_AS_AT'].iloc[-1]


second = pd.read_json('https://vaccinedata.covid19nearme.com.au/data/air_residence.json')

# 'AIR_RESIDENCE_FIRST_DOSE_APPROX_COUNT',
#        'AIR_RESIDENCE_SECOND_DOSE_APPROX_COUNT', 'ABS_ERP_JUN_2020_POP',
#        'VALIDATED', 'URL', 'AIR_RESIDENCE_FIRST_DOSE_COUNT',
#        'AIR_RESIDENCE_SECOND_DOSE_COUNT'

# %%
second['DATE_AS_AT'] = pd.to_datetime(second['DATE_AS_AT'])
second = second.sort_values(by='DATE_AS_AT', ascending=True)

listo = []

for state in second['STATE'].unique().tolist():

    ## DO PROJECTION
  
	first_projection = makeProjection(state,latest_date)

	first_finish_70 = first_projection['seventy_finish_second']
	first_finish_80 = first_projection['eighty_finish_second']
	first_finish_90 = first_projection['ninety_finish_second']

	cutoff_date = (latest_date - datetime.timedelta(days=6))

	# second_projection = makeProjection(state,cutoff_date)
	
	
	second_finish_70 = first_finish_70 + datetime.timedelta(days=5)
	second_finish_80 = first_finish_80 + datetime.timedelta(days=5)
	second_finish_90 = first_finish_90 + datetime.timedelta(days=5)

	inter = second.loc[second['STATE'] == state].copy()
	to_use = inter.loc[(inter["AGE_LOWER"] == 16) & (inter['AGE_UPPER'] == 999)].copy()

	# print(second_finish_70)
	# print(second_finish_80)

	latest = to_use.loc[to_use['DATE_AS_AT'] == to_use['DATE_AS_AT'].max()].copy()

	latest = latest[['STATE', 'AIR_RESIDENCE_FIRST_DOSE_PCT', 'AIR_RESIDENCE_SECOND_DOSE_PCT']]
	
	if first_projection['seventy_reached'] == False:
		if first_finish_70.strftime('%b') == second_finish_70.strftime('%b'):
			latest['Hit 70'] = f"{first_finish_70.day} - {second_finish_70.day} {second_finish_70.strftime('%b')}"
		else: 
			latest['Hit 70'] = f"{first_finish_70.day} {first_finish_70.strftime('%b')} - {second_finish_70.day} {second_finish_70.strftime('%b')}"
	else:
		latest['Hit 70'] = first_finish_70.strftime('%-d %b') + " ✓"

	if first_projection['eighty_reached'] == False:
		if first_finish_80.strftime('%b') == second_finish_80.strftime('%b'):
			latest['Hit 80'] = f"{first_finish_80.day} - {second_finish_80.day} {second_finish_80.strftime('%b')}"
		else:
			latest['Hit 80'] = f"{first_finish_80.day} {first_finish_80.strftime('%b')} - {second_finish_80.day} {second_finish_80.strftime('%b')}"
	else:
		latest['Hit 80'] = first_finish_80.strftime('%-d %b') + " ✓"

	if first_projection['ninety_reached'] == False:
		if first_finish_90.strftime('%b') == second_finish_90.strftime('%b'):
			latest['Hit 90'] = f"{first_finish_90.day} - {second_finish_90.day} {second_finish_90.strftime('%b')}"
		else:
			latest['Hit 90'] = f"{first_finish_90.day} {first_finish_90.strftime('%b')} - {second_finish_90.day} {second_finish_90.strftime('%b')}"
	else:
		latest['Hit 90'] = first_finish_90.strftime('%-d %b') + " ✓"

	listo.append(latest)

table_data = pd.concat(listo)
table_data.columns = ['State', 'First dose %', 'Second dose %', "Expected to hit 70% second dose", "Expected to hit 80% second dose", "Expected to hit 90% second dose"]



## Add greater than signs when they reach 95

table_data.loc[table_data['First dose %'] >= 95, 'First dose %'] = "> " + table_data.loc[table_data['First dose %'] >= 95].astype(str)
table_data.loc[table_data['Second dose %'] >= 95, 'Second dose %'] = "> " + table_data.loc[table_data['Second dose %'] >= 95].astype(str)

# table_data.loc[table_data['First dose %'] >= 95, 'First dose %'] = table_data.loc[table_data['First dose %'] >= 95].str.strip()

table_data['First dose %'] = table_data['First dose %'].astype(str)
table_data['First dose %'] = table_data['First dose %'].str.strip()
# print(table_data['Second dose %'])
# print(table_data)
# print(table_data.columns.tolist())
# %%

# print(table_data)
# print(table_data.columns)

# table_data = table_data[['State', 'Second dose %','Expected to hit 90% second dose']]

updated_date = datetime.datetime.now()
updated_date = updated_date.astimezone(pytz.timezone("Australia/Sydney")).strftime('%d %B %Y')

def makeTable(df):

    template = [
            {
                "title": "Current vaccination levels by jurisdiction",
                "subtitle": f"""Showing the percentage of the 16+ population vaccinated by dose and state of residence, and the date we could hit 70% and 80% of the 16+ population fully vaccinated based on the current lag between administering first and second doses. Last updated {updated_date}.""",
                "footnote": "",
                "source": "Department of Health, Ken Tsang, Guardian Australia analysis",
                "yScaleType":"",
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
    key = []
    # labels = []
    df.fillna("", inplace=True)
    chartData = df.to_dict('records')
    labels = []


    yachtCharter(template=template, labels=labels, data=chartData, chartId=[{"type":"table"}],
    options=[{"colorScheme":"guardian","format": "vanilla","enableSearch": "FALSE","enableSort": "FALSE"}], chartName=f"{chart_key}{test}")

makeTable(table_data)