import pandas as pd;
import pandas.io.sql as sqlio
import psycopg2;
import numpy as p;

conn = psycopg2.connect(
    host="localhost",
    database="TFL_Analysis",
    user="postgres",
    password="Faisal@123"
)
cursor=conn.cursor()
'''
##LCh by line
df=pd.read_csv(r"data_raw\Lost Customer Hours By Line.csv",skiprows=1, nrows = 10)
df.rename(columns={df.columns[0]: 'line'}, inplace=True)
melted_df=pd.melt(df, id_vars=["line"],var_name="year",value_name="Lost Customer Hours")
melted_df["Lost Customer Hours"] = melted_df["Lost Customer Hours"].str.replace(",","")
query=("Insert into lchbyline(line,lost_customer_hours,year) values(%s,%s,%s)")
for index,row in melted_df.iterrows():
    value=(row['line'],row['Lost Customer Hours'],row['year'])
    cursor.execute(query,value)


##LCH by category
df1=pd.read_csv(r"data_raw\Lost Customer Hours By Category.csv",skiprows=1, nrows = 24)
df1.rename(columns={df1.columns[0]: 'category'}, inplace=True)
melted_df1=pd.melt(df1,id_vars=["category"],var_name="year",value_name="Lost Customer Hours")
melted_df1=melted_df1.dropna()
melted_df1["Lost Customer Hours"]= melted_df1["Lost Customer Hours"].str.replace(",","")


query1=("Insert into lchbycategory(category,lost_customer_hours,year) values(%s,%s,%s)")
for index,row in melted_df1.iterrows():
    value1=(row['category'],row['Lost Customer Hours'],row['year'])
    cursor.execute(query1,value1)
'''

df2=pd.read_csv(r"data_raw\Excess Journey Time.csv",skiprows=1,nrows=10)
df2.rename(columns={df2.columns[0]:'line'},inplace=True)
melted_df2=pd.melt(df2,id_vars=["line"],var_name="year",value_name="Excess Journey Time")
melted_df2=melted_df2.dropna()
print(melted_df2)
query2=("Insert into excess_journey_time(ejt,year,line) values(%s,%s,%s)")
for index,row in melted_df2.iterrows():
    value2=(row['Excess Journey Time'],row['year'],row['line'])
    cursor.execute(query2,value2)






conn.commit()
conn.close()


