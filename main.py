import pathlib
import os.path
import pandas as pd
import requests
import csv
from bs4 import BeautifulSoup
from dataCollectionFunctions import FlightDataCollection
from datetime import datetime, timedelta

savePath = pathlib.Path().resolve()
csvPathAppendix = "csv-outputs/"
csvPath = os.path.join(savePath, csvPathAppendix)
d = datetime.today() - timedelta(days=60)
maxYear = d.year
months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
flightDataUrlBase = 'https://www.caa.co.uk/'

print("Hello and welcome to the Jet2 data collection programme")
year = input("Which year would you like to view data for?")

urlDataPaths = {
  "airports": f"data-and-analysis/uk-aviation-market/airports/uk-airport-data/uk-airport-data-{year}/",
  "airlines": f"data-and-analysis/uk-aviation-market/airlines/uk-airline-data/uk-airline-data-{year}/"
}
categoryDf = pd.DataFrame(list(urlDataPaths.keys()))
categoryDf = categoryDf.rename(columns={0:"Categories"})

yearCheck = True

while yearCheck:
  if year.isdecimal() != True:
    print("Please enter a valid year.")
    year = input("Which year would you like to view data for?")
  else:
    year = int(year)
    if year > maxYear or year < 2015:
      print("Please select a year within range.")
      year = input("Which year would you like to view data for?")
    else:
      yearCheck = False

print(categoryDf)

catSelect = input("Please enter the index of the category you would like to view data for:")

catSelectCheck = True

while catSelectCheck:
  if catSelect.isnumeric() != True:
    print("Please enter a numeric index value.")
    catSelect = input("Please enter the index of the category you would like to view data for:")
  else:
    catSelect = int(catSelect)
    if catSelect not in categoryDf.index:
      print("Please enter an index value from the dataframe.")
      catSelect = input("Please enter the index of the category you would like to view data for:")
    else:
      category = list(urlDataPaths.keys())[catSelect]
      catSelectCheck = False

print("Please wait whilst your data set options are retrieved...")

dataCategorySelection = urlDataPaths[category]
flightDataUrl = flightDataUrlBase+dataCategorySelection
availableMonths = FlightDataCollection.collectAvailableMonthsURLs(FlightDataCollection, months, year, flightDataUrl)
availableDataSets = FlightDataCollection.collectDataSetURLs(list(availableMonths.values())[0])

availableDatasetsDf = pd.DataFrame(list(availableDataSets.keys()))
availableDatasetsDf = availableDatasetsDf.rename(columns={0:"Available Datasets"})

print(availableDatasetsDf)

dataSetSelect = input("Please enter the index of the dataset you would like to view:")

dataSetSelectCheck = True

while dataSetSelectCheck:
  if dataSetSelect.isnumeric() != True:
    print("Please enter a numeric index value.")
    dataSetSelect = input("Please enter the index of the dataset you would like to view data for:")
  else:
    dataSetSelect = int(dataSetSelect)
    if dataSetSelect not in availableDatasetsDf.index:
      print("Please enter an index value from the dataframe.")
      catSelect = input("Please enter the index of the dataset you would like to view data for:")
    else:
      dataset = list(availableDataSets.keys())[dataSetSelect]
      dataSetSelectCheck = False

print(f"The selected data is available for the following months of {year}:")

for months in availableMonths:
  print(months)

month = input("Please select which month you would like to see the data for (type all for all months):")

monthCheck = True

while monthCheck:
  if month.lower() == "all":
    monthCheck = False
  else:
    if month.lower() not in availableMonths:
      print("Please enter a valid month from the values provided.")
      month = input("Please select which month you would like to see the data for (type all for all months):")
    else:
      monthCheck = False

FlightDataCollection.scrapeCSVData(FlightDataCollection, month.lower(), year, availableMonths, dataset, flightDataUrlBase, csvPath)
