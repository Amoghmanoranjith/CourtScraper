import requests
import json
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self, case_type, case_number, case_year):
        self.url = "https://delhihighcourt.nic.in/app/get-case-type-status"
        self.case_type = case_type
        self.params = {
        "draw": "2",
        "columns[0][data]": "DT_RowIndex",
        "columns[0][name]": "DT_RowIndex",
        "columns[0][searchable]": "true",
        "columns[0][orderable]": "false",
        "columns[0][search][value]": "",
        "columns[0][search][regex]": "false",
        "columns[1][data]": "ctype",
        "columns[1][name]": "ctype",
        "columns[1][searchable]": "true",
        "columns[1][orderable]": "true",
        "columns[1][search][value]": "",
        "columns[1][search][regex]": "false",
        "columns[2][data]": "pet",
        "columns[2][name]": "pet",
        "columns[2][searchable]": "true",
        "columns[2][orderable]": "true",
        "columns[2][search][value]": "",
        "columns[2][search][regex]": "false",
        "columns[3][data]": "orderdate",
        "columns[3][name]": "orderdate",
        "columns[3][searchable]": "true",
        "columns[3][orderable]": "true",
        "columns[3][search][value]": "",
        "columns[3][search][regex]": "false",
        "order[0][column]": "0",
        "order[0][dir]": "asc",
        "order[0][name]": "DT_RowIndex",
        "start": "0",
        "length": "50",
        "search[value]": "",
        "search[regex]": "false",
        "case_type": "W.P.(C)", # get this
        "case_number": "286", # get this
        "case_year": "2023" # get this
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest"
        }
    # get the links for downloadable pdfs
    # input is url extracted from main website
    def getPDFLinks(self, url):
        pdfLinks = []
        response = requests.get(url, params=self.params, headers=self.headers)
        try:
            data = response.json()
            data = data['data']
            for item in data:
                linkSoup = BeautifulSoup(item['case_no_order_link'], 'html.parser')
                pdfLinks.append(linkSoup.find('a')['href'])
            return pdfLinks
        except ValueError:
            print("Failed to parse JSON.")
            
    def scrape(self):
        """
        parties names 
        filing and next hearing dates
        pdf links ✅
        """
        response = requests.get(self.url, headers=self.headers, params=self.params)
        print("Status code:", response.status_code)
        data = response.json()['data'][0]
        petitioner = data['pet'].split("<br>")[0]
        respondent = data['res']
        print(petitioner)
        print(respondent)
        pdf_soup = BeautifulSoup(data['ctype'], 'html.parser')
        pdf_link = pdf_soup.find_all('a')[1]['href']
        print(pdf_link)
        pdfLinks = self.getPDFLinks(pdf_link)
        print(pdfLinks)

# print("Response JSON:\n", json.dumps(response.json(), indent=4))







