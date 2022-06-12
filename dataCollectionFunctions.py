import pathlib
import os.path
import requests
from bs4 import BeautifulSoup
import pandas as pd

class FlightDataCollection:

    availableMonthsUrls = {}

    def collectAvailableMonthsURLs(self, months, year, flightDataUrl):
        for m in months:
            url = f'{flightDataUrl}{m}-{year}/'
            response = requests.get(url)
            if response.url == url:
                availableMonthsUrlsLoop = {
                    m:
                    url}
                    
                self.availableMonthsUrls.update(availableMonthsUrlsLoop)
        return self.availableMonthsUrls

    def collectDataSetURLs(url):
        soup = str(BeautifulSoup(requests.get(url).content, "html.parser").find_all("a"))
        linksList = soup.split("</a>")
        titleCSVDict = {}

        for l in linksList:
            if "CSV document" in l:
                linkStart = l.find('href')+7
                linkEnd = l.find('>')-1
                link = l[linkStart:linkEnd]
                titleStart = l.find('Table')
                titleEnd = l.find('CSV')-2
                title = l[titleStart+9:titleEnd]
                numCheck = title[0:1]
                if numCheck.isnumeric():
                    titleEnd = len(title)
                    title = title[2:titleEnd]
                titleCSVDictLoop = {
                    title: link}

                titleCSVDict.update(titleCSVDictLoop)

        return titleCSVDict
    
    def writeCSVFiles(csvPath, url):
        csv=pd.read_csv(url)
        csv.to_csv(csvPath, encoding='utf-8')

    def scrapeCSVData(self, month, year, availableMonths, category, dataset, flightDataUrlBase, csvPath):
        urlList = []
        if month == "all":
            for monthKey, urlValue in availableMonths.items():
                datasets = self.collectDataSetURLs(urlValue)
                if dataset in datasets:
                    datasetURL = datasets[dataset]
                    urlList.append(flightDataUrlBase+datasetURL)
                    url = flightDataUrlBase+datasetURL
                    csvFilePath = os.path.join(csvPath, f"{category}-{dataset}-{monthKey}-{year}.csv")
                    self.writeCSVFiles(csvFilePath, url)
        else:
            availableMonths = availableMonths[month]
            datasets = self.collectDataSetURLs(availableMonths)
            datasetURL = datasets[dataset]
            urlList.append(flightDataUrlBase+datasetURL)
            url = flightDataUrlBase+datasetURL
            csvPath = os.path.join(csvPath, f"{category}-{dataset}-{month}-{year}.csv")
            self.writeCSVFiles(csvPath, url)

        return urlList