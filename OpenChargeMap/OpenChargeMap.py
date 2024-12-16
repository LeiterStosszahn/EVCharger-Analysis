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
        url = "https://api.openchargemap.io/v3/poi?key={}&countrycode={}&compact=true&maxresults={}".format(self.__key, country, self.maxResult)
        super().__init__(url)
        result = self.rget().json()
        path =os.path.join(path, country + "Charger.json")
        with open(path, 'w') as f:
            json.dump(result, f, indent=4)
        
        return 0

if __name__ == "__main__":
    #Get all charger information
    a = charger(10000)
    countries = ["IN"]
    for country in countries:
        a.getCountry(country, "Data")

    # Get all countries charger number
    b = allCountry()
    b.getAll("Data")