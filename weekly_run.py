import datetime

day = datetime.datetime.today().weekday()

import weekly.WEEKLY_vax_rollout

import oecd_total_bar
import new_table_incl_fourth


if day > 1:
  import weekly.WEEKLY_cases_bar
  import weekly.WEEKLY_covid_hospo_per_100k

  import weekly.WEEKLY_deaths_bar
  import weekly.WEEKLY_hospo_states_selector

  import weekly.WEEKLY_thrasher_feed