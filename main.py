from cases import cases
from scraper import Scraper

scraper = Scraper()
for case in cases:
    scraper.scrape(**case)