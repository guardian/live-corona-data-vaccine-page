#%%
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
import ssl
from datetime import timedelta
import requests
from modules.yachtCharter import yachtCharter
import datetime 

testo = ''
# testo = '-testo'
#%%

# df = pd.read_csv("https://vaccinedata.covid19nearme.com.au/data/all.csv")
# 'DATE_AS_AT', 'TOTALS_NATIONAL_TOTAL', 'TOTALS_NATIONAL_LAST_24HR', 
# 'TOTALS_CWTH_ALL_TOTAL', 'TOTALS_CWTH_ALL_LAST_24HR', 'TOTALS_CWTH_PRIMARY_CARE_TOTAL', 
# 'TOTALS_CWTH_PRIMARY_CARE_LAST_24HR', 'TOTALS_CWTH_AGED_CARE_TOTAL', 
# 'TOTALS_CWTH_AGED_CARE_LAST_24HR', 'STATE_CLINICS_VIC_TOTAL', 'STATE_CLINICS_VIC_LAST_24HR',
# 'STATE_CLINICS_QLD_TOTAL', 'STATE_CLINICS_QLD_LAST_24HR', 'STATE_CLINICS_WA_TOTAL', 
# 'STATE_CLINICS_WA_LAST_24HR', 'STATE_CLINICS_TAS_TOTAL', 'STATE_CLINICS_TAS_LAST_24HR', 
# 'STATE_CLINICS_SA_TOTAL', 'STATE_CLINICS_SA_LAST_24HR', 'STATE_CLINICS_ACT_TOTAL', 
# 'STATE_CLINICS_ACT_LAST_24HR', 'STATE_CLINICS_NT_TOTAL', 'STATE_CLINICS_NT_LAST_24HR', 
# 'STATE_CLINICS_NSW_TOTAL', 'STATE_CLINICS_NSW_LAST_24HR', 'CWTH_AGED_CARE_VIC_TOTAL', 
# 'CWTH_AGED_CARE_VIC_LAST_24HR', 'CWTH_AGED_CARE_QLD_TOTAL', 'CWTH_AGED_CARE_QLD_LAST_24HR',
# 'CWTH_AGED_CARE_WA_TOTAL', 'CWTH_AGED_CARE_WA_LAST_24HR', 'CWTH_AGED_CARE_TAS_TOTAL', 
# 'CWTH_AGED_CARE_TAS_LAST_24HR', 'CWTH_AGED_CARE_SA_TOTAL', 'CWTH_AGED_CARE_SA_LAST_24HR',
# 'CWTH_AGED_CARE_ACT_TOTAL', 'CWTH_AGED_CARE_ACT_LAST_24HR', 'CWTH_AGED_CARE_NT_TOTAL', 
# 'CWTH_AGED_CARE_NT_LAST_24HR', 'CWTH_AGED_CARE_NSW_TOTAL', 'CWTH_AGED_CARE_NSW_LAST_24HR', 
# 'CWTH_PRIMARY_CARE_VIC_TOTAL', 'CWTH_PRIMARY_CARE_VIC_LAST_24HR', 'CWTH_PRIMARY_CARE_QLD_TOTAL',
# 'CWTH_PRIMARY_CARE_QLD_LAST_24HR', 'CWTH_PRIMARY_CARE_WA_TOTAL', 'CWTH_PRIMARY_CARE_WA_LAST_24HR',
# 'CWTH_PRIMARY_CARE_TAS_TOTAL', 'CWTH_PRIMARY_CARE_TAS_LAST_24HR', 'CWTH_PRIMARY_CARE_SA_TOTAL', 
# 'CWTH_PRIMARY_CARE_SA_LAST_24HR', 'CWTH_PRIMARY_CARE_ACT_TOTAL', 'CWTH_PRIMARY_CARE_ACT_LAST_24HR',
# 'CWTH_PRIMARY_CARE_NT_TOTAL', 'CWTH_PRIMARY_CARE_NT_LAST_24HR', 'CWTH_PRIMARY_CARE_NSW_TOTAL', 
# 'CWTH_PRIMARY_CARE_NSW_LAST_24HR', 'CWTH_AGED_CARE_DOSES_FIRST_DOSE', 
# 'CWTH_AGED_CARE_DOSES_SECOND_DOSE', 'CWTH_AGED_CARE_FACILITIES_FIRST_DOSE',
# 'CWTH_AGED_CARE_FACILITIES_SECOND_DOSE', 'APPROX_VIC_SECOND_DOSE_TOTAL', 
# 'APPROX_QLD_SECOND_DOSE_TOTAL', 'APPROX_WA_SECOND_DOSE_TOTAL', 'APPROX_TAS_SECOND_DOSE_TOTAL',
# 'APPROX_SA_SECOND_DOSE_TOTAL', 'APPROX_ACT_SECOND_DOSE_TOTAL', 'APPROX_NT_SECOND_DOSE_TOTAL',
# 'APPROX_NSW_SECOND_DOSE_TOTAL', 'FIRST_NATIONS_VIC_FIRST_DOSE_TOTAL', 
# 'FIRST_NATIONS_VIC_SECOND_DOSE_TOTAL', 'FIRST_NATIONS_QLD_FIRST_DOSE_TOTAL',
# 'FIRST_NATIONS_QLD_SECOND_DOSE_TOTAL', 'FIRST_NATIONS_WA_FIRST_DOSE_TOTAL', 
# 'FIRST_NATIONS_WA_SECOND_DOSE_TOTAL', 'FIRST_NATIONS_TAS_FIRST_DOSE_TOTAL',
# 'FIRST_NATIONS_TAS_SECOND_DOSE_TOTAL', 'FIRST_NATIONS_SA_FIRST_DOSE_TOTAL', 
# 'FIRST_NATIONS_SA_SECOND_DOSE_TOTAL', 'FIRST_NATIONS_ACT_FIRST_DOSE_TOTAL', 
# 'FIRST_NATIONS_ACT_SECOND_DOSE_TOTAL', 'FIRST_NATIONS_NT_FIRST_DOSE_TOTAL', 
# 'FIRST_NATIONS_NT_SECOND_DOSE_TOTAL', 'FIRST_NATIONS_NSW_FIRST_DOSE_TOTAL', 
# 'FIRST_NATIONS_NSW_SECOND_DOSE_TOTAL', 'FIRST_NATIONS_AUS_FIRST_DOSE_TOTAL', 
# 'FIRST_NATIONS_AUS_SECOND_DOSE_TOTAL', 'FIRST_NATIONS_VIC_FIRST_PCT_TOTAL', 
# 'FIRST_NATIONS_VIC_SECOND_PCT_TOTAL', 'FIRST_NATIONS_QLD_FIRST_PCT_TOTAL', 
# 'FIRST_NATIONS_QLD_SECOND_PCT_TOTAL', 'FIRST_NATIONS_WA_FIRST_PCT_TOTAL', 
# 'FIRST_NATIONS_WA_SECOND_PCT_TOTAL', 'FIRST_NATIONS_TAS_FIRST_PCT_TOTAL', 
# 'FIRST_NATIONS_TAS_SECOND_PCT_TOTAL', 'FIRST_NATIONS_SA_FIRST_PCT_TOTAL', 
# 'FIRST_NATIONS_SA_SECOND_PCT_TOTAL', 'FIRST_NATIONS_ACT_FIRST_PCT_TOTAL', 
# 'FIRST_NATIONS_ACT_SECOND_PCT_TOTAL', 'FIRST_NATIONS_NT_FIRST_PCT_TOTAL', 
# 'FIRST_NATIONS_NT_SECOND_PCT_TOTAL', 'FIRST_NATIONS_NSW_FIRST_PCT_TOTAL',
# 'FIRST_NATIONS_NSW_SECOND_PCT_TOTAL', 'FIRST_NATIONS_AUS_FIRST_PCT_TOTAL', 
# 'FIRST_NATIONS_AUS_SECOND_PCT_TOTAL', 'VALIDATED', 'URL'


# df = pd.read_json('https://vaccinedata.covid19nearme.com.au/data/air.json')
# 'DATE_AS_AT', 'AIR_95_PLUS_FIRST_DOSE_COUNT', 'AIR_95_PLUS_FIRST_DOSE_PCT',
# 'AIR_95_PLUS_SECOND_DOSE_COUNT', 'AIR_95_PLUS_SECOND_DOSE_PCT', 
# 'AIR_95_PLUS_FEMALE_PCT', 'AIR_95_PLUS_MALE_PCT', 'AIR_90_94_FIRST_DOSE_COUNT',
# 'AIR_90_94_FIRST_DOSE_PCT', 'AIR_90_94_SECOND_DOSE_COUNT', 'AIR_90_94_SECOND_DOSE_PCT',
# 'AIR_90_94_FEMALE_PCT', 'AIR_90_94_MALE_PCT', 'AIR_85_89_FIRST_DOSE_COUNT',
# 'AIR_85_89_FIRST_DOSE_PCT', 'AIR_85_89_SECOND_DOSE_COUNT', 'AIR_85_89_SECOND_DOSE_PCT',
# 'AIR_85_89_FEMALE_PCT', 'AIR_85_89_MALE_PCT', 'AIR_80_84_FIRST_DOSE_COUNT', 
# 'AIR_80_84_FIRST_DOSE_PCT', 'AIR_80_84_SECOND_DOSE_COUNT', 'AIR_80_84_SECOND_DOSE_PCT',
# 'AIR_80_84_FEMALE_PCT', 'AIR_80_84_MALE_PCT', 'AIR_75_79_FIRST_DOSE_COUNT', 
# 'AIR_75_79_FIRST_DOSE_PCT', 'AIR_75_79_SECOND_DOSE_COUNT', 'AIR_75_79_SECOND_DOSE_PCT',
# 'AIR_75_79_FEMALE_PCT', 'AIR_75_79_MALE_PCT', 'AIR_70_74_FIRST_DOSE_COUNT',
# 'AIR_70_74_FIRST_DOSE_PCT', 'AIR_70_74_SECOND_DOSE_COUNT', 'AIR_70_74_SECOND_DOSE_PCT',
# 'AIR_70_74_FEMALE_PCT', 'AIR_70_74_MALE_PCT', 'AIR_65_69_FIRST_DOSE_COUNT', 
# 'AIR_65_69_FIRST_DOSE_PCT', 'AIR_65_69_SECOND_DOSE_COUNT', 'AIR_65_69_SECOND_DOSE_PCT', 
# 'AIR_65_69_FEMALE_PCT', 'AIR_65_69_MALE_PCT', 'AIR_60_64_FIRST_DOSE_COUNT', 
# 'AIR_60_64_FIRST_DOSE_PCT', 'AIR_60_64_SECOND_DOSE_COUNT', 'AIR_60_64_SECOND_DOSE_PCT',
# 'AIR_60_64_FEMALE_PCT', 'AIR_60_64_MALE_PCT', 'AIR_55_59_FIRST_DOSE_COUNT', 
# 'AIR_55_59_FIRST_DOSE_PCT', 'AIR_55_59_SECOND_DOSE_COUNT', 'AIR_55_59_SECOND_DOSE_PCT',
# 'AIR_55_59_FEMALE_PCT', 'AIR_55_59_MALE_PCT', 'AIR_50_54_FIRST_DOSE_COUNT', 
# 'AIR_50_54_FIRST_DOSE_PCT', 'AIR_50_54_SECOND_DOSE_COUNT', 'AIR_50_54_SECOND_DOSE_PCT',
# 'AIR_50_54_FEMALE_PCT', 'AIR_50_54_MALE_PCT', 'AIR_45_49_FIRST_DOSE_COUNT', 
# 'AIR_45_49_FIRST_DOSE_PCT', 'AIR_45_49_SECOND_DOSE_COUNT', 'AIR_45_49_SECOND_DOSE_PCT',
# 'AIR_45_49_FEMALE_PCT', 'AIR_45_49_MALE_PCT', 'AIR_40_44_FIRST_DOSE_COUNT', 
# 'AIR_40_44_FIRST_DOSE_PCT', 'AIR_40_44_SECOND_DOSE_COUNT', 'AIR_40_44_SECOND_DOSE_PCT', 
# 'AIR_40_44_FEMALE_PCT', 'AIR_40_44_MALE_PCT', 'AIR_35_39_FIRST_DOSE_COUNT', 
# 'AIR_35_39_FIRST_DOSE_PCT', 'AIR_35_39_SECOND_DOSE_COUNT', 'AIR_35_39_SECOND_DOSE_PCT', 
# 'AIR_35_39_FEMALE_PCT', 'AIR_35_39_MALE_PCT', 'AIR_30_34_FIRST_DOSE_COUNT', 
# 'AIR_30_34_FIRST_DOSE_PCT', 'AIR_30_34_SECOND_DOSE_COUNT', 'AIR_30_34_SECOND_DOSE_PCT', 
# 'AIR_30_34_FEMALE_PCT', 'AIR_30_34_MALE_PCT', 'AIR_25_29_FIRST_DOSE_COUNT', 
# 'AIR_25_29_FIRST_DOSE_PCT', 'AIR_25_29_SECOND_DOSE_COUNT', 'AIR_25_29_SECOND_DOSE_PCT', 
# 'AIR_25_29_FEMALE_PCT', 'AIR_25_29_MALE_PCT', 'AIR_20_24_FIRST_DOSE_COUNT', 
# 'AIR_20_24_FIRST_DOSE_PCT', 'AIR_20_24_SECOND_DOSE_COUNT', 'AIR_20_24_SECOND_DOSE_PCT', 
# 'AIR_20_24_FEMALE_PCT', 'AIR_20_24_MALE_PCT', 'AIR_16_19_FIRST_DOSE_COUNT', 
# 'AIR_16_19_FIRST_DOSE_PCT', 'AIR_16_19_SECOND_DOSE_COUNT', 'AIR_16_19_SECOND_DOSE_PCT', 
# 'AIR_16_19_FEMALE_PCT', 'AIR_16_19_MALE_PCT', 'VALIDATED', 'URL', 
# 'AIR_NSW_16_PLUS_FIRST_DOSE_COUNT', 'AIR_NSW_16_PLUS_FIRST_DOSE_PCT', 
# 'AIR_NSW_16_PLUS_SECOND_DOSE_COUNT', 'AIR_NSW_16_PLUS_SECOND_DOSE_PCT', 
# 'AIR_NSW_16_PLUS_POPULATION', 'AIR_VIC_16_PLUS_FIRST_DOSE_COUNT', 'AIR_VIC_16_PLUS_FIRST_DOSE_PCT',
# 'AIR_VIC_16_PLUS_SECOND_DOSE_COUNT', 'AIR_VIC_16_PLUS_SECOND_DOSE_PCT', 
# 'AIR_VIC_16_PLUS_POPULATION', 'AIR_QLD_16_PLUS_FIRST_DOSE_COUNT', 'AIR_QLD_16_PLUS_FIRST_DOSE_PCT',
# 'AIR_QLD_16_PLUS_SECOND_DOSE_COUNT', 'AIR_QLD_16_PLUS_SECOND_DOSE_PCT', 
# 'AIR_QLD_16_PLUS_POPULATION', 'AIR_WA_16_PLUS_FIRST_DOSE_COUNT', 'AIR_WA_16_PLUS_FIRST_DOSE_PCT', 
# 'AIR_WA_16_PLUS_SECOND_DOSE_COUNT', 'AIR_WA_16_PLUS_SECOND_DOSE_PCT', 'AIR_WA_16_PLUS_POPULATION',
# 'AIR_TAS_16_PLUS_FIRST_DOSE_COUNT', 'AIR_TAS_16_PLUS_FIRST_DOSE_PCT', 
# 'AIR_TAS_16_PLUS_SECOND_DOSE_COUNT', 'AIR_TAS_16_PLUS_SECOND_DOSE_PCT', 
# 'AIR_TAS_16_PLUS_POPULATION', 'AIR_SA_16_PLUS_FIRST_DOSE_COUNT', 'AIR_SA_16_PLUS_FIRST_DOSE_PCT',
# 'AIR_SA_16_PLUS_SECOND_DOSE_COUNT', 'AIR_SA_16_PLUS_SECOND_DOSE_PCT', 'AIR_SA_16_PLUS_POPULATION',
# 'AIR_ACT_16_PLUS_FIRST_DOSE_COUNT', 'AIR_ACT_16_PLUS_FIRST_DOSE_PCT',
# 'AIR_ACT_16_PLUS_SECOND_DOSE_COUNT', 'AIR_ACT_16_PLUS_SECOND_DOSE_PCT', 
# 'AIR_ACT_16_PLUS_POPULATION', 'AIR_NT_16_PLUS_FIRST_DOSE_COUNT', 'AIR_NT_16_PLUS_FIRST_DOSE_PCT', 
# 'AIR_NT_16_PLUS_SECOND_DOSE_COUNT', 'AIR_NT_16_PLUS_SECOND_DOSE_PCT', 
# 'AIR_NT_16_PLUS_POPULATION', 'AIR_NSW_50_PLUS_FIRST_DOSE_COUNT', 'AIR_NSW_50_PLUS_FIRST_DOSE_PCT', 
# 'AIR_NSW_50_PLUS_SECOND_DOSE_COUNT', 'AIR_NSW_50_PLUS_SECOND_DOSE_PCT', 
# 'AIR_NSW_50_PLUS_POPULATION', 'AIR_VIC_50_PLUS_FIRST_DOSE_COUNT', 'AIR_VIC_50_PLUS_FIRST_DOSE_PCT', 
# 'AIR_VIC_50_PLUS_SECOND_DOSE_COUNT', 'AIR_VIC_50_PLUS_SECOND_DOSE_PCT', 'AIR_VIC_50_PLUS_POPULATION',
# 'AIR_QLD_50_PLUS_FIRST_DOSE_COUNT', 'AIR_QLD_50_PLUS_FIRST_DOSE_PCT', 'AIR_QLD_50_PLUS_SECOND_DOSE_COUNT',
# 'AIR_QLD_50_PLUS_SECOND_DOSE_PCT', 'AIR_QLD_50_PLUS_POPULATION', 'AIR_WA_50_PLUS_FIRST_DOSE_COUNT',
# 'AIR_WA_50_PLUS_FIRST_DOSE_PCT', 'AIR_WA_50_PLUS_SECOND_DOSE_COUNT', 'AIR_WA_50_PLUS_SECOND_DOSE_PCT',
# 'AIR_WA_50_PLUS_POPULATION', 'AIR_TAS_50_PLUS_FIRST_DOSE_COUNT', 'AIR_TAS_50_PLUS_FIRST_DOSE_PCT',
# 'AIR_TAS_50_PLUS_SECOND_DOSE_COUNT', 'AIR_TAS_50_PLUS_SECOND_DOSE_PCT', 'AIR_TAS_50_PLUS_POPULATION',
# 'AIR_SA_50_PLUS_FIRST_DOSE_COUNT', 'AIR_SA_50_PLUS_FIRST_DOSE_PCT', 'AIR_SA_50_PLUS_SECOND_DOSE_COUNT',
# 'AIR_SA_50_PLUS_SECOND_DOSE_PCT', 'AIR_SA_50_PLUS_POPULATION', 'AIR_ACT_50_PLUS_FIRST_DOSE_COUNT', 
# 'AIR_ACT_50_PLUS_FIRST_DOSE_PCT', 'AIR_ACT_50_PLUS_SECOND_DOSE_COUNT', 'AIR_ACT_50_PLUS_SECOND_DOSE_PCT',
# 'AIR_ACT_50_PLUS_POPULATION', 'AIR_NT_50_PLUS_FIRST_DOSE_COUNT', 'AIR_NT_50_PLUS_FIRST_DOSE_PCT',
# 'AIR_NT_50_PLUS_SECOND_DOSE_COUNT', 'AIR_NT_50_PLUS_SECOND_DOSE_PCT', 'AIR_NT_50_PLUS_POPULATION',
# 'AIR_NSW_70_PLUS_FIRST_DOSE_COUNT', 'AIR_NSW_70_PLUS_FIRST_DOSE_PCT', 
# 'AIR_NSW_70_PLUS_SECOND_DOSE_COUNT', 'AIR_NSW_70_PLUS_SECOND_DOSE_PCT', 'AIR_NSW_70_PLUS_POPULATION',
# 'AIR_VIC_70_PLUS_FIRST_DOSE_COUNT', 'AIR_VIC_70_PLUS_FIRST_DOSE_PCT', 
# 'AIR_VIC_70_PLUS_SECOND_DOSE_COUNT', 'AIR_VIC_70_PLUS_SECOND_DOSE_PCT', 'AIR_VIC_70_PLUS_POPULATION',
# 'AIR_QLD_70_PLUS_FIRST_DOSE_COUNT', 'AIR_QLD_70_PLUS_FIRST_DOSE_PCT', 
# 'AIR_QLD_70_PLUS_SECOND_DOSE_COUNT', 'AIR_QLD_70_PLUS_SECOND_DOSE_PCT', 
# 'AIR_QLD_70_PLUS_POPULATION', 'AIR_WA_70_PLUS_FIRST_DOSE_COUNT', 'AIR_WA_70_PLUS_FIRST_DOSE_PCT',
# 'AIR_WA_70_PLUS_SECOND_DOSE_COUNT', 'AIR_WA_70_PLUS_SECOND_DOSE_PCT', 'AIR_WA_70_PLUS_POPULATION',
# 'AIR_TAS_70_PLUS_FIRST_DOSE_COUNT', 'AIR_TAS_70_PLUS_FIRST_DOSE_PCT', 
# 'AIR_TAS_70_PLUS_SECOND_DOSE_COUNT', 'AIR_TAS_70_PLUS_SECOND_DOSE_PCT', 
# 'AIR_TAS_70_PLUS_POPULATION', 'AIR_SA_70_PLUS_FIRST_DOSE_COUNT', 'AIR_SA_70_PLUS_FIRST_DOSE_PCT'
# 'AIR_SA_70_PLUS_SECOND_DOSE_COUNT', 'AIR_SA_70_PLUS_SECOND_DOSE_PCT', 'AIR_SA_70_PLUS_POPULATION',
# 'AIR_ACT_70_PLUS_FIRST_DOSE_COUNT', 'AIR_ACT_70_PLUS_FIRST_DOSE_PCT', 'AIR_ACT_70_PLUS_SECOND_DOSE_COUNT'
# 'AIR_ACT_70_PLUS_SECOND_DOSE_PCT', 'AIR_ACT_70_PLUS_POPULATION', 'AIR_NT_70_PLUS_FIRST_DOSE_COUNT',
# 'AIR_NT_70_PLUS_FIRST_DOSE_PCT', 'AIR_NT_70_PLUS_SECOND_DOSE_COUNT', 'AIR_NT_70_PLUS_SECOND_DOSE_PCT',
# 'AIR_NT_70_PLUS_POPULATION', 'AIR_AUS_16_PLUS_FIRST_DOSE_COUNT', 'AIR_AUS_16_PLUS_FIRST_DOSE_PCT', 
# 'AIR_AUS_16_PLUS_SECOND_DOSE_COUNT', 'AIR_AUS_16_PLUS_SECOND_DOSE_PCT', 'AIR_AUS_16_PLUS_POPULATION',
# 'AIR_AUS_50_PLUS_FIRST_DOSE_COUNT', 'AIR_AUS_50_PLUS_FIRST_DOSE_PCT', 'AIR_AUS_50_PLUS_SECOND_DOSE_COUNT',
# 'AIR_AUS_50_PLUS_SECOND_DOSE_PCT', 'AIR_AUS_50_PLUS_POPULATION', 'AIR_AUS_70_PLUS_FIRST_DOSE_COUNT', 
# 'AIR_AUS_70_PLUS_FIRST_DOSE_PCT', 'AIR_AUS_70_PLUS_SECOND_DOSE_COUNT', 'AIR_AUS_70_PLUS_SECOND_DOSE_PCT',
# 'AIR_AUS_70_PLUS_POPULATION', 'AIR_12_15_FIRST_DOSE_COUNT', 'AIR_12_15_FIRST_DOSE_PCT', 
# 'AIR_12_15_SECOND_DOSE_COUNT', 'AIR_12_15_SECOND_DOSE_PCT', 'AIR_12_15_FEMALE_PCT', 'AIR_12_15_MALE_PCT',
# 'AIR_NSW_12_15_FIRST_DOSE_COUNT', 'AIR_NSW_12_15_FIRST_DOSE_PCT', 'AIR_NSW_12_15_SECOND_DOSE_COUNT', 
# 'AIR_NSW_12_15_SECOND_DOSE_PCT', 'AIR_NSW_12_15_POPULATION', 'AIR_VIC_12_15_FIRST_DOSE_COUNT',
# 'AIR_VIC_12_15_FIRST_DOSE_PCT', 'AIR_VIC_12_15_SECOND_DOSE_COUNT', 'AIR_VIC_12_15_SECOND_DOSE_PCT',
# 'AIR_VIC_12_15_POPULATION', 'AIR_QLD_12_15_FIRST_DOSE_COUNT', 'AIR_QLD_12_15_FIRST_DOSE_PCT',
# 'AIR_QLD_12_15_SECOND_DOSE_COUNT', 'AIR_QLD_12_15_SECOND_DOSE_PCT', 'AIR_QLD_12_15_POPULATION',
# 'AIR_WA_12_15_FIRST_DOSE_COUNT', 'AIR_WA_12_15_FIRST_DOSE_PCT', 'AIR_WA_12_15_SECOND_DOSE_COUNT',
# 'AIR_WA_12_15_SECOND_DOSE_PCT', 'AIR_WA_12_15_POPULATION', 'AIR_TAS_12_15_FIRST_DOSE_COUNT',
# 'AIR_TAS_12_15_FIRST_DOSE_PCT', 'AIR_TAS_12_15_SECOND_DOSE_COUNT', 'AIR_TAS_12_15_SECOND_DOSE_PCT',
# 'AIR_TAS_12_15_POPULATION', 'AIR_SA_12_15_FIRST_DOSE_COUNT', 'AIR_SA_12_15_FIRST_DOSE_PCT',
# 'AIR_SA_12_15_SECOND_DOSE_COUNT', 'AIR_SA_12_15_SECOND_DOSE_PCT', 'AIR_SA_12_15_POPULATION',
# 'AIR_ACT_12_15_FIRST_DOSE_COUNT', 'AIR_ACT_12_15_FIRST_DOSE_PCT', 'AIR_ACT_12_15_SECOND_DOSE_COUNT',
# 'AIR_ACT_12_15_SECOND_DOSE_PCT', 'AIR_ACT_12_15_POPULATION', 'AIR_NT_12_15_FIRST_DOSE_COUNT', 
# 'AIR_NT_12_15_FIRST_DOSE_PCT', 'AIR_NT_12_15_SECOND_DOSE_COUNT', 'AIR_NT_12_15_SECOND_DOSE_PCT', 
# 'AIR_NT_12_15_POPULATION', 'AIR_AUS_12_15_FIRST_DOSE_COUNT', 'AIR_AUS_12_15_FIRST_DOSE_PCT', 
# 'AIR_AUS_12_15_SECOND_DOSE_COUNT', 'AIR_AUS_12_15_SECOND_DOSE_PCT', 'AIR_AUS_12_15_FEMALE_PCT', 
# 'AIR_AUS_12_15_MALE_PCT', 'AIR_AUS_16_PLUS_THIRD_DOSE_COUNT', 'AIR_AUS_16_PLUS_THIRD_DOSE_PCT', 
# 'AIR_AUS_18_PLUS_THIRD_DOSE_COUNT', 'AIR_AUS_18_PLUS_THIRD_DOSE_PCT', 'AIR_NSW_18_PLUS_THIRD_DOSE_COUNT',
# 'AIR_NSW_18_PLUS_THIRD_DOSE_PCT', 'AIR_VIC_18_PLUS_THIRD_DOSE_COUNT', 'AIR_VIC_18_PLUS_THIRD_DOSE_PCT',
# 'AIR_QLD_18_PLUS_THIRD_DOSE_COUNT', 'AIR_QLD_18_PLUS_THIRD_DOSE_PCT', 'AIR_WA_18_PLUS_THIRD_DOSE_COUNT',
# 'AIR_WA_18_PLUS_THIRD_DOSE_PCT', 'AIR_TAS_18_PLUS_THIRD_DOSE_COUNT', 'AIR_TAS_18_PLUS_THIRD_DOSE_PCT',
# 'AIR_SA_18_PLUS_THIRD_DOSE_COUNT', 'AIR_SA_18_PLUS_THIRD_DOSE_PCT', 'AIR_ACT_18_PLUS_THIRD_DOSE_COUNT',
# 'AIR_ACT_18_PLUS_THIRD_DOSE_PCT', 'AIR_NT_18_PLUS_THIRD_DOSE_COUNT', 'AIR_NT_18_PLUS_THIRD_DOSE_PCT',
# 'AIR_AUS_5_11_FIRST_DOSE_COUNT', 'AIR_AUS_5_11_FIRST_DOSE_PCT', 'AIR_AUS_5_11_POPULATION', 
# 'AIR_NSW_5_11_FIRST_DOSE_COUNT', 'AIR_NSW_5_11_FIRST_DOSE_PCT', 'AIR_NSW_5_11_POPULATION', 
# 'AIR_VIC_5_11_FIRST_DOSE_COUNT', 'AIR_VIC_5_11_FIRST_DOSE_PCT', 'AIR_VIC_5_11_POPULATION', 
# 'AIR_QLD_5_11_FIRST_DOSE_COUNT', 'AIR_QLD_5_11_FIRST_DOSE_PCT', 'AIR_QLD_5_11_POPULATION', 
# 'AIR_WA_5_11_FIRST_DOSE_COUNT', 'AIR_WA_5_11_FIRST_DOSE_PCT', 'AIR_WA_5_11_POPULATION', 
# 'AIR_TAS_5_11_FIRST_DOSE_COUNT', 'AIR_TAS_5_11_FIRST_DOSE_PCT', 'AIR_TAS_5_11_POPULATION', 
# 'AIR_SA_5_11_FIRST_DOSE_COUNT', 'AIR_SA_5_11_FIRST_DOSE_PCT', 'AIR_SA_5_11_POPULATION', 
# 'AIR_ACT_5_11_FIRST_DOSE_COUNT', 'AIR_ACT_5_11_FIRST_DOSE_PCT', 'AIR_ACT_5_11_POPULATION', 
# 'AIR_NT_5_11_FIRST_DOSE_COUNT', 'AIR_NT_5_11_FIRST_DOSE_PCT', 'AIR_NT_5_11_POPULATION', 
# 'AIR_AUS_5_11_SECOND_DOSE_COUNT', 'AIR_AUS_5_11_SECOND_DOSE_PCT', 'AIR_NSW_5_11_SECOND_DOSE_COUNT', 
# 'AIR_NSW_5_11_SECOND_DOSE_PCT', 'AIR_VIC_5_11_SECOND_DOSE_COUNT', 'AIR_VIC_5_11_SECOND_DOSE_PCT',
# 'AIR_QLD_5_11_SECOND_DOSE_COUNT', 'AIR_QLD_5_11_SECOND_DOSE_PCT', 'AIR_WA_5_11_SECOND_DOSE_COUNT', 
# 'AIR_WA_5_11_SECOND_DOSE_PCT', 'AIR_TAS_5_11_SECOND_DOSE_COUNT', 'AIR_TAS_5_11_SECOND_DOSE_PCT',
# 'AIR_SA_5_11_SECOND_DOSE_COUNT', 'AIR_SA_5_11_SECOND_DOSE_PCT', 'AIR_ACT_5_11_SECOND_DOSE_COUNT', 
# 'AIR_ACT_5_11_SECOND_DOSE_PCT', 'AIR_NT_5_11_SECOND_DOSE_COUNT', 'AIR_NT_5_11_SECOND_DOSE_PCT'


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get('https://covidlive.com.au/covid-live.json', headers=headers)

## Grab Covid Live Data

data = r.json()

# 'REPORT_DATE', 'LAST_UPDATED_DATE', 'CODE', 'NAME', 'CASE_CNT', 'TEST_CNT', 
# 'DEATH_CNT', 'RECOV_CNT', 'MED_ICU_CNT', 'MED_VENT_CNT', 'MED_HOSP_CNT', 
# 'SRC_OVERSEAS_CNT', 'SRC_INTERSTATE_CNT', 'SRC_CONTACT_CNT', 'SRC_UNKNOWN_CNT', 
# 'SRC_INVES_CNT', 'PREV_CASE_CNT', 'PREV_TEST_CNT', 'PREV_DEATH_CNT', 'PREV_RECOV_CNT', 
# 'PREV_MED_ICU_CNT', 'PREV_MED_VENT_CNT', 'PREV_MED_HOSP_CNT', 'PREV_SRC_OVERSEAS_CNT', 
# 'PREV_SRC_INTERSTATE_CNT', 'PREV_SRC_CONTACT_CNT', 'PREV_SRC_UNKNOWN_CNT', 'PREV_SRC_INVES_CNT',
# 'PROB_CASE_CNT', 'PREV_PROB_CASE_CNT', 'ACTIVE_CNT', 'PREV_ACTIVE_CNT', 'NEW_CASE_CNT', 
# 'PREV_NEW_CASE_CNT', 'VACC_DIST_CNT', 'PREV_VACC_DIST_CNT', 'VACC_DOSE_CNT', 'PREV_VACC_DOSE_CNT', 
# 'VACC_PEOPLE_CNT', 'PREV_VACC_PEOPLE_CNT', 'VACC_AGED_CARE_CNT', 'PREV_VACC_AGED_CARE_CNT',
# 'VACC_GP_CNT', 'PREV_VACC_GP_CNT', 'VACC_FIRST_DOSE_CNT', 'PREV_VACC_FIRST_DOSE_CNT', 
# 'VACC_FIRST_DOSE_CNT_12_15', 'PREV_VACC_FIRST_DOSE_CNT_12_15', 'VACC_PEOPLE_CNT_12_15',
# 'PREV_VACC_PEOPLE_CNT_12_15', 'VACC_BOOSTER_CNT', 'PREV_VACC_BOOSTER_CNT', 'VACC_FIRST_DOSE_CNT_5_11', 
# 'PREV_VACC_FIRST_DOSE_CNT_5_11', 'VACC_PEOPLE_CNT_5_11', 
# 'PREV_VACC_PEOPLE_CNT_5_11', 'NEW_PROB_CASE_CNT', 'PREV_NEW_PROB_CASE_CNT'
#%%
df = pd.read_json(r.text)
df = df[['REPORT_DATE', 'CODE', 'VACC_DOSE_CNT']]

## Drop rows only if they are blank within the past four weeks

latest_date = df['REPORT_DATE'].max()

init_date = datetime.datetime.strptime(latest_date, "%Y-%m-%d")

last_two = datetime.datetime.strftime((init_date - datetime.timedelta(days=28)), "%Y-%m-%d")

cope = df.loc[df['REPORT_DATE'] <= last_two].copy()
cope2 = df.loc[df['REPORT_DATE'] > last_two].copy()

cope2 = cope2.loc[cope2['VACC_DOSE_CNT'] != 0].copy()

cope.fillna(0, inplace=True)
cope2.dropna(subset=['VACC_DOSE_CNT'], inplace=True)

ant = pd.concat([cope, cope2])
ant.sort_values(by=['REPORT_DATE'], ascending=True, inplace=True)
ant.reset_index(drop=True, inplace=True)
ant.drop_duplicates(subset=['REPORT_DATE'], inplace=True)

df = ant.copy()

p = df 
print(p)
print(p.columns.tolist())
print(p['CODE'].unique().tolist())


states_daily = df.pivot(index='REPORT_DATE', columns = 'CODE', values='VACC_DOSE_CNT').reset_index()
states_daily = states_daily[['REPORT_DATE', 'ACT', 'AUS', 'NSW', 'NT', 'QLD', 'SA', 'TAS', 'VIC', 'WA']]
states_daily.columns = ['DATE_AS_AT', 'ACT_TOTAL', 'AUS_TOTAL', 'NSW_TOTAL', 'NT_TOTAL', 'QLD_TOTAL', 'SA_TOTAL', 'TAS_TOTAL', 'VIC_TOTAL', 'WA_TOTAL']
p = states_daily
print(p)
print(p.columns.tolist())

#%%
# cols = list(df.columns)

### THIS WAS THE PREVIOUS WAY OF DOING IT

# states = ["NSW","VIC","QLD","SA","WA","TAS","ACT","NT"]

# # STATE_CLINICS_WA_TOTAL CWTH_AGED_CARE_WA_TOTAL CWTH_PRIMARY_CARE_WA_TOTAL

# state_cum = df.copy()

# for state in states:
# 	state_cum[f'{state}_TOTAL'] = state_cum[f'STATE_CLINICS_{state}_TOTAL'] + state_cum[f'CWTH_AGED_CARE_{state}_TOTAL'] + state_cum[f'CWTH_PRIMARY_CARE_{state}_TOTAL']
	
# state_cum = state_cum[['DATE_AS_AT', 'TOTALS_NATIONAL_TOTAL', 'NSW_TOTAL', "VIC_TOTAL", "QLD_TOTAL", "SA_TOTAL", "WA_TOTAL", "TAS_TOTAL", "ACT_TOTAL", "NT_TOTAL"]]

# states_daily = state_cum.copy()

# states_daily = states_daily.set_index('DATE_AS_AT')

# states_daily = states_daily[['TOTALS_NATIONAL_TOTAL', 'NSW_TOTAL', "VIC_TOTAL", "QLD_TOTAL", "SA_TOTAL", "WA_TOTAL", "TAS_TOTAL", "ACT_TOTAL", "NT_TOTAL"]].sub(states_daily.shift())

# states_daily.reset_index(inplace=True)

# states_daily = states_daily.rename(columns = {"TOTALS_NATIONAL_TOTAL": "AUS_TOTAL"})

# short_cols = ['DATE_AS_AT']

# %%

# df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'], format="%Y-%m-%d")
# df = df.rename(columns={"REPORT_DATE": "Date"})

# #%%
# pivoted = df.pivot(index='Date', columns='CODE')['VACC_DOSE_CNT']

# daily_cum = pivoted[states]
# daily_cum.to_csv('pivot_cumulative.csv')

# # daily_cum["2021-02-24":"2021-08-16"] = daily_cum["2021-02-24":"2021-08-16"].apply(adjust)

# #%%

# daily = daily_cum.copy()

# for state in states:
# 	daily[state] = daily[state].sub(daily[state].shift())

# count = len(daily_cum["2021-02-24":"2021-08-15"].index) - 1

# daily.to_csv('daily-vax.csv')

# # Adjusts for the switchover from 2021-08-16 to the AIR derived data, by taking the new difference and adjusting previous values using an average of the difference

# diff_adjustment = {"NSW":119652, "VIC":-30981, "QLD":11598, "SA": -5354, "WA":15146, "TAS": 860, "ACT":47614, "NT":5192,"AUS":163727}
# state_adjustments = {}
# daily_adj = daily.copy()

# for state in states:
# 	gap = diff_adjustment[state]
# 	avg_7day = daily[state]["2021-08-09":"2021-08-15"].mean()
# 	adj_gap = gap - avg_7day
# 	adj_avg = adj_gap / count
# 	print("gap", gap, "avg_7day", avg_7day, "adj_gap", adj_gap, "adj_avg", adj_avg)
# 	state_adjustments[state] = {"adj_avg":adj_avg, "avg_7day":avg_7day}
# 	daily_adj[state]["2021-08-16"] = avg_7day

# #%%
# def adjust(col):
# 	return col + state_adjustments[col.name]["adj_avg"]

# daily_adj["2021-02-24":"2021-08-15"] = daily_adj["2021-02-24":"2021-08-15"].apply(adjust)

# #%%

# daily_short = daily_adj["2021-04-10":]
# # daily_short = daily["2021-04-10":]
# # daily[daily < 0] = 0

# #%%

# lastUpdated = daily_short.index[-1]
# # newUpdated = lastUpdated + timedelta(days=1)
# updatedText = lastUpdated.strftime('%-d %B, %Y')

# #%%

# def getRate(col):
# 	print(col.name)
# 	return col / population[col.name] * 100

# daily_short.apply(getRate)
# daily_rate = daily_short.apply(getRate)

# #%%

# daily_mean = daily_rate.rolling(7).mean()
# thirty_days = lastUpdated - timedelta(days=30)
# daily_mean = daily_mean[thirty_days:]
# daily_mean = daily_mean.dropna()
# # daily_mean = daily_mean[:-2]
# daily_mean.index = daily_mean.index.strftime('%Y-%m-%d')
# aus_only = daily_mean['AUS']

# #%%
# daily_mean = daily_mean.drop(['AUS'], axis=1)

# #%%
# daily_stack = daily_mean.stack().reset_index().rename(columns={"level_1":"category", 0:"State or territory"})
# daily_stack = daily_stack.set_index('Date')
# merge = pd.merge(daily_stack, aus_only, left_index=True, right_index=True)
# merge = merge.rename(columns={"AUS": "National"})
# merge = merge.round(3)

# print("merged", merge)


#%%

### Redo with Ken data

# url = 'https://vaccinedata.covid19nearme.com.au/data/air.json'

# air_data = pd.read_json(url)


#%%

# air = air_data.copy()

population = {
	"NSW":8166.4* 1000,
	"VIC":6680.6* 1000,
	"QLD":5184.8* 1000,
	"SA":1770.6* 1000,
	"WA":2667.1* 1000,
	"TAS":541.1* 1000,
	"NT":246.5* 1000,
	"ACT":431.2* 1000,
	"AUS":25693.1 * 1000
	}

states_daily['DATE_AS_AT'] = pd.to_datetime(states_daily['DATE_AS_AT'])

states =['NSW','VIC','QLD','WA','SA','TAS','NT','ACT','AUS']

short_cols = ['DATE_AS_AT']

states_daily.fillna(0, inplace=True)

for state in states:

	states_daily[f'{state}_TOTAL'] = states_daily[f'{state}_TOTAL'].diff(1)
	print(states_daily[f'{state}_TOTAL'])
	states_daily[f'{state}_7_day_avg'] = states_daily[f'{state}_TOTAL'].rolling(window=7).mean()
	print(states_daily[f'{state}_7_day_avg'])
	
	states_daily[f'{state}_7_day_avg_per_100'] = round((states_daily[f'{state}_7_day_avg']/population[state])*100,2)

	short_cols.append(f'{state}_7_day_avg_per_100')
	

rolled = states_daily[short_cols]


#%%

zdf = rolled.copy()


oz = zdf[['DATE_AS_AT', 'AUS_7_day_avg_per_100']]
oz.columns = ['Date', 'National']


zdf = zdf[['DATE_AS_AT', 'NSW_7_day_avg_per_100', 'VIC_7_day_avg_per_100', 'QLD_7_day_avg_per_100', 'WA_7_day_avg_per_100', 'SA_7_day_avg_per_100', 'TAS_7_day_avg_per_100', 'NT_7_day_avg_per_100', 'ACT_7_day_avg_per_100']]
zdf.columns = ['Date', 'NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'NT', 'ACT']



melted = pd.melt(zdf, id_vars=['Date'], value_vars=['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'NT', 'ACT'])

melted = melted.sort_values(by=['Date'], ascending=True)

tog = pd.merge(melted, oz, on=['Date'], how='left')

tog.columns = ['Date', 'Code', 'State or territory', 'National']

lastUpdated = tog['Date'].max()

updatedText = lastUpdated.strftime('%-d %B, %Y')

thirty_days = lastUpdated - timedelta(days=30)

tog = tog.loc[tog['Date'] > thirty_days]


tog['Date'] = tog['Date'].dt.strftime("%Y-%m-%d")

tog.set_index('Date', inplace=True)



merge = tog

p = tog

print(p)
print(p.columns.tolist())

def makeStateVaccinations(df):

	template = [
			{
				"title": "Trend in recent daily vaccinations by state and territory",
				"subtitle": "Showing the seven-day rolling average in Covid vaccination doses administered daily per 100 people in each state and territory, versus the national rate. Showing the last 30 days only. Last updated {date}".format(date=updatedText),
				"footnote": "",
				"source": " | Source: Guardian Australia analysis of <a href='https://covidlive.com.au/' target='_blank'>covidlive.com.au</a> data | Data shows vaccinations by state of administration, not by state of residence",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "",
				"timeInterval":"day",
				"tooltip":"<strong>Date: </strong>{{#nicedate}}Date{{/nicedate}}<br/><strong>Rolling average per 100: </strong>{{State or territory}}",
				"periodDateFormat":"",
				"margin-left": "35",
				"margin-top": "25",
				"margin-bottom": "22",
				"margin-right": "22",
				"xAxisDateFormat": "%b %d"
			}
		]
	key = []
	periods = [{"label":"Data change", "start":"2021-08-16","end":"","textAnchor":"start"}]
	labels = []
	options = [{"numCols":4, "chartType":"line", "height":150, "scaleBy":"group"}]
	chartId = [{"type":"smallmultiples"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template,options=options, data=chartData, periods=periods, chartId=chartId, chartName=f"state-vaccinations-sm-2021{testo}")

makeStateVaccinations(merge)

# %%
