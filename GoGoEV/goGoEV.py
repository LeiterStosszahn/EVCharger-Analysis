import sys, os, time, random
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, MultiPolygon, box
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from bs4 import Tag

sys.path.append(".") # Set path to the roots

from _toolClass.crawler import crawler

class goGoEV(crawler):
    __slots__ = ["centers"]
    __WINDOW = 0.3495
    BASIC_INFO = ["ev_stand_id", "lat", "lon"]
    ADD_INFO = ["ev_stand_id", "name", "address", "charging", "chargingNum"]

    def __init__(self):
        # Get window       
        gdf = gpd.read_file(r"ArcGISProcess//EVCharger.gdb", layer="iso2_geom")
        jpBorder = gdf.loc[gdf["iso2"] == "JP"]
        jpGeom: MultiPolygon = jpBorder.iloc[0].geometry
        minX, minY, maxX, maxY = jpGeom.bounds
        
        startX = minX + self.__WINDOW * 0.5
        startY = minY + self.__WINDOW * 0.5
        cols = int((maxX - minX) / self.__WINDOW) + 2
        rows = int((maxY - minY) / self.__WINDOW) + 2

        self.centers = []
        for i in range(rows):
            for j in range(cols):
                centerX = startX + j * self.__WINDOW
                centerY = startY + i * self.__WINDOW
                
                rect = box(
                    centerX - self.__WINDOW * 0.5,
                    centerY - self.__WINDOW * 0.5,
                    centerX + self.__WINDOW * 0.5,
                    centerY + self.__WINDOW * 0.5
                )
                
                # Whether the box in boundary
                intersection = rect.intersection(jpGeom)
                if not intersection.is_empty:
                    self.centers.append((centerX, centerY))

        return
    
    def getAll(self, savePath: str, threadNum: int) -> None:
        basicResult = []
        futures = []
        windowNum = len(self.centers)
        bar = tqdm(total=windowNum * 2 + 4, desc="Processing basic information", bar_format="{l_bar}{bar}| {n:.02f}/{total:.02f} [{elapsed}<{remaining}]")
        with ProcessPoolExecutor(max_workers=threadNum) as excutor:
            for centerCoor in self.centers:
                futures.append(excutor.submit(self.getBasic, centerCoor))
            for future in as_completed(futures):
                try:
                    basicResult += future.result()
                    bar.update(1)
                except Exception as e:
                    raise RuntimeError(e)

        bar.set_description("Saving basic information...")
        result = pd.DataFrame(basicResult, columns=self.BASIC_INFO).drop_duplicates(subset="ev_stand_id").set_index("ev_stand_id").sort_index()
        result.to_csv(os.path.join(savePath, "goGoEV_basic.csv"), encoding="utf-8")
        bar.update(1)

        additionResult = []
        futures = []
        chunk = round(windowNum / result.shape[0], 3)
        with ProcessPoolExecutor(max_workers=threadNum) as excutor:
            for id in result.index.to_list():
                futures.append(excutor.submit(self.getDetail, id))
            for future in as_completed(futures):
                try:
                    additionResult.append(future.result())
                    bar.update(chunk)
                except Exception as e:
                    raise RuntimeError(e)

        bar.set_description("Saving addition information...")
        addResult = pd.DataFrame(additionResult, columns=self.ADD_INFO).set_index("ev_stand_id")
        result = result.join(addResult)
        result.to_csv(os.path.join(savePath, "goGoEV.csv"), encoding="utf-8")
        bar.update(1)

        bar.set_description("Saving GeoJSON...")
        resultGeometry = [Point(lon, lat) for lon, lat in zip(result["lon"], result["lat"])]
        gpd.GeoDataFrame(result, geometry=resultGeometry, crs="EPSG:4326").to_file(
            os.path.join(savePath, "goGoEV.geojson"),
            driver="GeoJSON", encoding="utf-8"
        )
        bar.n = bar.total
        bar.last_print_n = bar.total
        bar.refresh()
        bar.close()

        return

    def getBasic(self, centerCoor: tuple[float, float]) -> list[list]:
        lon, lat  = centerCoor
        result = []
        url = f"https://ev.gogo.gs/api/spot/around.json?lat={lat}&lon={lon}&limit="
        super().__init__(url)
        j = self.rget().json()
        for i in j["result"]:
            result.append([i["ev_stand_id"], i["lat"], i["lon"]])
        time.sleep(random.random())
        
        return result
    
    def getDetail(self, id: int) -> list:
        chargingDetial = {"Type": [], "Power": [], "Currency": [], "other": []}
        chargingNum = 0
        url = "https://ev.gogo.gs/api/spot/info.json?ev_stand_id={}".format(id)
        super().__init__(url)
        j = self.rget().json()
        soup = bs(j["result"]["spot"]["html"], "html.parser")
        name = soup.find("a", {"class": "font-bold text-base"})
        if name is not None:
            name = name.text
        address = soup.find("p")
        if address is not None:
            address = address.text
        chargingAll = soup.find_all("div", {"class": "border bg-gray-100 mb-2"})
        for charging in chargingAll:
            if not isinstance(charging, Tag):
                continue
            cType = charging.find("p")
            if cType is not None:
                cType = cType.text.replace(' ','').split('\n')
                a = cType[0].split('x')
                chargingDetial["Type"].append(a[0] if len(a) > 0 else None)
                chargingNum += int(a[1]) if len(a) == 2 else 0
                chargingDetial["Power"].append(cType[2] if len(cType) > 2 else None)
                chargingDetial["Currency"].append(cType[4][1:] if len(cType) > 4 else None)
                cOther = charging.find("div", {"class": "flex gap-1 mt-2 flex-wrap text-sm"})
                if cOther is not None:
                    cOther = cOther.text.replace(' ','').split('\n')
                    cOther = [x for x in cOther if x != '']
                    cOther = ','.join(cOther)
                    chargingDetial["other"].append(cOther)
                else:
                    chargingDetial["other"].append(None)
        time.sleep(random.random())

        return [id, name, address, chargingDetial, chargingNum]

        
if __name__ == "__main__":
    goGoEV().getAll(r"GoGoEV\\Data", 14) # type: ignore
    