#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def makeProjection(df, cutoff_date):
	
	# variables set up for state projections
	
	today = datetime.datetime.today().date()
	
	# assumptions_cutoff = datetime.datetime.strptime("2021-09-01", "%Y-%m-%d")
	end_year = datetime.datetime.strptime("2022-01-01", "%Y-%m-%d")
	temp_state = df.copy()
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
	eighty_target = sixteen_pop[state] * 0.8
	seventy_target = sixteen_pop[state] * 0.7
	print("eighty_target", eighty_target)
	eighty_vax_to_go = eighty_target - current_first_doses
	seventy_vax_to_go = seventy_target - current_first_doses
	print("eighty_vax_to_go",eighty_vax_to_go)
	
	if (eighty_vax_to_go < 0):
		print("80 target already reached")
		days_to_go_80 = 0
		eighty_finish_first = temp_state[temp_state['FIRST_DOSE_COUNT'] > eighty_target]['DATE_AS_AT'].iloc[0]
		print(eighty_finish_first)
	else:
		print("80 target not yet reached")
		days_to_go_80 = int(round(eighty_vax_to_go / current_rolling,0)) + 1
		print("days to go 80", days_to_go_80)
		eighty_finish_first = current_date + datetime.timedelta(days=days_to_go_80) 
		print("eighty_finish_first", eighty_finish_first)
	if (seventy_vax_to_go < 0):
		print("70 target already reached")
		days_to_go_70 = 0
		seventy_finish_first = temp_state[temp_state['FIRST_DOSE_COUNT'] > seventy_target]['DATE_AS_AT'].iloc[0]
	else:
		print("70 target not yet reached")
		days_to_go_70 = int(round(seventy_vax_to_go / current_rolling,0)) + 1
		seventy_finish_first = current_date + datetime.timedelta(days=days_to_go_70) 
		print("days to go 70", days_to_go_70)

	
	eighty_vax_to_go_second = int(eighty_target - current_second_doses)
	seventy_vax_to_go_second = int(seventy_target - current_second_doses)

	print("eighty_vax_to_go_second", eighty_vax_to_go_second, "seventy_vax_to_go_second", seventy_vax_to_go_second)
	
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
	
	
# 	print("days_to_second_80", days_to_second_80)
# 	print("eighty_finish_second",eighty_finish_second)

# 	
# 	eighty_vax_to_go_second = int(eighty_target - current_second_doses)
# 	print(eighty_vax_to_go_second,days_to_go_80,current_lag)
	second_doses_rate_needed = int(round(eighty_vax_to_go_second / days_to_second_80,0))
# 	print("eighty_finish", eighty_finish_second)
	results = {"current_lag":current_lag, "eighty_finish_first": eighty_finish_first, "seventy_finish_first":seventy_finish_first, "eighty_finish_second":eighty_finish_second, "seventy_finish_second":seventy_finish_second, "current_rolling":current_rolling, "second_doses_rate_needed":second_doses_rate_needed,"eighty_target":eighty_target, "seventy_target":seventy_target, "seventy_reached":seventy_reached, "eighty_reached":eighty_reached}
# 	print(results)
	return results
