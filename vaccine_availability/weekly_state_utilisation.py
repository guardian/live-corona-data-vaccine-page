#%%
import pandas as pd 
from modules.yachtCharter import yachtCharter
import datetime

chart_key = "oz-datablogs-something_random"
fillo = 'https://vaccinedata.covid19nearme.com.au/data/distribution.json'

testo = "_testo"

#%%
df = pd.read_json(fillo)

# 'DATE_AS_AT', 'STATE_CLINICS_VIC_DISTRIBUTED',
#        'STATE_CLINICS_QLD_DISTRIBUTED', 'STATE_CLINICS_WA_DISTRIBUTED',
#        'STATE_CLINICS_TAS_DISTRIBUTED', 'STATE_CLINICS_SA_DISTRIBUTED',
#        'STATE_CLINICS_ACT_DISTRIBUTED', 'STATE_CLINICS_NT_DISTRIBUTED',
#        'STATE_CLINICS_NSW_DISTRIBUTED', 'CWTH_AGED_CARE_DISTRIBUTED',
#        'CWTH_PRIMARY_CARE_DISTRIBUTED', 'STATE_CLINICS_VIC_AVAILABLE',
#        'STATE_CLINICS_QLD_AVAILABLE', 'STATE_CLINICS_WA_AVAILABLE',
#        'STATE_CLINICS_TAS_AVAILABLE', 'STATE_CLINICS_SA_AVAILABLE',
#        'STATE_CLINICS_ACT_AVAILABLE', 'STATE_CLINICS_NT_AVAILABLE',
#        'STATE_CLINICS_NSW_AVAILABLE', 'CWTH_AGED_CARE_AVAILABLE',
#        'CWTH_PRIMARY_CARE_AVAILABLE', 'STATE_CLINICS_VIC_ADMINISTERED',
#        'STATE_CLINICS_QLD_ADMINISTERED', 'STATE_CLINICS_WA_ADMINISTERED',
#        'STATE_CLINICS_TAS_ADMINISTERED', 'STATE_CLINICS_SA_ADMINISTERED',
#        'STATE_CLINICS_ACT_ADMINISTERED', 'STATE_CLINICS_NT_ADMINISTERED',
#        'STATE_CLINICS_NSW_ADMINISTERED', 'CWTH_AGED_CARE_ADMINISTERED',
#        'CWTH_PRIMARY_CARE_ADMINISTERED',
#        'STATE_CLINICS_VIC_AVAILABLE_MINUS_ADMINISTERED',
#        'STATE_CLINICS_QLD_AVAILABLE_MINUS_ADMINISTERED',
#        'STATE_CLINICS_WA_AVAILABLE_MINUS_ADMINISTERED',
#        'STATE_CLINICS_TAS_AVAILABLE_MINUS_ADMINISTERED',
#        'STATE_CLINICS_SA_AVAILABLE_MINUS_ADMINISTERED',
#        'STATE_CLINICS_ACT_AVAILABLE_MINUS_ADMINISTERED',
#        'STATE_CLINICS_NT_AVAILABLE_MINUS_ADMINISTERED',
#        'STATE_CLINICS_NSW_AVAILABLE_MINUS_ADMINISTERED',
#        'CWTH_PRIMARY_CARE_AVAILABLE_MINUS_ADMINISTERED',
#        'STATE_CLINICS_VIC_ESTIMATED_DOSE_UTILISATION',
#        'STATE_CLINICS_QLD_ESTIMATED_DOSE_UTILISATION',
#        'STATE_CLINICS_WA_ESTIMATED_DOSE_UTILISATION',
#        'STATE_CLINICS_TAS_ESTIMATED_DOSE_UTILISATION',
#        'STATE_CLINICS_SA_ESTIMATED_DOSE_UTILISATION',
#        'STATE_CLINICS_ACT_ESTIMATED_DOSE_UTILISATION',
#        'STATE_CLINICS_NT_ESTIMATED_DOSE_UTILISATION',
#        'STATE_CLINICS_NSW_ESTIMATED_DOSE_UTILISATION',
#        'CWTH_AGED_CARE_ESTIMATED_DOSE_UTILISATION',
#        'CWTH_PRIMARY_CARE_ESTIMATED_DOSE_UTILISATION', 'VALIDATED', 'URL',
#        'CWTH_AGED_CARE_AVAILABLE_MINUS_ADMINISTERED'

# df = df[['DATE_AS_AT','STATE_CLINICS_NSW_DISTRIBUTED','STATE_CLINICS_NSW_AVAILABLE','STATE_CLINICS_NSW_ADMINISTERED',
# 'STATE_CLINICS_NSW_ESTIMATED_DOSE_UTILISATION', 'STATE_CLINICS_NSW_AVAILABLE_MINUS_ADMINISTERED']]

regions = ['NT', 'NSW', 'VIC', 'QLD', 
'ACT', 'SA', 'WA', 'TAS', "CWTH_AGED_CARE", "CWTH_PRIMARY_CARE"]

# rename = {"NT": "Northern Territory", "NSW": "NSW", "VIC": "Victoria", "QLD": ""}

#%%

listo = []

for region in regions:

    print(region)

    # include = [x for x in df.columns if region in x or x == 'DATE_AS_AT']

    # include = [x for x in include if f"{region}" in x or x == 'DATE_AS_AT']

    # inter = df[include]

    inter = df.copy()

    

    if region == "CWTH_PRIMARY_CARE":

        inter['Init'] = inter['CWTH_PRIMARY_CARE_AVAILABLE'] - inter['CWTH_PRIMARY_CARE_ADMINISTERED']

        # inter = inter[['DATE_AS_AT', 'Init']]

        # inter.rename(columns={f"{region}_PRIMARY_CARE_AVAILABLE_MINUS_ADMINISTERED": "Primary care (Commonwealth)"}, inplace=True)

    elif region == "CWTH_AGED_CARE":

        # inter.rename(columns={f"{region}_AGED_CARE_AVAILABLE_MINUS_ADMINISTERED": "Aged care (Commonwealth)"}, inplace=True)

        inter['Init'] = inter[f'CWTH_AGED_CARE_AVAILABLE'] - inter[f'CWTH_AGED_CARE_ADMINISTERED']

        # inter = inter[['DATE_AS_AT', 'Init']]
    
    else:

        inter['Init'] = inter[f'STATE_CLINICS_{region}_AVAILABLE'] - inter[f'STATE_CLINICS_{region}_ADMINISTERED']

        
        

        # inter.rename(columns={f"STATE_CLINICS_{region}_AVAILABLE_MINUS_ADMINISTERED": region}, inplace=True)

    # inter[region] = inter['Init'].diff(1)

    inter[region] = inter['Init']


    inter = inter[['DATE_AS_AT', region]]
    

    inter = pd.melt(inter, id_vars='DATE_AS_AT')

    # print(inter.columns)

    # inter.columns 

    listo.append(inter)

final = pd.concat(listo)

# melted = pd.melt(final, id_vars='DATE_AS_AT')

final.columns = ['Date', 'Variable', 'Value']

final['Date'] = final['Date'].dt.strftime('%Y-%m-%d')

final.loc[final['Variable'] == "CWTH_PRIMARY_CARE", 'Variable'] = "Primary care"
final.loc[final['Variable'] == "CWTH_AGED_CARE", 'Variable'] = "Aged care"

updated_date = final['Date'].max()
updated_date = datetime.datetime.strptime(updated_date, "%Y-%m-%d")
updated_date = datetime.datetime.strftime(updated_date, "%d/%m/%Y")

print(final)

# %%


def makeChart(df):

    template = [
            {
                "title": "Unused vaccines by jurisdiction",
                "subtitle": f"""Showing the difference between doses available and administered by each state, and in aged and primay care. Data as of {updated_date}""",
                "footnote": "",
                "source": "| Source: Ken Tsang, Department of Health rollout updates",
                "dateFormat":"%Y-%m-%d",
                "margin-left": "50",
                "margin-top": "20",
                "margin-bottom": "20",
                "margin-right": "10"
            }
        ]
    key = []
    # key = []
    labels = []
    df.fillna("", inplace=True)
    chartData = df.to_dict('records')
    # labels = [{"x":"2021-06-21", "y":10, "text":"hi", "align":"center", "offset":1}]
    periods = []

    yachtCharter(template=template, data=chartData, chartId=[{"type":"smallmultiples"}],
    options=[{"scaleBy": "individual","chartType": "area","numCols":1,"height": 100}], periods=periods, key=key, chartName=f"{chart_key}{testo}")

makeChart(final)
# 