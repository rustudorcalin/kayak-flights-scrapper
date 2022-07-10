import logging
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from tabulate import tabulate
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


logging.getLogger('WDM').setLevel(logging.FATAL)


def scrape(origin, destination, startdate, enddate):
    url = f"https://www.ro.kayak.com/flights/{origin}-{destination}/{startdate}/{enddate}?sort=bestflight_a&fs=stops=0"

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'lxml')

    # wait until page loads completely
    WebDriverWait(driver, 40).until(
        ec.presence_of_element_located((By.CLASS_NAME, "mainInfo"))
    )

    deptimes = soup.find_all('span', attrs={'class': 'depart-time base-time'})
    arrtimes = soup.find_all('span', attrs={'class': 'arrival-time base-time'})

    deptime = []
    for div in deptimes:
        deptime.append(div.getText())
    arrtime = []
    for div in arrtimes:
        arrtime.append(div.getText())

    deptime = np.asarray(deptime)
    deptime = deptime.reshape(int(len(deptime) / 2), 2)

    arrtime = np.asarray(arrtime)
    arrtime = arrtime.reshape(int(len(arrtime) / 2), 2)

    price_list = soup.select('div.Common-Booking-MultiBookProvider.Theme-featured-large.multi-row')
    price = []
    for div in price_list:
        val = div.getText().split('\n')[4]
        price.append(str(val))

    df = pd.DataFrame({"Origin": origin,
                       "Destination": destination,
                       "Startdate": startdate,
                       "Enddate": enddate,
                       "Price": price,
                       "Outbound": [m for m in deptime[:, 0]],
                       "Outbound2": [m for m in arrtime[:, 0]],
                       "Return": [m for m in deptime[:, 1]],
                       "Return2": [m for m in arrtime[:, 1]]
                       })
    driver.close()
    return df


if __name__ == '__main__':
    origin = input('Enter a valid IATA origin: ').upper()
    destination = input('Enter a valid IATA destination: ').upper()
    startdate = input('Start date (eg format YYYY-MM-DD): ')
    enddate = input('End date (eg format YYYY-MM-DD): ')

    print(f"Scraping for {origin} - {destination}, for outbound {startdate} and return {enddate}.")
    dataframe = scrape(origin=origin, destination=destination, startdate=startdate, enddate=enddate)

    print(tabulate(dataframe, headers='keys', tablefmt='psql'))
