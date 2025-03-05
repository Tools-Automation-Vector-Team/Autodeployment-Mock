#!/usr/lib/zabbix/externalscripts/env/bin/python

import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from requests.exceptions import Timeout, ConnectionError
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_status_code(url, session, timeout=12):
    try:
        response = session.get(url, timeout=timeout)
        status_code = response.status_code
    except requests.exceptions.SSLError:
        response = session.get(url, timeout=timeout, verify=False)
        status_code = response.status_code
    except Timeout:
        status_code = 408
    except ConnectionError:
        status_code = 503
    except Exception:
        status_code = 500
    return int(status_code)

class BLK:

    def __init__(self, base_url):
        self.base_url = base_url

    def get_page_urls(self, base_url, session):
        try:
            response = session.get(base_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            base_domain = urlparse(base_url).netloc
            return list(set([
                urljoin(base_url, tag['href'])
                for tag in soup.find_all('a', href=True)
                if urlparse(urljoin(base_url, tag['href'])).netloc == base_domain
            ]))
        except requests.exceptions.SSLError:
            response = session.get(base_url, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            base_domain = urlparse(base_url).netloc
            return list(set([
                urljoin(base_url, tag['href'])
                for tag in soup.find_all('a', href=True)
                if urlparse(urljoin(base_url, tag['href'])).netloc == base_domain
            ]))
        except Exception as e:
            print(e)
            return []

    def check_links(self, urls, session):
        broken_links = []
        with ThreadPoolExecutor() as executor:
            future_to_url = {executor.submit(get_status_code, url, session): url for url in urls}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    if future.result() != 200:
                        broken_links.append(url)
                except Exception as exc:
                    print(f"URL {url} generated an exception: {exc}")
        return broken_links

    def analyze(self):
        with requests.Session() as session:
            links = self.get_page_urls(self.base_url, session) + [self.base_url]
            broken_links = self.check_links(links, session)
            total_links = len(links)
            broken_links_count = len(broken_links)
            return {
                "Total_links": total_links,
                "Broken_links_count": broken_links_count,
                "Broken_Links": broken_links
            }

def main(url):
    url = f'https://{url}'
    blk = BLK(url)
    result = blk.analyze()
    # Convert the result dictionary to JSON format
    json_result = json.dumps(result, indent=4)
    print(json_result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check for broken links on a website.")
    parser.add_argument('url', type=str, help='The URL of the website to check.')
    args = parser.parse_args()
    main(args.url)
