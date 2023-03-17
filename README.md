Gumtrunk
--------

A simple web scraping utility.

# Installation

Downloading the utility:

```
git clone https://github.com/beyarkay/gumtrunk.git
cd gumtrunk
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
### An aside:

If you're installing `gumtrunk` on a raspberry pi, then you might (as I did)
get an error like this:

```
IMPORTANT: PLEASE READ THIS FOR ADVICE ON HOW TO SOLVE THIS ISSUE!

Importing the numpy C-extensions failed. This error can happen for
many reasons, often due to issues with your setup or how NumPy was
installed.

...

libf77blas.so.3: cannot open shared object file: No such file or directory
```

In this case, following the advice on [the numpy
website](https://numpy.org/devdocs/user/troubleshooting-importerror.html)
helped me a lot:

```
sudo apt-get install libatlas-base-dev
````

# Using the utility


To search `gumtree` for the phrase "hobie":

```
python3 src/main.py hobie
```

The results will be saved under `data/hobie.csv`

If you have a multi-word query:

```
python3 src/main.py hobie cats in south africa
```

Then the utility will search gumtree for "hobie cats in south africa", and save
the results under "data/hobie-cats-in-south-africa.csv". Making multiple
searches with one command is not supported as of yet.

# Expanding the utility

The utility defines an `AbstractScraper` class in `src/AbstractScraper.py`.

The basic assumption of `gumtrunk` is that most scrapers have three jobs:

1. Accept a search query
2. Traverse a series of search pages that list simplified items which a website
   thinks are related to your query.
3. Visit the dedicated URL for each of those search results, and download some
   data from the detailed URL.

So `gumtrunk` provides an easy way for you to specify the behaviour in each of
those three cases, and then takes care of glueing everything together.

Inheriting from `AbstractScraper` requires the implementation of four methods:

- `start_url(self, query)`: This should return the first URL that the scraper
  should download data from. Often this is different from the paginated URL.
- `scrape_listing_urls(self, soup)`: This should take in a `BeautifulSoup`
  soup, and return a list of URLs that describe the actual listings.
- `fetch_next_page(soup, page_num, query)`: This should take in a
  `BeautifulSoup` soup, a page number, a query, and return the correct URL for
  that page. It should return `None` if there are no more pages left to search.
- `parse_listing_url(self, url)`: This should take in a URL and return a
  dictionary of items, which will be stored as a CSV file by `gumtrunk`.

An example implementation is provided in `src/main.py` as the `GumtreeScraper`
class.
