# =============================================================================
# OPTIONAL ETL SCRIPT - MARKER NOTE
# =============================================================================
# This script is only needed if you want to recreate the database from raw CSVs.
# The submitted tfl_analysis_dump.sql already contains all cleaned data + views.
# You do NOT need to run this file for the dashboard to work.
# =============================================================================

import pandas as pd;
import pandas.io.sql as sqlio
import psycopg2;
import numpy as p;
import os;

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="TFL_Analysis",
        user="postgres",
        password="Faisal@123" # Change this to your own Postgres Password you set during the installation.  
    )
conn=get_connection()
cursor=conn.cursor()
    
    


##LCh by line
df=pd.read_csv(r"data_raw\Lost Customer Hours By Line.csv",skiprows=1, nrows = 10)
df.rename(columns={df.columns[0]: 'line'}, inplace=True)
melted_df=pd.melt(df, id_vars=["line"],var_name="year",value_name="Lost Customer Hours")
melted_df["Lost Customer Hours"] = melted_df["Lost Customer Hours"].str.replace(",","")
print(melted_df)
"""
query=("Insert into lchbyline(line,lost_customer_hours,year) values(%s,%s,%s)")
for index,row in melted_df.iterrows():
    value=(row['line'],row['Lost Customer Hours'],row['year'])
    cursor.execute(query,value)
"""


##LCH by category
df1=pd.read_csv(r"data_raw\Lost Customer Hours By Category.csv",skiprows=1, nrows = 24)
df1.rename(columns={df1.columns[0]: 'category'}, inplace=True)
melted_df1=pd.melt(df1,id_vars=["category"],var_name="year",value_name="Lost Customer Hours")
melted_df1=melted_df1.dropna()
melted_df1["Lost Customer Hours"]= melted_df1["Lost Customer Hours"].str.replace(",","")
print(melted_df1)
"""
query1=("Insert into lchbycategory(category,lost_customer_hours,year) values(%s,%s,%s)")
for index,row in melted_df1.iterrows():
    value1=(row['category'],row['Lost Customer Hours'],row['year'])
    cursor.execute(query1,value1)
"""

df2=pd.read_csv(r"data_raw\Excess Journey Time.csv",skiprows=1,nrows=10)
df2.rename(columns={df2.columns[0]:'line'},inplace=True)
melted_df2=pd.melt(df2,id_vars=["line"],var_name="year",value_name="Excess Journey Time")
melted_df2=melted_df2.dropna()
print(melted_df2)
"""
query2=("Insert into excess_journey_time(ejt,year,line) values(%s,%s,%s)")
for index,row in melted_df2.iterrows():
    value2=(row['Excess Journey Time'],row['year'],row['line'])
    cursor.execute(query2,value2)
"""

df3=pd.read_csv(r"data_raw\Escalator Availability.csv",skiprows=1,nrows=10)
df3.rename(columns={df3.columns[0]:'line'},inplace=True)
melted_df3=pd.melt(df3,id_vars=["line"],var_name="year",value_name="Escalator Availability(%)")
melted_df3["Escalator Availability(%)"]=melted_df3["Escalator Availability(%)"].str.replace("%","")
print(melted_df3)
"""
query3=("Insert into esc_avl(esc_avail,line,year) values(%s,%s,%s)")
for index,row in melted_df3.iterrows():
    value3=(row['Escalator Availability(%)'],row['line'],row['year'])
    cursor.execute(query3,value3)
"""

df4=pd.read_csv(r"data_raw\Customer Satisfation.csv",skiprows=[0,2],nrows=10)
df4.rename(columns={df4.columns[0]:'line'},inplace=True)
melted_df4=pd.melt(df4,id_vars=["line"],var_name="year",value_name="Customer Satisfaction")
print(melted_df4)
"""
query4=("Insert into css(line,year,customer_satisfaction) values (%s,%s,%s)")
for index,row in melted_df4.iterrows():
    value4=(row['line'],row['year'],row['Customer Satisfaction'])
    cursor.execute(query4,value4)
"""
df5=pd.read_csv(r"data_raw\Scheduled Operated.csv",skiprows=[0,2],nrows=10)
df5.rename(columns={df5.columns[0]:'line'},inplace=True)
melted_df5=pd.melt(df5,id_vars=["line"],var_name="year",value_name="Schedule Operated")
melted_df5["Schedule Operated"]=melted_df5["Schedule Operated"].str.replace("%","")
print(melted_df5)
"""
query5=("Insert into schedule_operated(line,year,schedule_operated) values(%s,%s,%s)")
for index,row in melted_df5.iterrows():
    value5=(row['line'],row['year'],row['Schedule Operated'])
    cursor.execute(query5,value5)
"""
conn.commit()
conn.close()

