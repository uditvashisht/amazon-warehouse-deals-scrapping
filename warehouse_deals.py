#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re

# To pretend that we are browsing using a web-browser

HEADERS = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"
}

AMAZON = 'https://www.amazon.com'

BASE_URL = 'https://www.amazon.com/s/search-alias%3Dwarehouse-deals&field-keywords='

# search words to be separated by + sign instead of whitespace

SEARCH_WORDS = "iphone"

url = BASE_URL + SEARCH_WORDS

# print(url)


def parse_result(result):
    ''' This will take care of 4 cases of results
    Case 1 When no result is available.
    Case 2 When all the results available are shown on first page only i.e. 24 results.
    Case 3 When there are more than 24 results and there are more than one page but the number of result is certain.
    Case 4 When there are over 500, 1000 or more results.
    '''

    matchRegex = re.compile(r'''(
    (1-\d+)\s
    (of)\s
    (over\s)?
    (\d,\d+|\d+)\s
    )''', re.VERBOSE)

    matchGroup = matchRegex.findall(result)

    # Case 1 simply exits the function
    # TODO Log such cases

    if "Amazon Warehouse" not in result:
        exit()

    else:
        # Case2
        if not matchGroup:
            resultCount = int(result.split()[0])
        # Case4
        elif matchGroup[0][3] == "over ":
            resultCount = 96
        # Case3
        else:
            resultCount = min([(int(matchGroup[0][4])), 96])

        return resultCount


def create_soup(url):

    req = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(req.text, 'html.parser')
    return soup


def crunch_numbers():

    soup = create_soup(url)
    result = soup.find("span", id="s-result-count").text
    resultCount = parse_result(result)
    navPages = min([resultCount // 24 + 1, 4])

    return resultCount, navPages


def get_url(text, dict):

    for key, value in dict.items():
        url = AMAZON + text.replace(key, value)

    return url


def scrap_data():

    resultCount, navPages = crunch_numbers()
    soup = create_soup(url)
    nextUrl = soup.find("span", class_="pagnLink").find("a")["href"]
    renameDicts = [{
        "sr_pg_2": "sr_pg_" + str(i),
        "page=2": "page=" + str(i)
    } for i in range(2, navPages + 1)]

    urlList = [get_url(nextUrl, dict) for dict in renameDicts]

    productName = []
    productLink = []
    productPrice = []

    for i in range(resultCount):

        if i > 23 and i <= 47:
            soup = create_soup(urlList[0])

        elif i > 47 and i <= 71:
            soup = create_soup(urlList[1])

        elif i > 71:
            soup = create_soup(urlList[2])

        id = "result_{}".format(i)

        try:
            name = soup.find("li", id=id).find("h2").text
            link = soup.find("li", id="result_{}".format(i)).find("a")["href"]
            price = soup.find(
                "li", id="result_{}".format(i)).find("span", {
                    'class': 'a-size-base'
                }).text
        except AttributeError:
            name = "Not Available"
            link = "Not Available"
            price = "Not Available"

        productName.append(name)
        productLink.append(link)
        productPrice.append(price)

    finalDict = {
        name: [link, price]
        for name, link, price in zip(productName, productLink,
                                     productPrice)
    }

    return finalDict


scrap_data()
