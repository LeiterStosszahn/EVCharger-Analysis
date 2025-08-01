import os, json, sys
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(".") # Set path to the roots

from _toolClass.crawler import crawler

class BEE(crawler):
    __allStationUrl = "https://evyatra.beeindia.gov.in/bee-ev-backend/getallPCSlatlng"
    __stateUrl = "https://evyatra.beeindia.gov.in/bee-ev-backend/getstatelist"
    __stationDetialUrl = "https://evyatra.beeindia.gov.in/bee-ev-backend/getPCSdetailsbystationid"
    __keys = [
        "companyname", "st_owner", "mobile_no", "contactPerson", "amenities",
        "avg_cost_discom", "opening_time", "closing_time", "is_tweenty_four_seven",
        "city_name", "wkStatus", "is_fourwheeler"
    ]
    __chagerKeys = [
        "id", "chargerRatedCapacityId", "typeOfChargerId", "ocpi_tariff_rate_id",
        "noOfChargers", "chargerType", "ratedCapacity", "serviceCharge", "power_type",
        "connector_working_status", "wkStatus", "tariff_rate"
    ]
    stateList = None
    finalResult = None

    def __init__(self):
        pass

    def getAllState(self, path: str = "") -> None:
        super().__init__(self.__stateUrl)
        data = self.rget()
        data = data.json()
        value = data["value"]
        result = pd.DataFrame.from_records(value, index="id")
        if path != "":
            result.to_csv(path + "stateID(BEE).csv", encoding="utf-8")
        
        self.stateList = result[["state_name"]].copy()
        
        return

    def getAllStation(self, path: str = "") -> None:
        super().__init__(self.__allStationUrl)
        data = self.rpost()
        data = data.json()
        value = data["value"]
        result = pd.DataFrame.from_records(value)

        # Change state id to text
        if not self.stateList is None:
            result.set_index("state_id", inplace=True)
            result["state_name"] = None
            result["state_name"].update(self.stateList["state_name"])
        result.set_index("id", drop=True, inplace=True)
        
        # Initialize detial columns
        for i in self.__keys:
            result[i] = None
        self.finalResult = result
        
        # Add detial information
        num = 0
        total= self.finalResult.shape[0]
        
        # Multithread
        threads = ThreadPoolExecutor(max_workers = 4)
        futures = set()
        for i in self.finalResult.index:
            num += 1
            futures.add(threads.submit(self.getDetial, i, num, total, path))
        for future in as_completed(futures):
            future.result()

        self.finalResult.to_csv(os.path.join(path,"BEEresult.csv"), encoding="utf-8")
    
    def getDetial(self, stationID: str, process: int, total: int, path: str) -> None:
        print("{}/{}".format(process, total))
        postData = json.dumps({"station_id": int(stationID)})
        r = crawler(self.__stationDetialUrl, postData)
        data = r.rpost()
        data = data.json()
        value = data["value"]
        for i in self.__keys:
            if self.finalResult is not None:
                self.finalResult.loc[stationID, i] = value[i]
            else:
                raise RuntimeError("Failed to initialize final result.")
        
        # Add information of charger
        num = 1
        for i in value["charger"]:
            for j in self.__chagerKeys:
                if self.finalResult is not None:
                    self.finalResult.loc[stationID, j + "_Chger" + str(num)] = i[j]
                else:
                    raise RuntimeError("Failed to initialize final result.")
            num += 1
        
        #Save intermediate results ever 100 times
        if process % 100 == 0:
            if self.finalResult is not None:
                self.finalResult.to_csv(os.path.join(path,"BEEresult.csv"), encoding="utf-8")
            else:
                raise RuntimeError("Failed to initialize final result.")

        return

if __name__ == "__main__":
    a=BEE()
    # Add path in the method if the csv of all state is needed
    a.getAllState("Data")
    a.getAllStation("Data")
