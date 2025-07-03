# API: https://openchargemap.org/site/develop/api#/operations/get-poi

import json, os
import pandas as pd
from bs4 import BeautifulSoup as bs
from bs4 import Tag

from _toolClass.crawler import crawler
from _toolClass.apiKey import Key

#Get list of all countries
class allCountry(crawler):
    def __init__(self):
        pass

    def getAll(self, path: str = "") -> None:
        super().__init__("https://openchargemap.org/site/country")
        data = pd.DataFrame({"ISO":[], "Country":[], "Station Number":[], "Location Number":[]})
        r = self.rget()
        r.encoding = "utf-8"
        soup = bs(r.text, "html.parser")
        div = soup.find_all("div", {"class": "well well-sm"})
        del(div[0]) # Del additional content
        num = 0
        for i in div:
            if not isinstance(i, Tag):
                continue
            h3 = i.find_all("h3")
            for j in h3:
                if not isinstance(j, Tag):
                    continue
                iso = j.find("a")
                if iso and isinstance(iso, Tag) and iso.has_attr('id'):
                    data.loc[num, "ISO"] = iso["id"]
                    data.loc[num, "Country"] = j.text
            ul = i.find_all("ul")
            for j in ul:
                string = j.text.strip().split(' ')
                data.loc[num, "Station Number"] = string[0]
                data.loc[num, "Location Number"] = string[4]
            num += 1
        data.to_csv(os.path.join(path, "CountryList.csv"), encoding="utf-8")

        return

class charger(crawler):
    __key = Key #API Key
    
    def __init__(self, maxResult: int) -> None:
        self.maxResult = maxResult
        self.JtC = jsonToCsv()
    
    def getCountry(self, country: str, path: str = ""):
        print(country)
        url = "https://api.openchargemap.io/v3/poi?key={}&countrycode={}&compact=true&maxresults={}".format(self.__key, country, self.maxResult)
        super().__init__(url)
        result = self.rget().json()
        with open(os.path.join(path, country + "Charger.json"), 'w') as f:
            json.dump(result, f, indent=4)

        #Save csv
        self.JtC.path = path
        self.JtC.run(result, country)               
        
        return

class jsonToCsv(crawler):
    head = ["StatusType", "IsRecentlyVerified", "UUID", "ParentChargePointID", "UsageTypeID", "UsageType", "UsageCost"]
    address = ["Title", "AddressLine1", "AddressLine2", "Town", "StateOrProvince", "Postcode", "Latitude", "Longitude"]
    connections = ["ID", "ConnectionTypeID", "ConnectionType", "Reference", "StatusTypeID_connection", "StatusType_connection",
                   "LevelID", "Level", "Amps", "Voltage", "PowerKW", "CurrentTypeID", "CurrentType", "Quantity"]
    other = ["NumberOfPoints", "DatePlanned", "DateLastConfirmed", "StatusTypeID", "DateLastStatusUpdate",
             "DataQualityLevel", "DateCreated"]
    all = head + address + connections + other

    def __init__(self, path: str = "") -> None:
        self.path = path

    def convert(self, country: str) -> None:
        with open(os.path.join(self.path, country + "Charger.json"), 'r', encoding="utf-8") as f:
            data = json.load(f)
        self.run(data, country)

        return
    
    def run(self, result, country: str) -> None:
        contents = {key: [] for key in self.all}
        num = 0
        count = 1
        length = len(result)
        for i in range(length):
            # Print stature every 100 times
            if not count % 1000:
                print("{}/{}".format(count, length))
            count += 1
            chargerPlace = result[i]
            chargerPoints = chargerPlace["Connections"]
            if len(chargerPoints) == 0:
                for content in self.head + self.other:
                    contents[content].append(chargerPlace[content])
                for add in self.address:
                    contents[add].append(chargerPlace["AddressInfo"][add])
                for connection in self.connections:
                    contents[connection].append(None)
                num += 1
            else:
                # If there are multiple connections, save each connection
                for j in range(len(chargerPoints)):
                    for content in self.head + self.other:
                        contents[content].append(chargerPlace[content])
                    for add in self.address:
                        contents[add].append(chargerPlace["AddressInfo"][add])
                    for connection in self.connections:
                        if connection in ["StatusTypeID_connection", "StatusType_connection"]:
                            contents[connection].append(chargerPoints[j][connection.replace("_connection", "")])
                        else:
                            contents[connection].append(chargerPoints[j][connection])
                    num += 1

        pd.DataFrame(contents).to_csv(os.path.join(self.path, country + "Charger.csv"), encoding="utf-8", index=False)                
        return

if __name__ == "__main__":
    # # Get all countries charger number
    # b = allCountry()
    # b.getAll("Data2025")

    countries = pd.read_csv("Data2025\\CountryList.csv", dtype=str)
    countries.fillna("NA", inplace=True) #One country's name is NA
    countries = countries["ISO"].to_list()
    # countries = countries[113:] #DE开始,跳过95US
    # #Get all charger information
    # a = charger(1000000)
    # countries = ["NA"]
    # for country in countries:
    #     a.getCountry(country, "Data2025")

    # c = jsonToCsv("Data2025")
    # for i in countries:
    #     print(i)
    #     c.convert(i)

    # Save to gpkg
    import geopandas as gpd
    from shapely.geometry import Point
    for i in countries:
        df = pd.read_csv(os.path.join("Data2025", i + "Charger.csv"), encoding="utf-8")
        df["country"] = i
        geometry = [Point(xy) for xy in zip(df["Longitude"], df["Latitude"])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        gdf.to_file(
            r"C:\\0_PolyU\\tmp\\Charger.gpkg",
            layer= i + "Charger",
            driver="GPKG"
        )