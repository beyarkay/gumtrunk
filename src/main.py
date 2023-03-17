from bs4 import BeautifulSoup
import os
import parsedatetime as pdt
from datetime import datetime
import requests
import sys
import ssl
import pandas as pd
import warnings
import AbstractScraper as S

warnings.filterwarnings("ignore")


class GumtreeScraper(S.AbstractScraper):
    def start_url(self, query):
        """Given a search query, return the starting URL."""
        return f"https://www.gumtree.co.za/s-all-the-ads/v1b0p1?q={query}"

    def scrape_listing_urls(self, soup):
        """Given the soup of a page of adverts/items, return the URLs of the
        items to scrape."""
        return [
            "https://www.gumtree.co.za" + l.select_one("a.related-ad-title").get("href")
            for l in soup.select(".related-ad-content")
        ]

    def fetch_next_page(self, soup, page_num, query):
        """Given the soup of a page of items/adverts, return the URL for the
        next page, or return None if there is no next page."""
        if len(soup.select(".icon-pagination-right")) == 0:
            return None
        page_str = "" if page_num == 1 else f"page-{page_num}/"
        return f"https://www.gumtree.co.za/s-all-the-ads/{page_str}v1b0p{page_num}?q={query}"

    def parse_listing_url(self, url):
        res = requests.get(url, verify=ssl.CERT_NONE)
        soup = BeautifulSoup(res.text)
        locations = [l.text.strip() for l in soup.select(".location a")]
        fmt_price = lambda p: p.replace(",", "").replace("R", "")
        cal = pdt.Calendar()
        now = datetime.now()
        listing_date = soup.select_one(".vip-stats .creation-date").text.strip()
        return {
            "title": soup.select_one("h1").text,
            "url": url,
            "price": fmt_price(soup.select_one(".ad-price").text.strip()),
            "location1": locations[0],
            "location2": locations[1],
            "listing_date": cal.parseDT(listing_date, now)[0],
            "raw_listing_date": listing_date,
            "downloaded_at": now,
            "description": soup.select_one(
                ".description-website-container .description-content"
            ).text.strip(),
        }


def main():
    if len(sys.argv) != 2:
        print("Usage: `python3 src/main.py <QUERY>`")
        sys.exit(1)

    gumtree = GumtreeScraper()
    query = " ".join(sys.argv[1:])
    # Get the Dataframe of the scraped items
    df = gumtree.scrape(query)
    # Create the path where we're saving the items
    path = f"data/{query.replace(' ', '-')}.csv"
    # If the path already exists, then read in the CSV that exists there
    if os.path.exists(path):
        old_df = pd.read_csv(path)
    else:
        old_df = pd.DataFrame()

    # Concat the two dataframes into one
    df = pd.concat((old_df, df))
    # And write the df back to disk
    df.to_csv(path, index=False)
    print(f"Data saved as a CSV under {path}.")


if __name__ == "__main__":
    main()
