import sys, os, json, copy
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

sys.path.append(".") # Set path to the roots

from _toolClass.crawler import crawler

class tvpi(crawler):
    __slots__ = []
    Json = ["_id", "name", "lat", "lng", "private", "current", "upkeep", "canReserve", "parentCompanyID"]
    connectedPlugs = ["name", "power", "current", "plug_id"]

    def __init__(self):
        pass
    
    def getData(self, j: list[dict], savePath: str) -> None:
        result = {x: [] for x in self.Json + ["connectedPlugs", "connectorNum"]}
        plug = {x: [] for x in self.connectedPlugs}
        for data in j:
            for i in self.Json:
                result[i].append(data.get(i, None))
            plugs = data.get("connectedPlugs", [])
            if plugs == []:
                result["connectedPlugs"].append(None)
                result["connectorNum"].append(None)
            else:
                plugResult = copy.deepcopy(plug)
                for p in plugs:
                    for i in self.connectedPlugs:
                        plugResult[i].append(p.get(i, None))
                result["connectedPlugs"].append(plugResult)
                result["connectorNum"].append(len(plugResult["name"]))

        result = pd.DataFrame(result)
        result.to_csv(os.path.join(savePath, "tvpi.csv"), encoding="utf-8")

        resultGeometry = [Point(lon, lat) for lon, lat in zip(result["lng"], result["lat"])]
        gpd.GeoDataFrame(result, geometry=resultGeometry, crs="EPSG:4326").to_file(
            os.path.join(savePath, "tvpi.geojson"),
            driver="GeoJSON", encoding="utf-8"
        )

        return

    def getFromCrawler(self, savePath: str) -> None:
        print("Downloading meta data...")
        url = r"https://api.tupinambaenergia.com.br/stationsShortVersion"
        super().__init__(url)
        j = self.rget().json()
        self.getData(j, savePath)
        
        return
    
    def getFromJson(self, jsonPath: str, savePath: str) -> None:
        with open(jsonPath, encoding="utf-8") as jf:
            j = json.load(jf)
            self.getData(j, savePath)

        return
        
if __name__ == "__main__":
    tvpi().getFromJson(r"Tvpi\\b.json", r"Tvpi\\Data")