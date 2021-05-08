import pandas as pd
df = pd.read_csv("Tables/Table 5  Threatened species in each major group by country - show all.csv")
#df["id"] = df["Name"].apply(len)
print(df.head())
print(df.columns)