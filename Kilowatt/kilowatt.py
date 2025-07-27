import sys, os, json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

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
        "id", "chargerId", "name", "nameEn", "address", "area", "region", # Basic info
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
        resultParking = {x: [] for x in self.jsonCarPark + ["region"]}

        for data in j:
            for i in self.jsonFirst:
                result[i].append(data.get(i, ""))
            result["CarParkID"].append(data["carPark"]["id"])
            for i in self.jsonCarPark:
                resultParking[i].append(data["carPark"].get(i, ""))
            resultParking["region"].append(data["region"])

        result = pd.DataFrame(result).sort_values("id")
        result.drop(result.loc[result["region"].isin(["台灣", "中國"])].index, inplace=True)
        result.drop(columns=["region"], inplace=True)
        result.drop(result.loc[result["id"].isin([2822, 1090])].index, inplace=True) # HZBM, lost lng&lat and Private
        result.loc[result["id"] == 4509, "longitude"] += 100 # wrong lng
        result.loc[result["id"] == 714, "latitude"] = 22.42655402957831 # 新界沙田香港科學園科技大道西8-10號香港科技園二期地庫停車場
        result.loc[result["id"] == 714, "longitude"] = 114.21002151090484
        result.loc[result["id"] == 1090, "latitude"] = 22.50704775918642 # 上水天平路33號奕翠園
        result.loc[result["id"] == 1090, "longitude"] = 114.13293655402333
        result.loc[result["id"] == 1211, "latitude"] = 22.37371350224374 # 沙田多石街23號水泉澳邨
        result.loc[result["id"] == 1211, "longitude"] = 114.19858817305845
        result.loc[result["id"] == 1242, "latitude"] = 22.31669238347453 # 觀塘海濱道77號海濱匯
        result.loc[result["id"] == 1242, "longitude"] = 114.21368703867783
        result.loc[result["id"] == 3855, "latitude"] = 22.33483125865408 # 荔枝角道873號
        result.loc[result["id"] == 3855, "longitude"] = 114.1468907540199
        result.to_csv(os.path.join(path, "{}_充电站.csv".format(region)), encoding="utf-8", index=False)

        resultParking = pd.DataFrame(resultParking).drop_duplicates("id").sort_values("id")
        resultParking.drop(resultParking.loc[resultParking["region"].isin(["台灣", "中國"])].index, inplace=True)
        resultParking.drop(columns=["region"], inplace=True)
        result.drop(result.loc[result["id"].isin([1270, 153])].index, inplace=True) # HZBM, lost lng&lat and Private
        resultParking.loc[resultParking["id"] == 1972, "longitude"] += 100
        resultParking.loc[resultParking["id"] == 399, "latitude"] = 22.42655402957831 # 新界沙田香港科學園科技大道西8-10號香港科技園二期地庫停車場
        resultParking.loc[resultParking["id"] == 399, "longitude"] = 114.21002151090484
        resultParking.loc[resultParking["id"] == 153, "latitude"] = 22.50704775918642 # 上水天平路33號奕翠園
        resultParking.loc[resultParking["id"] == 153, "longitude"] = 114.13293655402333
        resultParking.loc[resultParking["id"] == 318, "latitude"] = 22.37371350224374 # 沙田多石街23號水泉澳邨
        resultParking.loc[resultParking["id"] == 318, "longitude"] = 114.19858817305845
        resultParking.loc[resultParking["id"] == 399, "latitude"] = 22.31669238347453 # 觀塘海濱道77號海濱匯
        resultParking.loc[resultParking["id"] == 399, "longitude"] = 114.21368703867783
        resultParking.loc[resultParking["id"] == 1668, "latitude"] = 22.33483125865408 # 荔枝角道873號
        resultParking.loc[resultParking["id"] == 1668, "longitude"] = 114.1468907540199
        resultParking.to_csv(os.path.join(path, "{}_停车场.csv".format(region)), encoding="utf-8", index=False)

        resultGeometry = [Point(lon, lat) for lon, lat in zip(result["longitude"], result["latitude"])]
        gpd.GeoDataFrame(result, geometry=resultGeometry, crs="EPSG:4326").to_file(
            os.path.join(path, "{}_充电站.geojson".format(region)),
            driver="GeoJSON", encoding="utf-8"
        )

        parkGeometry = [Point(lon, lat) for lon, lat in zip(resultParking["longitude"], resultParking["latitude"])]
        gpd.GeoDataFrame(resultParking, geometry=parkGeometry, crs="EPSG:4326").to_file(
            os.path.join(path, "{}_停车场.geojson".format(region)),
            driver="GeoJSON", encoding="utf-8"
        )
        
        with open(os.path.join(path, "{}.json".format(region)), 'w', encoding="utf-8") as f:
            json.dump(j, f, ensure_ascii=False, indent=4)

        return
    
if __name__ == "__main__":
    kilowatt().getOneRegion("香港島", "Kilowatt\\Data")
    # kilowatt().getAll("Kilowatt\\Data")