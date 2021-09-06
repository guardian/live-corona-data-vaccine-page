
# %%
import pandas as pd 
import datetime

today = datetime.datetime.today().date()

sixteen_pop = {
    'NT':190571, 'NSW':6565651, 'VIC':5407574,
    'QLD':4112707, 'ACT':344037,
    'SA':1440400, 'WA':2114978, 'TAS':440172, "AUS":20619959}

third = pd.read_json('https://vaccinedata.covid19nearme.com.au/data/air_residence.json')

# 'AIR_RESIDENCE_FIRST_DOSE_APPROX_COUNT',
#        'AIR_RESIDENCE_SECOND_DOSE_APPROX_COUNT', 'ABS_ERP_JUN_2020_POP',
#        'VALIDATED', 'URL', 'AIR_RESIDENCE_FIRST_DOSE_COUNT',
#        'AIR_RESIDENCE_SECOND_DOSE_COUNT'

# %%
second = third.copy()

second['DATE_AS_AT'] = pd.to_datetime(second['DATE_AS_AT'])
second = second.sort_values(by='DATE_AS_AT', ascending=True)

listo = []

for state in second['STATE'].unique().tolist():
    inter = second.loc[second['STATE'] == state].copy()
    to_use = inter.loc[(inter["AGE_LOWER"] == 16) & (inter['AGE_UPPER'] == 999)].copy()

    to_use['Second_new'] = to_use['AIR_RESIDENCE_SECOND_DOSE_COUNT'].diff(1)
    to_use['Second_rolling'] = to_use['Second_new'].rolling(window=7).mean()

    latest = to_use.loc[to_use['DATE_AS_AT'] == to_use['DATE_AS_AT'].max()].copy()
    
    latest = latest[['STATE', 'AIR_RESIDENCE_FIRST_DOSE_PCT', 'AIR_RESIDENCE_SECOND_DOSE_PCT','AIR_RESIDENCE_SECOND_DOSE_COUNT', 'Second_rolling']]

    # print(latest)
    latest_count = latest['AIR_RESIDENCE_SECOND_DOSE_COUNT'].values[0]
    latest_rolling = latest['Second_rolling'].values[0]

    ### WORK OUT HOW MANY MORE DAYS TO GO

    

    eighty_target = sixteen_pop[state] * 0.8
    seventy_target = sixteen_pop[state] * 0.7

    eighty_vax_to_go = eighty_target - latest_count
    seventy_vax_to_go = seventy_target - latest_count



    days_to_go_80 = int(round(eighty_vax_to_go / latest_rolling,0))
    days_to_go_70 = int(round(seventy_vax_to_go / latest_rolling,0))

    eighty_finish = today + datetime.timedelta(days=days_to_go_80)
    seventy_finish = today + datetime.timedelta(days=days_to_go_70)

    eighty_finish = datetime.datetime.strftime(eighty_finish, "%d %B")

    seventy_finish = datetime.datetime.strftime(seventy_finish, "%d %B")

    final = pd.DataFrame.from_dict({"State": state,
                                    "First dose %": latest['AIR_RESIDENCE_FIRST_DOSE_PCT'].values[0],
                                    "Second dose %": latest['AIR_RESIDENCE_SECOND_DOSE_PCT'].values[0],
                                    "Reach 70% on": f"{seventy_finish}",
                                    "Reach 80% on": f"{eighty_finish}"}, orient="index")
                                    # columns=(['Row', "Values"]))

    final = final.T

    listo.append(final)

    
small = pd.concat(listo)




# for state in df['CODE'].unique().tolist():
#     inter = df.loc[df['CODE'] == state].copy()
#     inter['Incremental'] = inter['PREV_VACC_PEOPLE_CNT'].diff(1)
#     inter['Rolling'] = inter['Incremental'].rolling(window=7).mean()

#     # print(inter)

#     latest = inter.loc[inter['REPORT_DATE'] == inter['REPORT_DATE'].max()].copy()

#     latest_count = latest['PREV_VACC_PEOPLE_CNT'].values[0]
#     # latest_counts[state] = latest_count

#     latest_rolling = latest['Rolling'].values[0]

#     # rolling_averages[state] = latest_rolling

#     ### WORK OUT HOW MANY MORE DAYS TO GO

#     eighty_target = sixteen_pop[state] * 0.8
#     seventy_target = sixteen_pop[state] * 0.7

#     eighty_vax_to_go = eighty_target - latest_count
#     seventy_vax_to_go = seventy_target - latest_count

#     days_to_go_80 = int(round(eighty_vax_to_go / latest_rolling,0))
#     days_to_go_70 = int(round(seventy_vax_to_go / latest_rolling,0))

#     eighty_finish = today + datetime.timedelta(days=days_to_go_80)
#     seventy_finish = today + datetime.timedelta(days=days_to_go_70)

#     eighty_finish = datetime.datetime.strftime(eighty_finish, "%d/%m/%Y")

#     seventy_finish = datetime.datetime.strftime(seventy_finish, "%d/%m/%Y")


#     latest_count_hundred = round((latest_count/sixteen_pop[state])*100, 2)

#     latest_rolling = round(latest_rolling,0)

#     final = pd.DataFrame.from_dict({"State": state,
#                                     "Percent of 16+ population fully vaccinated": latest_count_hundred,
#                                     "Seven day average of second doses": latest_rolling,
#                                     "To fully vaccinate 70% of 16+": f"{days_to_go_70} days ({seventy_finish})",
#                                     "To fully vaccinate 80% of 16+": f"{days_to_go_80} days ({eighty_finish})"}, orient="index")
#                                     # columns=(['Row', "Values"]))

#     final = final.T

#     # print(final)

#     listo.append(final)
# %%
