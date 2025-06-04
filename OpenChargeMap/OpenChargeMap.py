# API: https://openchargemap.org/site/develop/api#/operations/get-poi

import json, os
import pandas as pd
from bs4 import BeautifulSoup as bs

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
            h3 = i.find_all("h3")
            for j in h3:
                data.loc[num, "ISO"] = j.find("a")["id"]
                data.loc[num, "Country"] = j.text
            ul = i.find_all("ul")
            for j in ul:
                string = j.text.strip().split(' ')
                data.loc[num, "Station Number"] = string[0]
                data.loc[num, "Location Number"] = string[4]
            num += 1
        data.to_csv(os.path.join(path, "CountryList.csv"), encoding="utf-8")

        return 0

class charger(crawler):
    __key = Key #API Key
    
    def __init__(self, maxResult: int):
        self.maxResult = maxResult
    
    def getCountry(self, country: str, path: str = ""):
        print(country)
        url = "https://api.openchargemap.io/v3/poi?key={}&countrycode={}&compact=true&maxresults={}".format(self.__key, country, self.maxResult)
        super().__init__(url)
        result = self.rget().json()
        with open(os.path.join(path, country + "Charger.json"), 'w') as f:
            json.dump(result, f, indent=4)

        #Save csv
        self.head = ["StatusType", "IsRecentlyVerified", "UUID", "ParentChargePointID", "UsageTypeID", "UsageType", "UsageCost"]
        self.address = ["Title", "AddressLine1", "AddressLine2", "Town", "StateOrProvince", "Postcode", "Latitude", "Longitude"]
        self.connections = ["ID", "ConnectionTypeID", "ConnectionType", "Reference", "StatusTypeID", "StatusType",
                       "LevelID", "Level", "Amps", "Voltage", "PowerKW", "CurrentTypeID", "CurrentType", "Quantity"]
        self.other = ["NumberOfPoints", "DatePlanned", "DateLastConfirmed", "StatusTypeID", "DateLastStatusUpdate",
                 "DataQualityLevel", "DateCreated"]
        all = self.head + self.address + self.connections + self.other
        csv = pd.DataFrame(columns=all)
        num = 0
        count = 1
        length = len(result)
        for i in range(length):
            # Print stature every 100 times
            if not count % 100:
                print("{}/{}".format(count, length))
            count += 1
            contents = dict.fromkeys(all)
            chargerPlace = result[i]
            for content in self.head + self.other:
                contents[content] = chargerPlace[content]
            for add in self.address:
                contents[add] = chargerPlace["AddressInfo"][add]
            chargerPoints = chargerPlace["Connections"]
            for j in range(len(chargerPoints)):
                for connection in self.connections:
                    contents[connection] = chargerPoints[j][connection]
                    csv.loc[num] = contents
                num += 1
        csv.to_csv(os.path.join(path, country + "Charger.csv"), encoding="utf-8")                
        
        return 0
    
    # def getDetial(self, all, result, i):
    #     contents = dict.fromkeys(all)
    #     chargerPlace = result[i]
    #     for content in self.head + self.other:
    #         contents[content] = chargerPlace[content]
    #     for add in self.address:
    #         contents[add] = chargerPlace["AddressInfo"][add]
    #     chargerPoints = chargerPlace["Connections"]
    #     for j in range(len(chargerPoints)):
    #         for connection in self.connections:
    #             contents[connection] = chargerPoints[j][connection]
    #             csv.loc[num] = contents
    #         num += 1

if __name__ == "__main__":
    # # Get all countries charger number
    # b = allCountry()
    # b.getAll("Data2025")

    countries = pd.read_csv("Data2025\\CountryList.csv", dtype=str)
    countries = countries["ISO"].to_list()
    countries = countries[113:] #DE开始,跳过95US
    #Get all charger information
    a = charger(1000000)
    countries = ["NA"]
    for country in countries:
        a.getCountry(country, "Data2025")