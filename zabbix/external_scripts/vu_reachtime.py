#!/usr/lib/zabbix/externalscripts/env/bin/python

import argparse
import requests
import time
from urllib.parse import urlparse

def reach_time(url):
    start_time = time.time()
    try:
        response = requests.head(url)
    except Exception as e:
        pass

    end_time = time.time()
    reach_time = end_time - start_time
    # display(f" url: {url}\n Reach time: {reach_time}")

    reach_time = round(reach_time, 5)
    return reach_time

def validate_and_format_url(url_or_domain):
    """Validates and formats a URL or domain name."""
    parsed = urlparse(url_or_domain)
    if not parsed.scheme:  # No scheme, assume it's a domain
        url_or_domain = "http://" + url_or_domain

    # Re-parse after adding the scheme (if needed)
    parsed = urlparse(url_or_domain)

    # Additional validation checks:
    if not all([parsed.scheme, parsed.netloc]):
        raise argparse.ArgumentTypeError("Invalid URL or domain name format")

    return parsed.geturl()

def main():
    parser = argparse.ArgumentParser(description="Validate and format a URL or domain name.")
    parser.add_argument("url_or_domain", type=validate_and_format_url, help="URL or domain name to validate and format.")

    args = parser.parse_args()
    print(reach_time(args.url_or_domain))

if __name__ == "__main__":
    main()
