import requests
from bs4 import BeautifulSoup
import json
import re
class Scraper:
    """
    Scraper for retrieving legal case status and associated documents from the Delhi High Court website.
    """
    def __init__(self):
        """
        Initializes the Scraper object with predefined API endpoint and headers.
        """
        self.url = "https://delhihighcourt.nic.in/app/get-case-type-status"
        self.params = {}
        self.headers = {"X-Requested-With": "XMLHttpRequest"}

    def getPDFLinks(self, url):
        """
        Fetches PDF links from a given Delhi High Court secondary page.

        Args:
            url (str): The URL of the secondary details page containing order PDF links.

        Returns:
            list[str]: A list of extracted PDF URLs. Returns partial results even if full parsing fails.

        Notes:
            This method attempts to extract anchor tags embedded in a JSON response
            and parse their `href` attributes using BeautifulSoup.
        """
        pdfLinks = []
        response = requests.get(url, headers=self.headers)
        try:
            data = response.json()["data"]
            print(data, flush=True)
            for item in data:
                linkSoup = BeautifulSoup(item["case_no_order_link"], "html.parser")
                a_tag = linkSoup.find("a")
                if a_tag and "href" in a_tag.attrs:
                    pdfLinks.append(a_tag["href"])
        except ValueError:
            print("Failed to parse JSON.")
        return pdfLinks

    def scrape(self, **kwargs):
        """
        Scrapes case information from the Delhi High Court website based on case details.

        Args:
            **kwargs:
                case_type (str): Type of the case (e.g., 'CIVIL', 'CRL').
                case_number (str): Case number.
                case_year (str): Year of filing.

        Returns:
            tuple:
                dict: A dictionary containing:
                    - case_type (str)
                    - case_number (str)
                    - case_year (str)
                    - petitioner (str)
                    - respondent (str)
                    - next_date (str or None)
                    - last_date (str or None)
                    - pdf_links (list of str): Up to 3 most recent PDFs
                    - status (int): HTTP status code
                str: Raw JSON response object from the court API (or empty string on error)

        Raises:
            None explicitly, but internal HTTP and JSON decoding errors are handled gracefully.

        Notes:
            - If the court site is down or returns an unexpected format, the method returns an error response.
            - If no case is found, status code `404` is returned with an appropriate message.
        """
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

        if response.status_code != 200:
            print("Request failed.", response.status_code)
            return {
                "status": response.status_code,
                "error": "site might be down or unreachable",
            }, ""

        try:
            data = response.json()["data"][0]
        except (ValueError, IndexError, KeyError):
            return {"status": 404, "error": "records not found"}, ""

        petitioner = data["pet"].split("<br>")[0].replace("&amp;", "&")
        respondent = data["res"].replace("&amp;", "&")

        cleaned_orderdate = data["orderdate"]
        next_date_match = re.search(r"NEXT DATE:\s*([^\r\n<]+)", cleaned_orderdate)
        last_date_match = re.search(r"Last Date:\s*([^\r\n<]+)", cleaned_orderdate)
        next_date = next_date_match.group(1).strip() if next_date_match else None
        last_date = last_date_match.group(1).strip() if last_date_match else None

        pdf_soup = BeautifulSoup(data["ctype"], "html.parser")
        pdf_link = ""
        links = pdf_soup.find_all("a")
        if len(links) >= 2:
            pdf_link = links[1]["href"]

        pdfLinks = self.getPDFLinks(pdf_link)
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
