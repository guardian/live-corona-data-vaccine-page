import pandas as pd 



dummy_vals = [x for x in range(0, 400)]

dummy_date = '2021-03-22'

dummy_df = pd.DataFrame({"Units":1, 
                "Date": pd.date_range(start=dummy_date, periods=len(dummy_vals))})


dummy_df = dummy_df.loc[(dummy_df['Date'] > "2021-03-23") & (dummy_df['Date'] <= "2021-12-31")]


print(dummy_df)