from bs4 import BeautifulSoup
from tqdm import tqdm
import ssl
from datetime import datetime
import pandas as pd
import requests


class AbstractScraper:
    def __init__(self):
        pass

    def start_url(self, query):
        raise NotImplementedError()

    def scrape_listing_urls(self, soup):
        raise NotImplementedError()

    def fetch_next_page(soup, page_num, query):
        raise NotImplementedError()

    def parse_listing_url(self, url):
        raise NotImplementedError()

    def scrape(self, query):
        print(f"Scraping {query}")
        url = self.start_url(query)
        print(f"URL is {url}")
        listing_urls = []
        page_num = 1
        pbar = tqdm(desc=url[:50])
        while True:
            print()
            res = requests.get(
                url,
                verify=ssl.CERT_NONE,
            )
            soup = BeautifulSoup(res.text)
            new_urls = self.scrape_listing_urls(soup)
            pbar.update(len(new_urls))
            listing_urls.extend(new_urls)
            page_num += 1
            url = self.fetch_next_page(soup, page_num, query)
            if url is None:
                pbar.close()
                break
            pbar.desc = url[:60]

        print("Parsing listing URLs")
        parsed = []
        urls = list(set(listing_urls))
        pbar = tqdm(total=len(urls))
        for u in urls:
            pbar.desc = u[:60]
            try:
                parsed.append(self.parse_listing_url(u))
            except Exception as e:
                print(e)
            pbar.update(1)
        pbar.close()
        self.df = pd.DataFrame(parsed)
        return self.df
