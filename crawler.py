##Assignment 4 question 4
#crawler.py
#This program is a crawler that goes to the url it is isntructed to crawl and then stops once it reaches the destination.

import urllib.request
from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib.parse import urljoin, urlparse

# Setting up MongoDB connection and database collection
client = MongoClient('localhost', 27017)
db = client['cs_crawler']
pages_collection = db['pages']

# Function to store the HTML of a webpage in MongoDB
def store_page(url, html):
    pages_collection.insert_one({"url": url, "html": html})
    print(f"Stored HTML for {url} in MongoDB.")

# Function to check if the HTML contains the target pag
def target_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    heading = soup.find(lambda tag: tag.name == "h1" and "Permanent Faculty" in tag.text)
    if heading:
        print(f"Target page found with heading 'Permanent Faculty'")
    return heading is not None

# Function to retrieve HTML content from a given URL
def retrieve_html(url):
    try:
        with urllib.request.urlopen(url) as response:
            content_type = response.getheader('Content-Type')
            if content_type and content_type.startswith('text/html'):
                html = response.read()
                print(f"Retrieved {url} successfully. Length of HTML: {len(html)}")
                return html
            else:
                print(f"Unexpected Content-Type ({content_type}) for URL: {url}")
    except Exception as e:
        print(f"Error retrieving {url}: {e}")
    return None


# Function to parse the HTML and extract all valid links
def parse(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        if urlparse(full_url).scheme in ['http', 'https']:
            links.add(full_url)
    return links

# Frontier class manages the queue of URLs to visit and the set of visited URLs
class Frontier:
    def __init__(self, start_url):
        self.frontier = [start_url]
        self.visited = set()
        print(f"Starting crawl at {start_url}")

    def add_url(self, url):
        if url not in self.visited:
            self.frontier.append(url)

    def next_url(self):
        while self.frontier:
            url = self.frontier.pop(0)
            if url not in self.visited:
                self.visited.add(url)
                print(f"Visiting {url}")
                return url
        return None

    def done(self):
        return not self.frontier

    def clear(self):
        self.frontier = []
        print("Frontier cleared. Stopping crawl.")

# Main crawler function that drives the crawling process
def crawler_thread(frontier):
    while not frontier.done():
        url = frontier.next_url()
        if url:
            html = retrieve_html(url)
            if html:
                store_page(url, html)
                if target_page(html):
                    print(f"Target page found at {url}")
                    frontier.clear()
                    return
                else:
                    parsed_urls = parse(html, url)
                    if not parsed_urls:
                        print(f"No links found on {url}")
                    for parsed_url in parsed_urls:
                        print(f"Found link: {parsed_url}")
                        frontier.add_url(parsed_url)
            else:
                print(f"No HTML retrieved for {url}")
                
#Crawler starts crawling the url
initial_url = "https://www.cpp.edu/sci/computer-science/"
frontier = Frontier(initial_url)
crawler_thread(frontier)
