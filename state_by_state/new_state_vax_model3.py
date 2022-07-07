#%%
import pandas as pd
import requests
from modules.yachtCharter import yachtCharter
import datetime


pd.options.mode.chained_assignment = None


testo = "-testo"
#%%


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
    'QLD':4112707 + 270146 + 478731, 'ACT':344037 + 18930 +39789,
    'SA':1440400 + 82747 + 148816, 'WA':2114978 + 132869 + 244154,
     'TAS':440172 + 26308 + 45033, "AUS":20619959 + 1243990 + 2276638}

five_11_pop = {'NT':24750, 'NSW':716460,
    'VIC':578499,'QLD':478731, 'ACT':39789,
    'SA':148816, 'WA':244154,
     'TAS':45033, "AUS":2276638}

eighteen_plus = {"AUS": 20068897, "NSW": 6576596,
"VIC": 5366921, "QLD":4131396, "SA":1448431, 'WA':2118269, "TAS":443555,
"NT":186710, "ACT":342638}

url = 'https://vaccinedata.covid19nearme.com.au/data/air.json'

air_data = pd.read_json(url)

cols = list(air_data.columns)

states =['AUS','NSW','VIC','QLD','WA','SA','TAS','NT','ACT']
short_cols = ['DATE_AS_AT']

newData = pd.DataFrame()

cols = air_data.columns.tolist()
boost = [x for x in cols if "THIRD_DOSE_COUNT" in x]

p = air_data

print(p)
print(p.columns.tolist())

print(boost)

for state in states:
    temp = air_data.copy()

    # temp = air_data[['DATE_AS_AT',f'AIR_{state}_16_PLUS_FIRST_DOSE_COUNT', f'AIR_{state}_16_PLUS_SECOND_DOSE_COUNT']]
    temp['STATE'] = state



    temp[f'AIR_{state}_12_15_FIRST_DOSE_COUNT'] = pd.to_numeric(temp[f'AIR_{state}_12_15_FIRST_DOSE_COUNT'])
    temp[f'AIR_{state}_12_15_SECOND_DOSE_COUNT'] = pd.to_numeric(temp[f'AIR_{state}_12_15_SECOND_DOSE_COUNT'])

    temp[f'AIR_{state}_12_15_FIRST_DOSE_COUNT'].fillna(0, inplace=True)
    temp[f'AIR_{state}_12_15_SECOND_DOSE_COUNT'].fillna(0, inplace=True)

    temp['12_PLUS_FIRST'] = temp[f'AIR_{state}_16_PLUS_FIRST_DOSE_COUNT'] + temp[f'AIR_{state}_12_15_FIRST_DOSE_COUNT']
    temp['12_PLUS_SECOND'] = temp[f'AIR_{state}_16_PLUS_SECOND_DOSE_COUNT'] + temp[f'AIR_{state}_12_15_SECOND_DOSE_COUNT']

    temp['STATE'] = state
    temp = temp.rename(columns={f'AIR_{state}_5_11_FIRST_DOSE_COUNT':'5_11_FIRST',
    f'AIR_{state}_5_11_SECOND_DOSE_COUNT':'5_11_SECOND'})

    temp = temp.rename(columns={f'AIR_{state}_16_PLUS_FIRST_DOSE_COUNT':'16_PLUS_FIRST_DOSE_COUNT',f'AIR_{state}_16_PLUS_SECOND_DOSE_COUNT':'16_PLUS_SECOND_DOSE_COUNT'})

    if state == "AUS":
        temp.rename(columns={f'AIR_{state}_16_PLUS_THIRD_DOSE_COUNT': 'THIRD_DOSE'}, inplace=True)
    else:
        temp.rename(columns={f'AIR_{state}_18_PLUS_THIRD_DOSE_COUNT': 'THIRD_DOSE'}, inplace=True)

    temp = temp[['DATE_AS_AT','STATE', '16_PLUS_FIRST_DOSE_COUNT', '16_PLUS_SECOND_DOSE_COUNT',
    '12_PLUS_FIRST','12_PLUS_SECOND','5_11_FIRST', '5_11_SECOND', 'THIRD_DOSE']]



    newData = newData.append(temp)

#%%

def makeProjection(state, cutoff_date, first_dose_name, second_dose_name, booster_name, population_dict):

	# variables set up for state projections

	today = datetime.datetime.today().date()

	# assumptions_cutoff = datetime.datetime.strptime("2021-09-01", "%Y-%m-%d")
	end_year = datetime.datetime.strptime("2022-01-01", "%Y-%m-%d")
	temp_state = newData.loc[newData['STATE'] == state].copy()
	temp_state = temp_state[temp_state['DATE_AS_AT'] <= cutoff_date]

	temp_state['daily_first_dose'] = temp_state[first_dose_name].diff(1)
	temp_state['daily_second_dose'] = temp_state[second_dose_name].diff(1)
	temp_state['daily_booster_dose'] = temp_state[booster_name].diff(1)
	temp_state['daily_booster_dose'] = temp_state['daily_booster_dose'].fillna(0)


	temp_state['daily_first_dose_avg'] = temp_state['daily_first_dose'].rolling(window=7).mean()
	temp_state['daily_second_dose_avg'] = temp_state['daily_second_dose'].rolling(window=7).mean()
	temp_state['daily_booster_avg'] = temp_state['daily_booster_dose'].rolling(window=7).mean()

	print(state)
	# print(temp_state[booster_name])
	# print(temp_state['daily_booster_dose'])
	# print(temp_state['daily_booster_avg'])

	temp_state.to_csv('temp-state-doses.csv')

	last_doses = temp_state['daily_first_dose_avg'].iloc[-1]

	# current_second_doses = temp_state[second_dose_name].iloc[-1]
	current_second_doses = temp_state[second_dose_name].max()
	# print("current second", current_second_doses)
	# current_first_doses = temp_state[first_dose_name].iloc[-1]
	current_first_doses = temp_state[first_dose_name].max()
	# current_boosters = temp_state[booster_name].iloc[-1]
	current_boosters = temp_state[booster_name].max()

	current_date = temp_state['DATE_AS_AT'].iloc[-1]
# 	print("currentdate", current_date)
	current_rolling = int(temp_state['daily_first_dose_avg'].iloc[-1])
	current_rolling_sec = int(temp_state['daily_second_dose_avg'].iloc[-1])
	current_rolling_boosters = int(temp_state['daily_booster_avg'].iloc[-1])
	# Handle data change in NT and ACT
	change_date = "2021-07-28"

	if state == "ACT" or state == "NT":
		temp_temp_state = temp_state[temp_state['DATE_AS_AT'] >= change_date]
		first_dose_eq_second = temp_temp_state[temp_temp_state[first_dose_name] >= current_second_doses]['DATE_AS_AT'].iloc[0]
	else:
		first_dose_eq_second = temp_state[temp_state[first_dose_name] >= current_second_doses]['DATE_AS_AT'].iloc[0]

	current_lag = (current_date - first_dose_eq_second).days + 1

	print(state, current_lag)
	
	print(temp_state[temp_state[second_dose_name] >= current_boosters])

	print(current_boosters)

	booster_eq_second = temp_state[temp_state[second_dose_name] >= current_boosters]['DATE_AS_AT'].iloc[0]
	current_booster_lag = (current_date - booster_eq_second).days + 1


	# print("current_lag", current_lag)
	print("Current booster lag", current_booster_lag)

	ninety_target = population_dict[state] * 0.9
	eighty_target = population_dict[state] * 0.8
	seventy_target = population_dict[state] * 0.7

	booster_target_70 = population_dict[state] * 0.7
	booster_target_80 = population_dict[state] * 0.8
	booster_target_90 = population_dict[state] * 0.9

	# print("eighty_target", eighty_target)
	ninety_vax_to_go = ninety_target - current_first_doses
	eighty_vax_to_go = eighty_target - current_first_doses
	seventy_vax_to_go = seventy_target - current_first_doses

	booster_vax_to_go_70 = booster_target_70 - current_boosters
	booster_vax_to_go_80 = booster_target_80 - current_boosters
	booster_vax_to_go_90 = booster_target_90 - current_boosters
	# print("eighty_vax_to_go",eighty_vax_to_go)



	if (eighty_vax_to_go < 0):
		# print("80 target already reached")
		days_to_go_80 = 0
		eighty_finish_first = temp_state[temp_state[first_dose_name] > eighty_target]['DATE_AS_AT'].iloc[0]
		# print(eighty_finish_first)
	else:
		# print("80 target not yet reached")
		days_to_go_80 = int(round(eighty_vax_to_go / current_rolling,0)) + 1
		# print("days to go 80", days_to_go_80)
		eighty_finish_first = current_date + datetime.timedelta(days=days_to_go_80)
		# print("eighty_finish_first", eighty_finish_first)

	if (seventy_vax_to_go < 0):
		# print("70 target already reached")
		days_to_go_70 = 0
		seventy_finish_first = temp_state[temp_state[first_dose_name] > seventy_target]['DATE_AS_AT'].iloc[0]
	else:
		# print("70 target not yet reached")
		days_to_go_70 = int(round(seventy_vax_to_go / current_rolling,0)) + 1
		seventy_finish_first = current_date + datetime.timedelta(days=days_to_go_70)
		# print("days to go 70", days_to_go_70)

### ADD 90 target

	if (ninety_vax_to_go < 0):
		# print("90 target already reached")
		days_to_go_90 = 0
		ninety_finish_first = temp_state[temp_state[first_dose_name] > ninety_target]['DATE_AS_AT'].iloc[0]
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
		# print("70% second dose target already reached")
		seventy_finish_second = temp_state[temp_state[second_dose_name] > seventy_target]['DATE_AS_AT'].iloc[0]
		seventy_reached = True
	else:
		seventy_finish_second = seventy_finish_first + datetime.timedelta(days=current_lag)

	# Check if eighty percent second dose target has already been met

	eighty_reached = False
	if (eighty_vax_to_go_second < 0):
		# print("80% second dose target already reached")
		eighty_finish_second = temp_state[temp_state[second_dose_name] > eighty_target]['DATE_AS_AT'].iloc[0]
		days_to_second_80 = 0
		eighty_reached = True
	else:
		eighty_finish_second = eighty_finish_first + datetime.timedelta(days=current_lag)
		days_to_second_80 = (eighty_finish_second - current_date).days + 1

	ninety_reached = False
	if (ninety_vax_to_go_second < 0):
		# print("90% second dose target already reached")
		ninety_finish_second = temp_state[temp_state[second_dose_name] > ninety_target]['DATE_AS_AT'].iloc[0]
		days_to_second_90 = 0
		ninety_reached = True
	else:
		ninety_finish_second = ninety_finish_first + datetime.timedelta(days=current_lag)
		days_to_second_90 = (ninety_finish_second - current_date).days + 1


	booster_reached_70 = False
	if (booster_vax_to_go_70 < 0):

		days_to_go_booster_70 = 0
		booster_finish_70 = temp_state[temp_state[booster_name] > booster_target_70 ]['DATE_AS_AT'].iloc[0]
		booster_reached_70 = True
	else:
		days_to_go_booster = int(round(booster_vax_to_go_70 / current_rolling_boosters,0)) + 1
		booster_finish_70 = seventy_finish_second + datetime.timedelta(days=current_booster_lag)


	booster_reached_80 = False

	if (booster_vax_to_go_80 < 0):

		days_to_go_booster_80 = 0
		booster_finish_80 = temp_state[temp_state[booster_name] > booster_target_80 ]['DATE_AS_AT'].iloc[0]
		booster_reached_80 = True
	else:
		days_to_go_booster = int(round(booster_vax_to_go_80 / current_rolling_boosters,0)) + 1
		booster_finish_80 = eighty_finish_second + datetime.timedelta(days=current_booster_lag)


		booster_reached_90 = False
	if (booster_vax_to_go_90 < 0):

		days_to_go_booster_90 = 0
		booster_finish_90 = temp_state[temp_state[booster_name] > booster_target_90 ]['DATE_AS_AT'].iloc[0]
		booster_reached_90 = True
	else:
		days_to_go_booster = int(round(booster_vax_to_go_90 / current_rolling_boosters,0)) + 1
		booster_finish_90 = ninety_finish_second + datetime.timedelta(days=current_booster_lag)


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
# # 	print("eighty_finish", eighty_finish_second)
	results = {"current_lag":current_lag, "current_rolling":current_rolling,  "second_doses_rate_needed":second_doses_rate_needed,
	"eighty_finish_first": eighty_finish_first, "seventy_finish_first":seventy_finish_first, "ninety_finish_first": ninety_finish_first,
	"eighty_finish_second":eighty_finish_second, "seventy_finish_second":seventy_finish_second, "ninety_finish_second": ninety_finish_second,
	"eighty_target":eighty_target, "seventy_target":seventy_target, "ninety_target":ninety_target,
	"seventy_reached":seventy_reached, "eighty_reached":eighty_reached, "ninety_reached": ninety_reached,
	"booster_reached_70":booster_reached_70, "booster_reached_80":booster_reached_80, "booster_reached_90":booster_reached_90,
	"current_booster_lag":current_booster_lag, "current_booster_rolling":current_rolling_boosters,
	"booster_finish_70":booster_finish_70, "booster_finish_80":booster_finish_80, "booster_finish_90":booster_finish_90}

  # 	print(results)
	return results

#%%

latest_date = newData['DATE_AS_AT'].iloc[-1]


# %%

print('hi')



#%%

latest_date = newData['DATE_AS_AT'].iloc[-1]

newProjections = []



for state in states:
	# print(state)
	for day in range(0,6):
		# print("day",day)
		cutoff_date = (latest_date - datetime.timedelta(days=day))
		# print("cutoff", cutoff_date.strftime("%Y-%m-%d"))
		results = makeProjection(state,cutoff_date, '16_PLUS_FIRST_DOSE_COUNT', '16_PLUS_SECOND_DOSE_COUNT', 'THIRD_DOSE', sixteen_pop)
		print(results)
		row = {"day":day, "recent":(14 - day), "state":state, "eighty_finish_second":results['eighty_finish_second'].strftime("%Y-%m-%d"),
		 "seventy_finish_second":results["seventy_finish_second"].strftime("%Y-%m-%d"),"current_rolling":results['current_rolling'],
		  "second_doses_rate_needed":results['second_doses_rate_needed'], "eighty_target":results['eighty_target'],
		   "seventy_target":results['seventy_target'], "cutoff":cutoff_date, "seventy_reached": results['seventy_reached'],
		    "eighty_reached": results['eighty_reached'],
			"ninety_finish_second":results['ninety_finish_second'].strftime("%Y-%m-%d"),
			"ninety_target":results['ninety_target'],"ninety_reached": results['ninety_reached'],
			"current_booster_lag":results["current_booster_lag"], "current_booster_rolling":results["current_booster_rolling"],
			"booster_finish_70":results["booster_finish_70"].strftime("%Y-%m-%d"), "booster_finish_80":results["booster_finish_80"].strftime("%Y-%m-%d"), "booster_finish_90":results["booster_finish_90"].strftime("%Y-%m-%d")
			}


		newProjections.append(row)

newProjectionsDf = pd.DataFrame(newProjections)

print(newProjectionsDf)
print(newProjectionsDf.columns)


#%%

# Sync the data using Yacht

def makeChart(df):

	df['cutoff'] = df['cutoff'].dt.strftime("%Y-%m-%d")

	template = [
            {
                "title": "Current vaccination levels by jurisdiction",
                "subtitle": f"""Showing the percentage of the 16+ population vaccinated by dose and state of residence, and the date we could hit 70% and 80% of the 16+ population fully vaccinated based on the seven day moving average of second doses. Last updated {latest_date}""",
                "footnote": "",
                "source": "Department of Health, Ken Tsang",
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
    options=[{"colorScheme":"guardian","format": "vanilla","enableSearch": "FALSE","enableSort": "FALSE"}], chartName=f"new-model-state-projections-boosters{testo}")

makeChart(newProjectionsDf.copy())

#%%
