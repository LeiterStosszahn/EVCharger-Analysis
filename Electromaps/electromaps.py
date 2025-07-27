import sys, os, json, threading, time, random, gc
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

sys.path.append(".") # Set path to the roots

from _toolClass.crawler import crawler

class electromaps(crawler):
    __slots__ = []
    Json = ["latitude", "longitude", "name"]
    Detial = ["instructions"]
    DetialAddress = ["address", "city", "country_code"]

    def __init__(self):
        pass
    
    def getDataByCoor(self, XMax: float, YMax: float, XMin: float, YMin: float, savePath: str, name: str, countryCode: list[str] = []) -> None:
        print("Downloading meta data...")
        url = "https://www.electromaps.com/mapi/v2/locations?latNE={}&lngNE={}&latSW={}&lngSW={}" \
            "&realtime=false&connectors=&types=ON_STREET,PARKING,AIRPORT,CAMPING,HOTEL,RESTAURANT,SHOP,WORKSHOP,FUEL_STATION,CAR_DEALER,MALL,TAXI" \
            "&power=3&app=false&rfid=false&favorites=false&skipAuthTokenValidation=true".format(
                YMax, XMax, YMin, XMin
            )
        super().__init__(url)
        result = {x: [] for x in self.Json + ["id"]}
        resultDetial = {x: [] for x in self.Detial + self.DetialAddress + ["id"]}

        j = self.rget().json()
        bar = tqdm(total=len(j)+1, desc="Downloading...", unit="point")
        futures = []
        futuresToID = {} # Store futures to id mapping for debugging
        detialLock = threading.Lock()
        excutor = ThreadPoolExecutor(max_workers=os.cpu_count())
        for data in j:
            id = data["id"]
            # Use multi-thread to get detial
            future = excutor.submit(self.getDetial, id, resultDetial, (detialLock, bar))
            futures.append(future)
            futuresToID[future] = id
            # Get basic info
            result["id"].append(id)
            for i in self.Json:
                result[i].append(data.get(i, None))
        for future in as_completed(futures):
            id = futuresToID[future]
            try:
                future.result()
            except Exception as e:
                tqdm.write("Error in id {}: {}".format(id, e))
        
        bar.set_description("Saving...")
        result = pd.DataFrame(result).sort_values("id").set_index("id")
        resultDetial = pd.DataFrame(resultDetial).set_index("id")   
        result = result.join(resultDetial)

        if countryCode != []:
            result = result[result["country_code"].isin(countryCode)]
        result.to_csv(os.path.join(savePath, "{}.csv".format(name)))

        resultGeometry = [Point(lon, lat) for lon, lat in zip(result["longitude"], result["latitude"])]
        gpd.GeoDataFrame(result, geometry=resultGeometry, crs="EPSG:4326").to_file(
            os.path.join(savePath, "{}.geojson".format(name)),
            driver="GeoJSON", encoding="utf-8"
        )

        with open(os.path.join(savePath, "{}.json".format(name)), 'w', encoding="utf-8") as f:
            json.dump(j, f, ensure_ascii=False, indent=4)
        bar.update(1)
        bar.close()

        return

    def getDetial(self, id: int, result: dict, multiProcess: None | tuple[threading.Lock, tqdm] = None) -> None:
        # Avoid http 500
        time.sleep(random.uniform(0.1, 0.3))
        url = "https://www.electromaps.com/mapi/v2/locations/{}".format(id)
        super().__init__(url)
        def addResult(result: dict, id: int, j: Any) -> None:
            result["id"].append(id)
            for i in self.Detial:
                result[i].append(j.get(i, None))
            for i in self.DetialAddress:
                result[i].append(j.get("address", None).get(i, None))

            return

        j = self.rget().json()
        if multiProcess is not None:
            lock, bar = multiProcess
            with lock:
                addResult(result, id, j)
                bar.update(1)
        else:
            addResult(result, id, j)

        return
        
if __name__ == "__main__":
    a =electromaps()
    a.getDataByCoor(130.9213000000001, 38.615000000000066, 124.60970000000009, 33.163400000000024, "Electromaps\\Data", "KOR", ["KR"])