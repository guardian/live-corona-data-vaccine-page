import datetime

day = datetime.datetime.today().weekday()
print("Date of the week: ", day)

import oecd_total_bar
import fixed_weekly_global_bar

# day = 5


if day >= 0:

    import weekly.WEEKLY_cases_bar
    import weekly.WEEKLY_covid_hospo_per_100k

    import weekly.WEEKLY_deaths_bar
    import weekly.WEEKLY_hospo_states_selector

    import weekly.WEEKLY_thrasher_feed
    import weekly.WEEKLY_vax_rollout
    import new_table_incl_fourth