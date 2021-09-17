#%%
import pandas as pd
import requests
import os
import ssl
from modules.yachtCharter import yachtCharter
import numpy as np
import datetime
import pytz
import plotly.express as px
import plotly.graph_objs as go


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

# source: https://www.health.gov.au/sites/default/files/documents/2021/07/covid-19-vaccine-rollout-update-5-july-2021.pdf

url = 'https://vaccinedata.covid19nearme.com.au/data/air.json'

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

newData.to_csv('temp.csv')
	
#%%


#%%

# state = "NSW"
# cutoff_date = (latest_date - datetime.timedelta(days=2))
# latest_date = newData['DATE_AS_AT'].iloc[-1]
	
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
	
	current_lag = (current_date - first_dose_eq_second).days
	
	eighty_target = sixteen_pop[state] * 0.8
	seventy_target = sixteen_pop[state] * 0.7
	eighty_vax_to_go = eighty_target - current_first_doses
	seventy_vax_to_go = seventy_target - current_first_doses
	
	days_to_go_80 = int(round(eighty_vax_to_go / current_rolling,0))
	days_to_go_70 = int(round(seventy_vax_to_go / current_rolling,0))
	
	eighty_finish_first = today + datetime.timedelta(days=days_to_go_80)
	seventy_finish_first = today + datetime.timedelta(days=days_to_go_70)
	
	eighty_finish_second = eighty_finish_first + datetime.timedelta(days=current_lag)
	seventy_finish_second = seventy_finish_first + datetime.timedelta(days=current_lag)
	time_between_70_80_sec = eighty_finish_second - seventy_finish_second
	time_between_70_80_fir = eighty_finish_first - seventy_finish_first
# 	print("timediff1", time_between_70_80_fir)
# 	print("timediff2", time_between_70_80_sec)
	eighty_vax_to_go_second = int(eighty_target - current_second_doses)
# 	print(eighty_vax_to_go_second,days_to_go_80,current_lag)
	second_doses_rate_needed = int(round(eighty_vax_to_go_second / (days_to_go_80 + current_lag),0))
# 	print("eighty_finish", eighty_finish_second)
	results = {"current_lag":current_lag, "eighty_finish_first": eighty_finish_first, "seventy_finish_first":seventy_finish_first, "eighty_finish_second":eighty_finish_second, "seventy_finish_second":seventy_finish_second, "current_rolling":current_rolling, "second_doses_rate_needed":second_doses_rate_needed,"eighty_target":eighty_target}
# 	print(results)
	return results


#%%

latest_date = newData['DATE_AS_AT'].iloc[-1]

newProjections = []
test_states = ["NT"]

for state in states:
	print(state)
	for day in range(0,14):
		print("day",day)
		cutoff_date = (latest_date - datetime.timedelta(days=day))
		print("cutoff", cutoff_date.strftime("%Y-%m-%d"))
		results = makeProjection(state,cutoff_date)
		print(results)
		row = {"day":day, "recent":(14 - day), "state":state, "eighty_finish_second":results['eighty_finish_second'], "seventy_finish_second":results["seventy_finish_second"],"current_rolling":results['current_rolling'], "second_doses_rate_needed":results['second_doses_rate_needed'], "eighty_target":results['eighty_target'], "cutoff":cutoff_date}
		newProjections.append(row)
	
#%%

newProjectionsDf = pd.DataFrame(newProjections)

fig = px.scatter(newProjectionsDf, x=["eighty_finish_second", "seventy_finish_second"], y="state",
				 size='recent', color='recent', color_continuous_scale='reds', opacity=0.7)
																		
# fig.add_trace(go.Scatter(x=newProjectionsDf["seventy_finish_second"], y=newProjectionsDf["state"],
#                   mode='markers',opacity=0.7))


fig.show()

#%%

# This is all stuff for de-bugging the projection below here

def makeStateChart(state):

# 	state = "WA"
	date_index = pd.date_range(start='2021-07-01', end='2021-12-31')	
	temp_state = newData.loc[newData['STATE'] == state].copy()
	# temp_state = temp_state[temp_state['DATE_AS_AT'] <= cutoff_date]
	temp_state['daily_first_dose'] = temp_state['FIRST_DOSE_COUNT'].diff(1)
	temp_state['daily_second_dose'] = temp_state['SECOND_DOSE_COUNT'].diff(1)
	temp_state['daily_first_dose_avg'] = temp_state['daily_first_dose'].rolling(window=7).mean()
	temp_state['daily_second_dose_avg'] = temp_state['daily_second_dose'].rolling(window=7).mean()
	
	temp_state.index = temp_state['DATE_AS_AT']
	temp_state = temp_state.reindex(date_index)
	# temp_state['second_dose_estimate'] = temp_state.apply(makeSecondDoses, axis=1)
	
	temp_projections = temp_state.copy()
	
	to_chart = ['SECOND_DOSE_COUNT','FIRST_DOSE_COUNT']
	
	for day in range(0,14):
		print(day)
		temp_projections[f'second_dose_projection_{day}'] = 0
		temp_projections[f'first_dose_projection_{day}'] = 0
		current_proj = newProjectionsDf[(newProjectionsDf['day'] == day) & (newProjectionsDf['state'] == state)]
		print(current_proj)
		eighty_target = current_proj['eighty_target'].iloc[0]
		cutoff_date = current_proj['cutoff'].iloc[0]
		temp_projections[cutoff_date:][f'second_dose_projection_{day}'] = current_proj['second_doses_rate_needed'].iloc[0]
		temp_projections[cutoff_date:][f'first_dose_projection_{day}'] = current_proj['current_rolling'].iloc[0]
		
		temp_projections.at[cutoff_date,f'second_dose_projection_{day}'] = temp_projections.at[cutoff_date,'SECOND_DOSE_COUNT']
		temp_projections.at[cutoff_date,f'first_dose_projection_{day}'] = temp_projections.at[cutoff_date,'FIRST_DOSE_COUNT']
	
		temp_projections[f'cumulative_second_dose_projection_{day}'] = temp_projections[f'second_dose_projection_{day}'].cumsum()
		temp_projections[f'cumulative_first_dose_projection_{day}'] = temp_projections[f'first_dose_projection_{day}'].cumsum()
		
		temp_projections[f'cumulative_second_dose_projection_{day}']['2021-07-01':cutoff_date] = None
		temp_projections[f'cumulative_first_dose_projection_{day}']['2021-07-01':cutoff_date] = None
		
		temp_projections[f'cumulative_second_dose_projection_{day}'][temp_projections[f'cumulative_second_dose_projection_{day}'] > eighty_target] = None
		temp_projections[f'cumulative_first_dose_projection_{day}'][temp_projections[f'cumulative_first_dose_projection_{day}'] > eighty_target] = None
		to_chart.append(f'cumulative_first_dose_projection_{day}')
		to_chart.append(f'cumulative_second_dose_projection_{day}')
	
	
	other_chart = ['SECOND_DOSE_COUNT','FIRST_DOSE_COUNT','cumulative_first_dose_projection_0', 'cumulative_first_dose_projection_6', 'cumulative_second_dose_projection_0','cumulative_second_dose_projection_6']	
	fig = px.line(temp_projections,
				  title=f"Second dose projections for {state}", 
				  x=temp_projections.index, y=other_chart)
	# fig.layout.update(showlegend=False)
	fig.show()

makeStateChart("NT")

# #%%

# # Make total projection col





# temp_projections['pop'] = sixteen_pop[state]
# temp_projections['second_dose_pct_proj'] = temp_projections['cumulative_second_dose_projection'] / temp_projections['pop'] * 100
# temp_projections['first_dose_pct_proj'] = temp_projections['cumulative_first_dose_projection'] / temp_projections['pop'] * 100

# # to_80 = temp_projections[temp_projections['second_dose_pct_proj'] <= 81]
# to_80 = temp_projections.copy()
# to_80['cumulative_second_dose_projection']['2021-07-01':current_date] = None
# to_80['cumulative_first_dose_projection']['2021-07-01':current_date] = None
# to_80['cumulative_second_dose_projection_rolling']['2021-07-01':current_date] = None

# to_80['cumulative_first_dose_projection'][to_80['cumulative_first_dose_projection'] > eighty_target] = None
# to_80['cumulative_second_dose_projection'][to_80['cumulative_second_dose_projection'] > eighty_target] = None
# to_80['cumulative_second_dose_projection_rolling'][to_80['cumulative_second_dose_projection_rolling'] > eighty_target] = None

# # temp_projections = temp_projections[temp_projections['second_dose_pct_proj'] <= 81]


# #%%


# fig = px.line(to_80,
# 			  title=f"Second dose projections for {state}", 
# 			  x=to_80.index, y=['SECOND_DOSE_COUNT','cumulative_second_dose_projection','cumulative_second_dose_projection_rolling','FIRST_DOSE_COUNT','cumulative_first_dose_projection']
# 			  )
# fig.data[0].name = "Second dose count"
# fig.data[1].name = "Second dose projected"
# fig.data[2].name = "Second dose avg proj"
# fig.data[3].name = "First dose count"
# fig.data[4].name = "First dose projected"
# fig.show()

# # fig.write_html("second-dose-projections.html")


# 		