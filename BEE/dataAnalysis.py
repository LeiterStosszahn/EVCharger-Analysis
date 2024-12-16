import os
import pandas as pd
import numpy as np

class analysis:
    def __init__(self):
        # Have mixed data type, all data are readed as str
        self.data = pd.read_csv(r"Data\\BEEresult.csv", dtype=str, encoding="utf-8")

    def statistics(self, path: str = "") -> None:
        maxColNum = self.data.shape[1]
        chargerStartInd = [x for x in range(22, maxColNum, 12)]
        self.data["charger"] = self.data.iloc[:, chargerStartInd].count(axis=1)

        # How many stations and how many chargers
        fourWheel = self.data.loc[self.data["is_fourwheeler"] == "True"].groupby(["state_name"]).size().reset_index(name="stationNum(Fourwheels)")
        print(fourWheel)
        result = self.data.groupby(["state_name"]).agg(
            stationNum = ("state_name", 'size'),
            chargerNum = ("charger", "sum") 
        )
        result = pd.merge(fourWheel, result, on="state_name", how="outer").fillna(0)
        result.to_csv(os.path.join(path, "stateNumStat.csv"), encoding="utf-8")

        return 0

if __name__ == "__main__":
    a = analysis()
    a.statistics("Data")