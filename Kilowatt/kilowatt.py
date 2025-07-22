import sys, os, json
import pandas as pd

sys.path.append(".") # Set path to the roots

from _toolClass.crawler import crawler

class kilowatt(crawler):
    __slots__ = []
    REGION = {
            "香港島": r"%E9%A6%99%E6%B8%AF%E5%B3%B6",
            "九龍": r"%E4%B9%9D%E9%BE%8D",
            "新界": r"%E6%96%B0%E7%95%8C"
        }
    jsonFirst = [
        "id", "chargerId", "name", "nameEn", "address", "area", # Basic info
        "notes", "provider", "providerTel", "providerEmail", "providerWhatsApp", # Addition Info
        "type", "plug", "power", "slots", # Charging Info
        "carParkPricings", "chargingPricing", "avgPricePerKwh", "avgPricePerKwh2", # Price
        "latitude", "longitude",
        "updatedAt", # Meta data
        "aiSummary", "aiSummerizedAt"
    ]
    jsonCarPark = [
        "id", "name", "address", "description", "location", "carParkPricings", "featuredName", "featuredOrder", # Basic info
        "latitude", "longitude",
        "providers", "types", "chargersCount", "chargerIds", # Charging Info
        "parkingOfferUrl" # Additional Info
    ]

    def __init__(self) -> None:
        pass

    def getAll(self, path: str = "") -> None:
        for region in list(self.REGION.keys()):
            savePath = os.path.join(path, region)
            if not os.path.exists(savePath):
                os.mkdir(savePath)
            self.getOneRegion(region, os.path.join(path, region))

        return
    
    def getOneRegion(self, region: str, path: str = "") -> None:
        if region not in list(self.REGION.keys()):
            raise RuntimeError("Region do not exisit.")
        super().__init__("https://api.kilowatt.hk/charger/all?area=".format(self.REGION[region]))
        j = self.rget().json()
        
        result = {x: [] for x in self.jsonFirst + ["CarParkID"]}
        resultParking = {x: [] for x in self.jsonCarPark}

        for data in j:
            for i in self.jsonFirst:
                result[i].append(data.get(i, ""))
            result["CarParkID"].append(data["carPark"]["id"])
            for i in self.jsonCarPark:
                resultParking[i].append(data["carPark"].get(i, ""))

        pd.DataFrame(result).sort_values("id").to_csv(os.path.join(path, "{}_充电站.csv".format(region)), encoding="utf-8", index=False)
        pd.DataFrame(resultParking).drop_duplicates("id").sort_values("id").to_csv(os.path.join(path, "{}_停车场.csv".format(region)), encoding="utf-8", index=False)

        with open(os.path.join(path, "{}.json".format(region)), 'w', encoding="utf-8") as f:
            json.dump(j, f, ensure_ascii=False, indent=4)

        return
    
if __name__ == "__main__":
    # kilowatt().getOneRegion("香港島", "test")
    kilowatt().getAll("Kilowatt\\Data")