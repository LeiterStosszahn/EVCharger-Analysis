import requests, time, random
from tqdm import tqdm

from .apiKey import Headers

class crawler:
    __slots__ = ["url", "postData"]
    __headers = Headers

    def __init__(self, url: str, postData: dict | str = {}):
        self.url = url
        self.postData = postData

    def rpost(self) -> requests.Response:
        while True:
            try:
                r = requests.post(self.url, headers=self.__headers, data = self.postData, timeout=(3,7))
                if self.__staureCode(r, "post"):
                    time.sleep(random.randint(5,10))
                    continue
                else:
                    return r
            except:
                tqdm.write("Network error, retry...")
                time.sleep(random.randint(5,10))
                continue
    
    def rget(self, stream=False) -> requests.Response:
        while True:
            try:
                r = requests.get(self.url, headers=self.__headers, timeout=(3,7), stream=stream)
                if self.__staureCode(r, "get"):
                    time.sleep(random.randint(5,10))
                    continue
                else:
                    return r
            except:
                tqdm.write("Network error, retry...")
                time.sleep(random.randint(5,10))
                continue

    @staticmethod
    def __staureCode(r: requests.Response, rtype: str) -> bool:
        code = r.status_code
        if code != 200:
            tqdm.write("Error, stature code in {} is {}.".format(rtype, code))
            time.sleep(random.randint(5,10))
            return True
        else:
            return False