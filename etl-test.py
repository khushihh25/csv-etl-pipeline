import pandas as pd
import sqlite3
pd.set_option("display.width", 200) #pd.set_option(...) is a global setting. Once set, every DataFrame you print in that script follows it.
pd.set_option("display.max_column", None) #None means “no limit.” The option is asking: “what is the maximum number of columns you may show?”

df = pd.read_csv("messy_sales.csv") #extract
#transform the dirty data fpr that we need first how the data looks


#startig with order_id
df= df.drop_duplicates().reset_index(drop=True)
df["customer_name"]= df["customer_name"].str.strip().str.title()
df["city"] = df["city"].str.strip().str.title()

df["order_date"] = pd.to_datetime(df["order_date"].str.strip(), format="mixed", dayfirst=True)
df["amount"] = df["amount"].str.replace(r"[^\d.]","", regex=True)
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
df.loc[df["quantity"] <= 0, "quantity"] = None

df["status"]= df["status"].str.strip().str.lower()
print(df.info())
print(df)

conn = sqlite3.connect("data.db")
df.to_sql("data", conn, if_exists="replace", index_label=False)
check = pd.read_sql("""
select city, count(*) as orders, sum(amount) as total_sales
from data
where status = 'delivered'
group by city
order by total_sales desc""", conn)
print(check)
conn.close

