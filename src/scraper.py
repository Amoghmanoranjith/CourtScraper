import requests
from bs4 import BeautifulSoup
import json
import re


class Scraper:
    def __init__(self):
        # url of bypassed api
        self.url = "https://delhihighcourt.nic.in/app/get-case-type-status"
        # params to mimic web page request format
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
        }
        # mimic an AJAX request
        self.headers = {"X-Requested-With": "XMLHttpRequest"}

    # get the pdf links from webpage like https://delhihighcourt.nic.in/app/case-type-status-details
    def getPDFLinks(self, url):
        pdfLinks = []
        response = requests.get(url, headers=self.headers)
        try:
            data = response.json()["data"]
            for item in data:
                linkSoup = BeautifulSoup(item["case_no_order_link"], "html.parser")
                a_tag = linkSoup.find("a")
                if a_tag and "href" in a_tag.attrs:
                    pdfLinks.append(a_tag["href"])
            return pdfLinks
        except ValueError:
            print("Failed to parse JSON.")
            return []

    # takes input of case_type, case_number, and case_year and returns parsed response
    def scrape(self, **kwargs):
        self.params.update(
            {
                "case_type": kwargs.get("case_type"),
                "case_number": kwargs.get("case_number"),
                "case_year": kwargs.get("case_year"),
            }
        )
        print(
            f"Searching for Case: {kwargs['case_type']} {kwargs['case_number']}/{kwargs['case_year']}"
        )
        response = requests.get(self.url, headers=self.headers, params=self.params)
        # handling response statuses from court api
        if response.status_code != 200:
            print("Request failed.", response.status_code)
            return {
                "status": response.status_code,
                "error": "site might be down or unreachable",
            }, ""
        # if response is empty means user gave invalid parameters
        try:
            data = response.json()["data"][0]
        except (ValueError, IndexError, KeyError):
            print("")
            return {"status": 404, "error": "records not found"}, ""
        # parsing the pet and res names
        petitioner = data["pet"].split("<br>")[0]
        respondent = data["res"]
        petitioner = petitioner.replace("&amp;", "&")
        respondent = respondent.replace("&amp;", "&")
        cleaned_orderdate = data["orderdate"]
        # parsing the dates part
        next_date_match = re.search(r"NEXT DATE:\s*([^\r\n<]+)", cleaned_orderdate)
        last_date_match = re.search(r"Last Date:\s*([^\r\n<]+)", cleaned_orderdate)
        next_date = next_date_match.group(1).strip() if next_date_match else None
        last_date = last_date_match.group(1).strip() if last_date_match else None
        # extracting the link for the pdfs
        pdf_soup = BeautifulSoup(data["ctype"], "html.parser")
        pdf_link = ""
        links = pdf_soup.find_all("a")
        if len(links) >= 2:
            pdf_link = links[1]["href"]
        # get the pdf links from that page   
        pdfLinks = self.getPDFLinks(pdf_link)
        # return 3 most recent files
        pdfLinks = pdfLinks[:3]
        return {
            "case_type": kwargs.get("case_type"),
            "case_number": kwargs.get("case_number"),
            "case_year": kwargs.get("case_year"),
            "petitioner": petitioner,
            "respondent": respondent,
            "next_date": next_date,
            "last_date": last_date,
            "pdf_links": pdfLinks,
            "status": response.status_code,
        }, data
