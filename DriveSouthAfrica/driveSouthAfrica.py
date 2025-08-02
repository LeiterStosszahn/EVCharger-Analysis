import sys, os, json, re
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from py_mini_racer import py_mini_racer

sys.path.append(".") # Set path to the roots

from _toolClass.crawler import crawler

class driveSouthAfrica(crawler):
    __slots__ = []
    Json = ["name", "locatedIn", "address", "type2", "type2TotalBays", "typeCCS", "typeCCSTotalBays", "contact"]

    def __init__(self):
        pass
    
    def getData(self, j: list[dict], savePath: str) -> None:
        result = {x: [] for x in self.Json + ["lat", "lng", "numberOfChargers"]}
        for data in j:
            for i in self.Json:
                result[i].append(data.get(i, None))
            position = data.get("position", {})
            a = data.get("type2TotalBays", "").split(' ')[0]
            b = data.get("typeCCSTotalBays", "").split(' ')[0]
            if len(a) == 0:
                a = 0
            else:
                a = int(a)
            if len(b) == 0:
                b = 0
            else:
                b = int(b)
            if a == 0 and b == 0:
                a = None
            else:
                a += b
            result["numberOfChargers"].append(a)
            if position == {}:
                result["lat"].append(None)
                result["lng"].append(None)
            else:
                result["lat"].append(position.get("lat", None))
                result["lng"].append(position.get("lng", None))

        result = pd.DataFrame(result)
        result.to_csv(os.path.join(savePath, "driveSouthAfrica.csv"), encoding="utf-8")

        resultGeometry = [Point(lon, lat) for lon, lat in zip(result["lng"], result["lat"])]
        gpd.GeoDataFrame(result, geometry=resultGeometry, crs="EPSG:4326").to_file(
            os.path.join(savePath, "driveSouthAfrica.geojson"),
            driver="GeoJSON", encoding="utf-8"
        )

        return

    def getFromCrawler(self, savePath: str) -> None:
        print("Downloading meta data...")
        url = r"https://media.drivesouthafrica.com/wp-content/themes/dsa_theme/js/ev-map-tool-script.js?ver=1.0.3"
        super().__init__(url)
        js = self.rget().text
        # Find chaging station in js
        pattern = r"(var\s+chargingStations\s*=\s*\[.*?\]);"
        match = re.search(pattern, js, re.DOTALL)
        if match is None:
            raise ValueError("Cannot find chargingStations.")
        targetCode = match.group(0) + "\nJSON.stringify(chargingStations);"

        # Process js code
        ctx = py_mini_racer.MiniRacer()
        resultJson = ctx.eval(targetCode)
        j = json.loads(resultJson)
        self.getData(j, savePath)

        with open(os.path.join(savePath, "rowData.js"), 'w', encoding="utf-8") as f:
            f.write(targetCode)

        with open(os.path.join(savePath, "driveSouthAfrica.json"), 'w', encoding="utf-8") as f:
            json.dump(j, f, indent=4, ensure_ascii=False)
        
        return
        
if __name__ == "__main__":
    driveSouthAfrica().getFromCrawler(r"DriveSouthAfrica\\Data")